from unittest.mock import patch
from django.test import TestCase,override_settings,Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import DatabaseError
from apps.projects import tests as fixtures
from apps.profiles.models import ResumeVersion
from apps.notifications.models import Notification
from .models import Application
from .services import submit_application

@override_settings(DEBUG=True,AUTHENTICATION_MODE='demo',PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class ApplicationTests(TestCase):
    setUp=fixtures.ResearchModulesTests.setUp
    user=fixtures.ResearchModulesTests.user
    data=fixtures.ResearchModulesTests.data
    create=fixtures.ResearchModulesTests.create
    pdf=fixtures.ResearchModulesTests.pdf

    def prepare(self,upload=False):
        self.project=self.create(self.teacher)
        self.client.force_login(self.student)
        resume=ResumeVersion(profile=self.student.profile,original_name='original.pdf')
        resume.file.save('original.pdf',self.pdf(),save=False);resume.save()
        self.resume=resume
        self.url=reverse('recruitment:apply',args=[self.project.pk])
        data={'resume_choice':'profile','profile_resume':resume.pk,'motivation':'I can build accessible interfaces.','academic_score':'8/10'}
        if upload:
            data.update(resume_choice='upload',uploaded_resume=self.pdf('different.pdf'))
        self.formdata=data
        response=self.client.post(self.url,data)
        self.assertEqual(response.status_code,302)
        return Application.objects.get()

    def test_review_then_submit_preserves_snapshot_and_original_resume(self):
        app=self.prepare()
        url=reverse('recruitment:detail',args=[app.pk])
        self.assertEqual(app.status,'draft')
        self.assertContains(self.client.get(url),'original.pdf')
        self.assertContains(self.client.get(url),'Confirm &amp; submit application',html=False)
        self.student.profile.name='Changed later';self.student.profile.save()
        self.client.post(url,{'revision':app.revision})
        app.refresh_from_db()
        self.assertEqual(app.status,'submitted')
        self.assertIsNotNone(app.submitted_at)
        self.assertEqual(app.snapshot['name'],'student')
        replacement=ResumeVersion(profile=self.student.profile,original_name='new.pdf')
        replacement.file.save('new.pdf',self.pdf(),save=False);replacement.save()
        self.assertEqual(app.profile_resume_id,self.resume.pk)
        response=self.client.get(reverse('recruitment:resume',args=[app.pk])); self.assertEqual(response.status_code,200); response.close()

    def test_new_upload_does_not_replace_profile_resume_and_is_private(self):
        app=self.prepare(upload=True)
        self.assertIsNone(app.profile_resume_id)
        self.assertEqual(app.resume_name,'different.pdf')
        self.assertEqual(self.student.profile.resumes.count(),1)
        self.assertEqual(self.student.profile.latest_resume.pk,self.resume.pk)
        url=reverse('recruitment:resume',args=[app.pk])
        response=self.client.get(url)
        self.assertTrue(b''.join(response.streaming_content).startswith(b'%PDF'))
        response.close()
        self.assertIn('no-store',response['Cache-Control'])
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(url).status_code,404)
        self.assertNotContains(self.client.get(reverse('recruitment:project',args=[self.project.pk])),'student')
        submit_application(self.student,app.pk,app.revision)
        response=self.client.get(url); self.assertEqual(response.status_code,200); response.close()
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(url).status_code,404)
        self.assertEqual(self.client.get(reverse('recruitment:detail',args=[app.pk])).status_code,404)

    def test_retries_one_application_and_one_notification_per_recipient(self):
        app=self.prepare()
        self.client.post(self.url,self.formdata)
        app.refresh_from_db()
        for _ in range(2):
            self.client.post(reverse('recruitment:detail',args=[app.pk]),{'revision':app.revision})
        self.assertEqual(Application.objects.count(),1)
        self.assertEqual(Notification.objects.filter(title='Application submitted').count(),1)
        self.assertEqual(Notification.objects.filter(title='New application').count(),1)
        before=Application.objects.get().snapshot
        self.client.post(self.url,self.formdata|{'motivation':'Cannot change submitted text'})
        self.assertEqual(Application.objects.get().snapshot,before)
        self.assertNotEqual(Application.objects.get().motivation,'Cannot change submitted text')
        self.client.post('/accounts/logout/')
        self.client.post('/accounts/login/',{'email':self.student.email,'password':'Testing!2026'})
        self.assertContains(self.client.get('/applications/'),'Submitted')

    def test_reject_teacher_owner_closed_and_unapproved_mentor(self):
        app=self.prepare()
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(self.url).status_code,404)
        own=self.create(self.student)
        own.mentor=self.teacher;own.status='recruiting';own.save()
        self.assertEqual(self.client.get(reverse('recruitment:apply',args=[own.pk])).status_code,404)
        self.project.status='closed';self.project.save()
        response=self.client.post(reverse('recruitment:detail',args=[app.pk]),{'revision':app.revision})
        self.assertEqual(response.status_code,404)
        app.refresh_from_db();self.assertEqual(app.status,'draft')
        self.project.status='recruiting';self.project.save()
        self.teacher.profile.teacher_approved=False;self.teacher.profile.save()
        self.assertEqual(self.client.get(self.url).status_code,404)

    def test_other_resume_and_invalid_upload_rejected(self):
        app=self.prepare()
        other=ResumeVersion(profile=self.other.profile,original_name='other.pdf')
        other.file.save('other.pdf',self.pdf(),save=False);other.save()
        response=self.client.post(self.url,self.formdata|{'profile_resume':other.pk})
        self.assertContains(response,'Select a valid choice')
        response=self.client.post(self.url,self.formdata|{'resume_choice':'upload',
            'uploaded_resume':SimpleUploadedFile('bad.pdf',b'not a PDF')})
        self.assertContains(response,'readable, unencrypted PDF')
        self.assertEqual(Application.objects.get().profile_resume_id,self.resume.pk)

    def test_stale_review_and_notification_rollback(self):
        app=self.prepare()
        url=reverse('recruitment:detail',args=[app.pk])
        self.client.post(self.url,self.formdata)
        self.assertContains(self.client.post(url,{'revision':app.revision}),'draft changed')
        app.refresh_from_db()
        with patch('apps.recruitment.services.notify',side_effect=DatabaseError('error')):
            self.assertContains(self.client.post(url,{'revision':app.revision}),'could not be submitted')
        app.refresh_from_db()
        self.assertEqual(app.status,'draft')
        self.assertFalse(Notification.objects.filter(title='New application').exists())

    def test_csrf_upload_failure_cleanup_and_missing_resume(self):
        app=self.prepare()
        strict=Client(enforce_csrf_checks=True);strict.force_login(self.student)
        self.assertEqual(strict.post(reverse('recruitment:detail',args=[app.pk]),{'revision':1}).status_code,403)
        with patch('apps.recruitment.models.Application.save',side_effect=DatabaseError('metadata failure')):
            response=self.client.post(self.url,self.formdata|{'resume_choice':'upload','uploaded_resume':self.pdf('failed.pdf')})
        self.assertContains(response,'could not be saved')
        from pathlib import Path
        from django.conf import settings
        self.assertEqual(list((Path(settings.MEDIA_ROOT)/'applications').rglob('*.pdf')),[])
        self.resume.file.delete(save=False)
        self.assertContains(self.client.post(reverse('recruitment:detail',args=[app.pk]),{'revision':app.revision}),'could not be submitted')
