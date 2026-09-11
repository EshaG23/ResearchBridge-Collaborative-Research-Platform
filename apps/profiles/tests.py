
import io
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone
from pypdf import PdfWriter
from apps.accounts.models import User
from .models import Profile, Department, Skill, ResearchInterest, ResumeVersion

@override_settings(DEBUG=True, AUTHENTICATION_MODE='demo')
class ProfileWorkflowTests(TestCase):
    def setUp(self):
        self.storage = tempfile.TemporaryDirectory()
        self.addCleanup(self.storage.cleanup)
        self.override = override_settings(MEDIA_ROOT=self.storage.name)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.user = User.objects.create_user('demo.student@rbunagpur.in', is_demo=True, roster_role='student')
        self.client.force_login(self.user)
        self.department = Department.objects.get(name='CSE')
        self.skill = Skill.objects.create(name='Python')
        self.interest = ResearchInterest.objects.create(name='AI')
        self.data = {'role':'student','name':'Demo Student','phone':'9876543210','department':self.department.pk,
                     'skills':[self.skill.pk],'interests':[self.interest.pk], 'availability':10,'year':2,'action':'complete'}
    def pdf(self, name='resume.pdf'):
        writer = PdfWriter()
        writer.add_blank_page(width=100,height=100)
        stream = io.BytesIO();writer.write(stream)
        return SimpleUploadedFile(name,stream.getvalue(),content_type='application/pdf')

    def test_required_student_fields_and_no_gate_bypass(self):
        response = self.client.post('/profile/', {'role':'student','action':'complete'})
        self.assertContains(response,'This field is required')
        self.assertIsNone(Profile.objects.get().completed_at)
        self.assertRedirects(self.client.get('/dashboard/'),'/profile/')

    def test_completed_profile_resume_versions_logout_and_return(self):
        self.assertEqual(self.client.post('/profile/',self.data|{'resume':self.pdf()}).status_code,302)
        profile = Profile.objects.get()
        self.assertIsNotNone(profile.completed_at)
        first = ResumeVersion.objects.get()
        with first.file.open('rb') as stream:
            original = stream.read()
        self.client.post('/profile/',self.data|{'resume':self.pdf('new.pdf')})
        self.assertEqual(ResumeVersion.objects.count(),2)
        with first.file.open('rb') as stream:
            self.assertEqual(stream.read(),original)
        self.client.post('/accounts/logout/')
        self.assertEqual(self.client.get('/dashboard/').status_code,302)
        self.user.set_password('ExistingTest!2026'); self.user.save()
        self.client.post('/accounts/login/', {'email': self.user.email, 'password':'ExistingTest!2026'})
        self.assertContains(self.client.get('/dashboard/'),'Demo Student')
        response = self.client.get(f'/profile/resumes/{first.pk}/')
        self.assertEqual(response.status_code,200)
        self.assertEqual(b''.join(response.streaming_content),original)

    def test_draft_retained_and_edit_cannot_escalate_role(self):
        self.client.post('/profile/',{'role':'student','name':'Draft name','action':'draft'})
        self.assertEqual(Profile.objects.get().name,'Draft name')
        self.assertIsNone(Profile.objects.get().completed_at)
        self.client.post('/profile/',self.data|{'resume':self.pdf()})
        self.client.post('/profile/',self.data|{'role':'teacher','teacher_approved':'on'})
        profile = Profile.objects.get()
        self.assertEqual(profile.role,'student')
        self.assertFalse(profile.teacher_approved)

    def test_teacher_optional_fields_and_approval_not_self_granted(self):
        self.user.roster_role='teacher'; self.user.save()
        data = self.data|{'role':'teacher','availability':'','year':'','teacher_approved':'on'}
        response = self.client.post('/profile/',data)
        self.assertEqual(response.status_code,302)
        profile = Profile.objects.get()
        self.assertFalse(profile.is_verified_teacher)
        self.assertIsNotNone(profile.completed_at)
        self.assertIsNone(profile.year)
        self.assertFalse(ResumeVersion.objects.exists())

    def test_private_download_denies_another_user(self):
        self.client.post('/profile/',self.data|{'resume':self.pdf()})
        pk = ResumeVersion.objects.get().pk
        other = User.objects.create_user('other@rbunagpur.in', is_demo=True, roster_role='student')
        self.client.force_login(other)
        self.assertEqual(self.client.get(f'/profile/resumes/{pk}/').status_code,404)

    def test_invalid_pdf_phone_availability_and_scholar_rejected(self):
        response = self.client.post('/profile/', self.data|{'phone':'abc','availability':100,
            'resume':SimpleUploadedFile('bad.pdf',b'not a pdf',content_type='application/pdf')})
        self.assertEqual(response.status_code,200)
        self.assertFalse(ResumeVersion.objects.exists())
        self.assertIsNone(Profile.objects.get().completed_at)
        response = self.client.post('/profile/',self.data|{'role':'teacher','scholar_url':'https://example.com/fake'})
        self.assertContains(response,'scholar.google.com')

    def test_save_failure_does_not_claim_success_or_leave_file(self):
        from unittest.mock import patch
        with patch('apps.profiles.models.ResumeVersion.save',side_effect=RuntimeError('storage metadata failed')):
            response = self.client.post('/profile/',self.data|{'resume':self.pdf()})
        self.assertContains(response,'could not be saved')
        self.assertFalse(ResumeVersion.objects.exists())
        self.assertIsNone(Profile.objects.get().completed_at)
