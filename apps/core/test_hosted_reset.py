import io
import sqlite3
import tempfile
import uuid
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command, CommandError
from django.test import TransactionTestCase, Client, override_settings
from django.utils import timezone

from apps.accounts.models import User
from apps.profiles.models import Profile, ResumeVersion, Department, Skill, ResearchInterest
from apps.projects.models import Project
from apps.communities.models import Community, SummaryResource, Sprint
from apps.collaboration.models import ChatMessage, Poll, PollOption, PollVote, ChatAttachment
from apps.tasks.models import Task, TaskFile, Submission, Review
from apps.core.backup import verify
from apps.core.management.commands import reset_hosted_demo as command


@override_settings(AUTHENTICATION_MODE='real', PASSWORD_RESET_ENABLED=False,
                   PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class HostedResetTests(TransactionTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.data = self.root / 'data'
        self.uploads = self.data / 'uploads'
        self.uploads.mkdir(parents=True)
        self.override = override_settings(DATA_DIR=self.data, MEDIA_ROOT=self.uploads)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.secret = self.data / 'secret-sentinel'
        self.secret.write_text('unchanged')
        self.department = Department.objects.create(name='Reset test department')
        self.skill = Skill.objects.create(name='Reset test skill')
        self.interest = ResearchInterest.objects.create(name='Reset test interest')
        self.accounts = []
        for role in ['student', 'teacher']:
            for number in range(5):
                password = f'Private-{role}-{number}!9384'
                user = User.objects.create_user(f'{role}{number}@rknec.in', password,
                                                roster_role=role, is_demo=False)
                profile = Profile.objects.create(user=user, role=role, name='Filled profile',
                    department=self.department, phone='12345', year=3, availability=10,
                    previous_research='Research', scholar_url='https://example.org',
                    teacher_approved=True, completed_at=timezone.now())
                profile.skills.add(self.skill)
                profile.interests.add(self.interest)
                self.accounts.append((user, password))
        self.project = Project.objects.create(creator=self.accounts[0][0], title='Test',
                         domain=self.interest, short_description='Test', open_positions=2)
        self.project.skills.add(self.skill)
        self.community = Community.objects.create(project=self.project, created_by=self.accounts[5][0])
        msg = ChatMessage.objects.create(community=self.community, sender=self.accounts[5][0],
                                        sender_name='Teacher', request_key=uuid.uuid4())
        ChatMessage.objects.create(community=self.community, sender=self.accounts[0][0],
                                   reply_to=msg, sender_name='Student', request_key=uuid.uuid4())
        poll = Poll.objects.create(message=msg, question='Test?')
        option = PollOption.objects.create(poll=poll, text='Yes', order=1)
        PollVote.objects.create(poll=poll, option=option, voter=self.accounts[0][0])
        ChatAttachment.objects.create(message=msg, file='chat/test.txt', filename='test.txt',
                                      kind='document', mime='text/plain', size=4, sha256='test')
        (self.uploads / 'chat').mkdir()
        (self.uploads / 'chat/test.txt').write_bytes(b'test')
        (self.uploads / 'orphan.bin').write_bytes(b'orphan')
        ResumeVersion.objects.create(profile=self.accounts[0][0].profile,
                                     file='resume.pdf', original_name='resume.pdf')
        sprint = Sprint.objects.create(community=self.community, title='Sprint', goal='Goal')
        task = Task.objects.create(community=self.community, sprint=sprint, title='Task',
                                   assignee=self.accounts[0][0], created_by=self.accounts[5][0])
        old = TaskFile.objects.create(task=task, uploader=self.accounts[0][0], file='old.pdf', size=1)
        new = TaskFile.objects.create(task=task, uploader=self.accounts[0][0], file='new.pdf', size=1, replaces=old)
        sub = Submission.objects.create(task=task, submitter=self.accounts[0][0], number=1, summary='Done')
        sub.files.add(old, new)
        Review.objects.create(submission=sub, reviewer=self.accounts[5][0], decision='approved')
        resource = SummaryResource.objects.create(community=self.community, title='V1', category='reference',
                    url='https://example.org/1', added_by=self.accounts[5][0])
        SummaryResource.objects.create(community=self.community, title='V2', category='reference',
                    url='https://example.org/2', added_by=self.accounts[5][0], replaces=resource)
        from apps.agreements.models import Agreement, AgreementEvidence, AgreementReview
        from apps.recruitment.models import Application, OfferLetter, ReviewDecision, MeetingInvitation
        from apps.mentorship.models import MentorSearch, MentorRequest
        from apps.notifications.models import Notification
        from apps.documents.models import ProjectDocument, DocumentVersion
        from apps.ip_progress.models import Completion, IPUpdate, Achievement
        from apps.communities.models import Membership, CommunityEvent
        student, teacher = self.accounts[0][0], self.accounts[5][0]
        application = Application.objects.create(project=self.project, applicant=student,
                         profile_resume=ResumeVersion.objects.first())
        OfferLetter.objects.create(application=application, issued_by=teacher,
                                    issued_at=timezone.now(), snapshot={}, pdf='letter.pdf')
        ReviewDecision.objects.create(application=application, actor=teacher, request_key=uuid.uuid4())
        MeetingInvitation.objects.create(application=application, created_by=teacher,
                         request_key=uuid.uuid4(), scheduled_at=timezone.now())
        agreement = Agreement.objects.create(project=self.project, student=student, enrolled_by=teacher)
        evidence = AgreementEvidence.objects.create(agreement=agreement, request_key=uuid.uuid4(),
                         snapshot={}, created_at=timezone.now(), pdf='agreement.pdf', signature=[[1, 2]])
        AgreementReview.objects.create(evidence=evidence, actor=teacher, request_key=uuid.uuid4())
        Membership.objects.create(community=self.community, user=student, role='student', admitted_evidence=evidence)
        CommunityEvent.objects.create(community=self.community, actor=teacher, request_key=uuid.uuid4())
        search = MentorSearch.objects.create(project=self.project)
        MentorRequest.objects.create(search=search, teacher=teacher, position=1, score=100)
        Notification.objects.create(recipient=student, event_key='test', project=self.project, application=application)
        document = ProjectDocument.objects.create(project=self.project, title='Document')
        DocumentVersion.objects.create(document=document, uploader=student, version=1, file='document.pdf', size=1)
        Completion.objects.create(community=self.community)
        IPUpdate.objects.create(community=self.community, author=teacher, task=task)
        Achievement.objects.create(community=self.community, approved_by=teacher, milestone_date=timezone.localdate())

    def run_reset(self, **kwargs):
        options = dict(confirm=command.CONFIRMATION, writers_stopped=True,
                       backup_dir=str(self.root / 'backup'), stdout=io.StringIO())
        options.update(kwargs)
        call_command('reset_hosted_demo', **options)

    def test_ten_existing_logins_profiles_backups_and_taxonomy(self):
        before = list(User.objects.order_by('pk').values())
        with command.connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM django_migrations')
            migrations = cursor.fetchone()
        self.run_reset()
        self.assertEqual(before, list(User.objects.order_by('pk').values()))
        for model in command.deletion_order():
            self.assertEqual(model.objects.count(), 0, model._meta.label)
        for user, password in self.accounts:
            profile = Profile.objects.get(user=user)
            self.assertIsNone(profile.completed_at)
            self.assertEqual(profile.role, user.roster_role)
            self.assertEqual(profile.name, '')
            self.assertFalse(profile.teacher_approved)
            self.assertIsNone(profile.department_id)
            self.assertFalse(profile.skills.exists())
            self.assertFalse(profile.interests.exists())
            client = Client()
            response = client.post('/accounts/login/', {'email': user.email, 'password': password})
            self.assertEqual(response.status_code, 302)
            self.assertEqual(int(client.session['_auth_user_id']), user.pk)
            self.assertRedirects(client.get('/dashboard/'), '/profile/', fetch_redirect_response=False)
        self.assertTrue(Department.objects.filter(pk=self.department.pk).exists())
        self.assertTrue(Skill.objects.filter(pk=self.skill.pk).exists())
        self.assertTrue(ResearchInterest.objects.filter(pk=self.interest.pk).exists())
        self.assertEqual(self.secret.read_text(), 'unchanged')
        self.assertEqual(list(self.uploads.iterdir()), [])
        verify(self.root / 'backup')
        self.assertEqual((self.root / 'backup/uploads/chat/test.txt').read_bytes(), b'test')
        with closing(sqlite3.connect(self.root / 'backup/db.sqlite3')) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM accounts_user').fetchone()[0], 10)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM projects_project').fetchone()[0], 1)
        with command.connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM django_migrations')
            self.assertEqual(cursor.fetchone(), migrations)

    def test_preview_and_confirmation_guards(self):
        self.run_reset(dry_run=True)
        self.run_reset(confirm=None)
        for options in [dict(confirm='yes'), dict(writers_stopped=False), dict(backup_dir=None),
                        dict(backup_dir=str(self.data / 'backup'))]:
            with self.assertRaises(CommandError):
                self.run_reset(**options)
        self.assertEqual(Project.objects.count(), 1)
        self.assertFalse((self.root / 'backup').exists())
        self.assertTrue((self.uploads / 'chat/test.txt').exists())

    def test_backup_failure_prevents_deletion(self):
        with patch.object(command, 'make_backup', side_effect=OSError('disk full')):
            with self.assertRaises(CommandError):
                self.run_reset()
        self.assertEqual(Project.objects.count(), 1)
        self.assertTrue(Profile.objects.filter(completed_at__isnull=False).exists())
        self.assertTrue((self.uploads / 'chat/test.txt').exists())

    def test_database_failure_rolls_back_all_deletion(self):
        original = command.reset_database
        def fail(order):
            original(order)
            raise RuntimeError('simulated failure')
        with patch.object(command, 'reset_database', side_effect=fail):
            with self.assertRaises(CommandError):
                self.run_reset()
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(PollVote.objects.count(), 1)
        self.assertEqual(Profile.objects.filter(completed_at__isnull=False).count(), 10)
        self.assertTrue((self.uploads / 'chat/test.txt').exists())

    def test_upload_failure_restores_directory_and_database(self):
        original = Path.mkdir
        def fail(path, *args, **kwargs):
            if path == self.uploads:
                raise OSError('simulated upload error')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'mkdir', fail):
            with self.assertRaises(CommandError):
                self.run_reset()
        self.assertEqual(Project.objects.count(), 1)
        self.assertTrue((self.uploads / 'chat/test.txt').exists())

    def test_missing_profile_created_and_repeated_reset_safe(self):
        self.accounts[9][0].profile.delete()
        self.run_reset()
        self.run_reset(backup_dir=str(self.root / 'second-backup'))
        self.assertEqual(User.objects.count(), 10)
        self.assertEqual(Profile.objects.filter(completed_at__isnull=True).count(), 10)
