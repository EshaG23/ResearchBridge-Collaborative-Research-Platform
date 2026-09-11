import io
import uuid
import tempfile
from unittest.mock import patch
from django.test import TestCase, override_settings, Client
from django.urls import reverse
from django.db import DatabaseError
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from pypdf import PdfWriter
from apps.accounts.models import User
from apps.profiles.models import Profile, Department, Skill, ResearchInterest, ResumeVersion
from apps.documents.models import DocumentVersion, ProjectDocument
from apps.documents.services import upload_document
from apps.notifications.models import Notification
from apps.notifications.services import notify, authorised_url
from apps.core.permissions import can_manage_project
from .models import Project, ConfidentialIdea

@override_settings(DEBUG=True, AUTHENTICATION_MODE='demo', PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class ResearchModulesTests(TestCase):
    def setUp(self):
        storage = tempfile.TemporaryDirectory()
        self.addCleanup(storage.cleanup)
        override = override_settings(MEDIA_ROOT=storage.name)
        override.enable()
        self.addCleanup(override.disable)
        self.student = self.user('student')
        self.teacher = self.user('teacher','teacher')
        self.other = self.user('outsider')
        self.dept = Department.objects.get(name='CSE')
        self.skill = Skill.objects.create(name='Python')
        self.domain = ResearchInterest.objects.create(name='Artificial intelligence')
        self.client.force_login(self.student)

    def user(self, name, role='student', approved=True):
        user = User.objects.create_user(name+'@rknec.in','Testing!2026',roster_role=role,is_demo=True)
        Profile.objects.create(user=user,role=role,name=name,teacher_approved=approved,completed_at=timezone.now())
        return user

    def data(self, **changes):
        return {'creation_key':str(uuid.uuid4()),'revision':1,'title':'Accessible campus navigation',
            'short_description':'Help build an accessible campus route planner.',
            'domain':self.domain.pk,'departments':[self.dept.pk],'skills':[self.skill.pk],
            'open_positions':3,'available_roles':'Developer',
            'confidential_details':'PRIVATE-SENTINEL: unpublished sensor method','action':'submit'} | changes

    def create(self, user=None, **changes):
        self.client.force_login(user or self.student)
        response = self.client.post('/projects/create/',self.data(**changes))
        self.assertEqual(response.status_code,302)
        return Project.objects.get(pk=response.url.split('/')[-2])

    def pdf(self,name='note.pdf'):
        buf=io.BytesIO()
        writer=PdfWriter()
        writer.add_blank_page(width=100,height=100)
        writer.write(buf)
        return SimpleUploadedFile(name,buf.getvalue(),content_type='application/pdf')

    def test_student_and_teacher_create_correct_states_and_roles(self):
        student_idea = self.create()
        faculty_idea = self.create(self.teacher)
        self.assertEqual(student_idea.creator,self.student)
        self.assertIsNone(student_idea.mentor)
        self.assertEqual(student_idea.status,'pending_mentor')
        self.assertEqual(faculty_idea.mentor,self.teacher)
        self.assertEqual(faculty_idea.status,'recruiting')
        self.assertEqual(student_idea.skills.get(),self.skill)
        self.assertEqual(student_idea.departments.get(),self.dept)
        self.assertEqual(ConfidentialIdea.objects.count(),2)

    def test_repeated_submission_has_one_project_and_notification(self):
        data=self.data()
        for _ in range(2):
            self.assertEqual(self.client.post('/projects/create/',data).status_code,302)
        self.assertEqual(Project.objects.count(),1)
        self.assertEqual(Notification.objects.count(),1)

    def test_unapproved_faculty_and_incomplete_profile_cannot_create(self):
        pending=self.user('pending','teacher',approved=False)
        self.client.force_login(pending)
        self.assertEqual(self.client.post('/projects/create/',self.data()).status_code,403)
        self.student.profile.completed_at=None
        self.student.profile.save()
        self.client.force_login(self.student)
        self.assertRedirects(self.client.get('/projects/create/'),'/profile/')
        self.assertFalse(Project.objects.exists())

    def test_invalid_recruitment_fields_and_forged_privileges(self):
        response=self.client.post('/projects/create/',self.data(short_description='x'*241,open_positions=0,departments=[],skills=[]))
        self.assertEqual(response.status_code,200)
        self.assertFalse(Project.objects.exists())
        project=self.create(mentor=self.teacher.pk,creator=self.other.pk,status='recruiting')
        self.assertIsNone(project.mentor)
        self.assertEqual(project.creator,self.student)
        self.assertEqual(project.status,'pending_mentor')

    def test_draft_is_private_and_can_be_published(self):
        project=self.create(self.teacher,action='draft')
        self.assertEqual(project.status,'draft')
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse('projects:detail',args=[project.pk])).status_code,404)
        self.client.force_login(self.teacher)
        self.client.post(reverse('projects:edit',args=[project.pk]),self.data(creation_key=project.creation_key,revision=1))
        project.refresh_from_db()
        self.assertEqual(project.status,'recruiting')

    def test_public_details_and_dashboard_never_leak_confidential_information(self):
        project=self.create(self.teacher)
        self.client.force_login(self.other)
        for url in ['/dashboard/',reverse('projects:detail',args=[project.pk])]:
            response=self.client.get(url)
            self.assertContains(response,project.title)
            self.assertNotContains(response,'PRIVATE-SENTINEL')
            self.assertNotContains(response,'/private/')
        for name in ['private','edit']:
            self.assertEqual(self.client.get(reverse('projects:'+name,args=[project.pk])).status_code,404)
        self.assertEqual(self.client.post(reverse('projects:edit',args=[project.pk]),self.data()).status_code,404)
        self.client.logout()
        self.assertEqual(self.client.get(reverse('projects:detail',args=[project.pk])).status_code,302)

    def test_created_ideas_and_my_projects_scoped(self):
        first=self.create(title='Student owned')
        self.create(self.teacher,title='Faculty owned')
        self.client.force_login(self.student)
        response=self.client.get('/projects/?view=created')
        self.assertContains(response,'Student owned')
        self.assertNotContains(response,'Faculty owned')
        first.mentor=self.teacher
        first.save()
        self.client.force_login(self.teacher)
        self.assertContains(self.client.get('/projects/'),'Student owned')
        self.assertNotContains(self.client.get('/projects/?view=created'),'Student owned')
        self.assertEqual(Project.objects.get(pk=first.pk).creator,self.student)

    def test_attached_mentor_only_and_access_revocation(self):
        project=self.create()
        self.assertFalse(can_manage_project(self.teacher,project))
        project.mentor=self.teacher
        project.save()
        self.client.force_login(self.teacher)
        self.assertContains(self.client.get(reverse('projects:private',args=[project.pk])),'PRIVATE-SENTINEL')
        self.teacher.profile.teacher_approved=False
        self.teacher.profile.save()
        self.assertEqual(self.client.get(reverse('projects:private',args=[project.pk])).status_code,404)
        self.assertNotContains(self.client.get('/projects/'),project.title)
        project.mentor=None
        project.save()
        self.teacher.profile.teacher_approved=True
        self.teacher.profile.save()
        self.assertEqual(self.client.get(reverse('projects:private',args=[project.pk])).status_code,404)

    def test_stale_edit_preserves_newer_changes(self):
        project=self.create()
        url=reverse('projects:edit',args=[project.pk])
        data=self.data(action='save',creation_key=project.creation_key,revision=1,title='New title')
        self.assertEqual(self.client.post(url,data).status_code,302)
        self.assertContains(self.client.post(url,data|{'title':'Stale title'}),'changed in another window')
        project.refresh_from_db()
        self.assertEqual(project.title,'New title')
        self.assertEqual(project.revision,2)

    def test_notification_retries_persistence_and_read_status(self):
        project=self.create()
        first=notify(self.student,'stable-event','Saved',project=project)
        self.assertEqual(notify(self.student,'stable-event','Saved',project=project).pk,first.pk)
        self.client.post('/accounts/logout/')
        self.client.post('/accounts/login/',{'email':self.student.email,'password':'Testing!2026'})
        self.assertContains(self.client.get('/notifications/'),'Saved')
        self.assertEqual(self.client.get('/notifications/poll/').json()['unread_count'],2)
        url=reverse('notifications:read',args=[first.pk])
        self.assertEqual(self.client.get(url).status_code,405)
        self.client.post(url)
        first.refresh_from_db()
        read_at=first.read_at
        self.client.post(url)
        first.refresh_from_db()
        self.assertEqual(first.read_at,read_at)
        self.client.post('/notifications/read-all/')
        self.assertEqual(self.client.get('/notifications/poll/').json()['unread_count'],0)
        self.assertContains(self.client.get('/notifications/?filter=unread'),'caught up')

    def test_notifications_are_recipient_scoped_with_fresh_authorised_links(self):
        project=self.create()
        note=notify(self.teacher,'request','Mentor request',project=project)
        self.assertIsNone(authorised_url(note,self.student))
        self.assertEqual(self.client.post(reverse('notifications:read',args=[note.pk])).status_code,404)
        self.assertNotContains(self.client.get('/notifications/'),'Mentor request')
        self.client.force_login(self.teacher)
        self.assertIsNone(self.client.get('/notifications/poll/').json()['items'][0]['url'])
        project.mentor=self.teacher
        project.save()
        self.assertEqual(self.client.get('/notifications/poll/').json()['items'][0]['url'],reverse('projects:detail',args=[project.pk]))
        project.mentor=None
        project.save()
        self.assertRedirects(self.client.post(reverse('notifications:read',args=[note.pk]),{'open':'1','next':'https://example.com'}),'/notifications/')

    def test_notification_and_idea_transaction_rollback(self):
        with patch('apps.projects.services.notify',side_effect=DatabaseError('database problem')):
            self.assertContains(self.client.post('/projects/create/',self.data()),'could not be saved')
        self.assertFalse(Project.objects.exists())
        self.assertFalse(ConfidentialIdea.objects.exists())
        self.assertFalse(Notification.objects.exists())

    def test_notification_and_idea_post_require_csrf(self):
        strict=Client(enforce_csrf_checks=True)
        strict.force_login(self.student)
        self.assertEqual(strict.post('/projects/create/',self.data()).status_code,403)
        self.assertEqual(strict.post('/notifications/read-all/').status_code,403)

    def test_private_upload_versions_download_and_cross_project_denial(self):
        project=self.create()
        url=reverse('documents:upload',args=[project.pk])
        self.assertEqual(self.client.post(url,{'title':'Concept note','file':self.pdf()}).status_code,302)
        version=DocumentVersion.objects.get()
        original_path=version.file.name
        url2=reverse('documents:version',args=[project.pk,version.document_id])
        self.assertEqual(self.client.post(url2,{'file':self.pdf('revision.pdf')}).status_code,302)
        self.assertEqual(DocumentVersion.objects.count(),2)
        self.assertEqual(list(version.document.versions.values_list('version',flat=True)),[2,1])
        version.refresh_from_db()
        self.assertEqual(version.file.name,original_path)
        download=reverse('documents:download',args=[project.pk,version.pk])
        response=self.client.get(download)
        self.assertEqual(response.status_code,200)
        self.assertTrue(b''.join(response.streaming_content).startswith(b'%PDF-'))
        response.close()
        self.assertIn('no-store',response['Cache-Control'])
        self.assertIn('attachment',response['Content-Disposition'])
        self.assertEqual(response['X-Content-Type-Options'],'nosniff')
        other_project=self.create(self.other)
        self.assertEqual(self.client.get(download).status_code,404)
        self.assertEqual(self.client.get(reverse('documents:download',args=[other_project.pk,version.pk])).status_code,404)
        self.assertEqual(self.client.post(reverse('documents:version',args=[other_project.pk,version.document_id]),{'file':self.pdf()}).status_code,404)
        self.assertEqual(self.client.post(url,{'title':'Hack','file':self.pdf()}).status_code,404)
        self.client.logout()
        self.assertEqual(self.client.get(download).status_code,302)
        self.assertEqual(self.client.get('/media/'+original_path).status_code,404)

    def test_upload_validation_and_storage_failure_rollback(self):
        project=self.create()
        url=reverse('documents:upload',args=[project.pk])
        response=self.client.post(url,{'title':'Bad','file':SimpleUploadedFile('fake.pdf',b'not PDF')})
        self.assertContains(response,'readable, unencrypted PDF')
        self.assertFalse(ProjectDocument.objects.exists())
        with patch('apps.documents.models.DocumentVersion.save',side_effect=RuntimeError('metadata error')):
            response=self.client.post(url,{'title':'Failure','file':self.pdf()})
        self.assertContains(response,'could not be saved')
        self.assertFalse(ProjectDocument.objects.exists())
        self.assertFalse(DocumentVersion.objects.exists())
        from django.conf import settings
        from pathlib import Path
        self.assertEqual(list(Path(settings.MEDIA_ROOT).rglob('*.pdf')),[])

    def test_missing_files_and_immutable_versions(self):
        project=self.create()
        version=upload_document(self.student,project,'Note',self.pdf())
        with self.assertRaises(ValidationError):
            version.save()
        version.file.delete(save=False)
        self.assertEqual(self.client.get(reverse('documents:download',args=[project.pk,version.pk])).status_code,404)
        resume=ResumeVersion(profile=self.student.profile,original_name='resume.pdf')
        resume.file.save('resume.pdf',self.pdf(),save=False)
        resume.save()
        with self.assertRaises(ValidationError):
            resume.save()
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(reverse('profiles:resume',args=[resume.pk])).status_code,404)

    def test_poll_and_private_views_are_not_cached(self):
        project=self.create()
        for url in ['/notifications/poll/','/notifications/','/projects/',reverse('projects:private',args=[project.pk])]:
            self.assertIn('no-store',self.client.get(url)['Cache-Control'])

