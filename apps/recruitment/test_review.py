import uuid
from datetime import timedelta,timezone as dt_timezone
from unittest.mock import patch
from django.test import TestCase,override_settings,Client
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from apps.recruitment import tests as fixtures
from apps.projects.models import Project
from apps.notifications.models import Notification
from apps.notifications.services import authorised_url
from .models import Application,ReviewDecision,MeetingInvitation
from .services import submit_application
from .review_services import review_application,invite_to_meeting,cancel_meeting
from .review_forms import MeetingForm

@override_settings(DEBUG=True,AUTHENTICATION_MODE='demo',PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class ApplicantReviewTests(TestCase):
    setUp=fixtures.ApplicationTests.setUp
    user=fixtures.ApplicationTests.user
    data=fixtures.ApplicationTests.data
    create=fixtures.ApplicationTests.create
    pdf=fixtures.ApplicationTests.pdf
    prepare=fixtures.ApplicationTests.prepare

    def submitted(self):
        self.app=self.prepare()
        submit_application(self.student,self.app.pk,self.app.revision)
        self.app.refresh_from_db()
        return self.app

    def decision(self,action,key=None,revision=None):
        return review_application(self.teacher,self.app.pk,action,
            self.app.revision if revision is None else revision,key or uuid.uuid4())

    def meeting_data(self):
        return {'request_key':uuid.uuid4(),'revision':self.app.revision,
            'message':'Private meeting discussion','venue':'Private Lab 5',
            'scheduled_at':timezone.now()+timedelta(days=2),'online_url':'https://meet.example.com/research'}

    def test_shortlist_selection_are_distinct_and_history_preserves_snapshot(self):
        self.submitted()
        snapshot=self.app.snapshot.copy()
        resume=self.app.profile_resume_id
        key=uuid.uuid4()
        self.decision('shortlist',key)
        self.decision('shortlist',key) # Same old revision is an idempotent retry.
        self.app.refresh_from_db()
        self.assertEqual(self.app.status,'shortlisted')
        self.assertEqual(ReviewDecision.objects.count(),1)
        self.assertEqual(Notification.objects.filter(title='Application status updated').count(),1)
        self.decision('select')
        self.app.refresh_from_db()
        self.assertEqual(self.app.status,'selected')
        self.assertEqual(self.app.snapshot,snapshot)
        self.assertEqual(self.app.profile_resume_id,resume)
        self.assertEqual(list(self.app.decisions.values_list('new_status',flat=True)),['selected','shortlisted'])
        self.assertEqual(self.project.applications.filter(status='selected').count(),1)
        self.assertFalse(Notification.objects.filter(title__icontains='letter').exists())

    def test_reopen_and_return_to_review_and_stale_actions(self):
        self.submitted()
        old_revision=self.app.revision
        self.decision('not_selected')
        self.app.refresh_from_db()
        self.decision('reopen')
        self.app.refresh_from_db()
        self.assertEqual(self.app.status,'submitted')
        self.decision('shortlist')
        self.app.refresh_from_db()
        self.decision('remove_shortlist')
        self.app.refresh_from_db()
        self.assertEqual(self.app.status,'submitted')
        with self.assertRaises(ValidationError):
            self.decision('shortlist',revision=old_revision)
        with self.assertRaises(ValidationError):
            self.decision('select')
        with self.assertRaises(ValidationError):
            self.decision('invented')

    def test_selection_capacity_and_final_decision_guard(self):
        self.submitted()
        self.project.open_positions=1;self.project.save()
        self.decision('shortlist');self.app.refresh_from_db();self.decision('select');self.app.refresh_from_db()
        with self.assertRaises(ValidationError):
            self.decision('not_selected')
        other=Application.objects.create(project=self.project,applicant=self.other,status='shortlisted',
            profile_resume=self.resume,resume_name='fixture.pdf',snapshot={},motivation='fixture')
        with self.assertRaises(ValidationError):
            review_application(self.teacher,other.pk,'select',other.revision,uuid.uuid4())
        self.assertEqual(self.project.applications.filter(status='selected').count(),1)

    def test_proposer_overview_excludes_private_records_and_actions(self):
        self.submitted()
        self.project.creator=self.other;self.project.save()
        self.client.force_login(self.other)
        response=self.client.get(reverse('recruitment:project',args=[self.project.pk]))
        self.assertContains(response,'student')
        for private in [self.student.email,'original.pdf','I can build accessible interfaces.','Review application','Submitted résumé']:
            self.assertNotContains(response,private)
        row=response.context['page'][0]
        self.assertNotIn('snapshot',row)
        self.assertNotIn('snapshot__phone',row)
        for url in [reverse('recruitment:detail',args=[self.app.pk]),reverse('recruitment:resume',args=[self.app.pk]),
            reverse('recruitment:meeting',args=[self.app.pk])]:
            self.assertEqual(self.client.get(url).status_code,404)
        self.assertEqual(self.client.post(reverse('recruitment:decision',args=[self.app.pk]),
            {'action':'shortlist','revision':1,'request_key':uuid.uuid4()}).status_code,404)

    def test_only_attached_approved_mentor_can_decide(self):
        self.submitted()
        outsider=self.user('faculty-outsider','teacher')
        for user in [self.student,self.other,outsider]:
            self.client.force_login(user)
            self.assertEqual(self.client.post(reverse('recruitment:decision',args=[self.app.pk]),
                {'action':'shortlist','revision':1,'request_key':uuid.uuid4()}).status_code,404)
        self.teacher.profile.teacher_approved=False;self.teacher.profile.save()
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(reverse('recruitment:project',args=[self.project.pk])).status_code,404)
        self.assertEqual(self.client.get(reverse('recruitment:resume',args=[self.app.pk])).status_code,404)

    def test_drafts_hidden_and_not_reviewable(self):
        self.app=self.prepare()
        self.client.force_login(self.teacher)
        self.assertContains(self.client.get(reverse('recruitment:project',args=[self.project.pk])),'No applicants')
        with self.assertRaises(ValidationError):
            self.decision('shortlist')
        with self.assertRaises(ValidationError):
            invite_to_meeting(self.teacher,self.app.pk,self.meeting_data())

    def test_meeting_ist_validation_and_private_notification_links(self):
        self.submitted()
        local=timezone.localtime(timezone.now()+timedelta(days=2)).replace(hour=15,minute=30,second=0,microsecond=0)
        form=MeetingForm({'request_key':str(uuid.uuid4()),'revision':self.app.revision,
            'message':'Private meeting discussion','venue':'Private Lab 5','scheduled_at':local.strftime('%Y-%m-%dT%H:%M'),
            'online_url':'https://meet.example.com/research'})
        self.assertTrue(form.is_valid(),form.errors)
        meeting=invite_to_meeting(self.teacher,self.app.pk,form.cleaned_data)
        self.assertEqual(meeting.scheduled_at.astimezone(dt_timezone.utc).hour,10)
        self.assertEqual(meeting.scheduled_at.astimezone(dt_timezone.utc).minute,0)
        note=Notification.objects.get(title='Meeting invitation')
        self.assertEqual(authorised_url(note,self.student),reverse('recruitment:detail',args=[self.app.pk]))
        self.assertIsNone(authorised_url(note,self.other))
        self.assertNotIn('Private Lab',note.message)
        self.client.force_login(self.student)
        response=self.client.get(reverse('recruitment:detail',args=[self.app.pk]))
        self.assertContains(response,'15:30')
        self.assertContains(response,'IST')
        self.assertContains(response,'Private Lab 5')
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse('recruitment:detail',args=[self.app.pk])).status_code,404)

    def test_meeting_retries_cancellation_and_history(self):
        self.submitted()
        data=self.meeting_data()
        meeting=invite_to_meeting(self.teacher,self.app.pk,data)
        self.assertEqual(invite_to_meeting(self.teacher,self.app.pk,data).pk,meeting.pk)
        self.assertEqual(MeetingInvitation.objects.count(),1)
        self.assertEqual(Notification.objects.filter(title='Meeting invitation').count(),1)
        cancel_meeting(self.teacher,meeting.pk);cancel_meeting(self.teacher,meeting.pk)
        meeting.refresh_from_db()
        self.assertIsNotNone(meeting.cancelled_at)
        self.assertEqual(meeting.cancelled_by,self.teacher)
        self.assertEqual(Notification.objects.filter(title='Meeting cancelled').count(),1)
        self.assertEqual(meeting.message,data['message'])
        self.client.force_login(self.student)
        self.assertContains(self.client.get(reverse('recruitment:detail',args=[self.app.pk])),'Cancelled')

    def test_invalid_meeting_and_stale_review_fail_safely(self):
        self.submitted()
        data=self.meeting_data()
        with self.assertRaises(ValidationError):
            invite_to_meeting(self.teacher,self.app.pk,data|{'scheduled_at':timezone.now()-timedelta(minutes=1)})
        with self.assertRaises(ValidationError):
            invite_to_meeting(self.teacher,self.app.pk,data|{'online_url':'javascript:alert(1)'})
        self.decision('shortlist')
        with self.assertRaises(ValidationError):
            invite_to_meeting(self.teacher,self.app.pk,data)
        self.assertFalse(MeetingInvitation.objects.exists())

    def test_transactional_rollback_of_status_and_meeting(self):
        self.submitted()
        with patch('apps.recruitment.review_services.notify',side_effect=DatabaseError('failed')):
            with self.assertRaises(DatabaseError):
                self.decision('shortlist')
            with self.assertRaises(DatabaseError):
                invite_to_meeting(self.teacher,self.app.pk,self.meeting_data())
        self.app.refresh_from_db()
        self.assertEqual(self.app.status,'submitted')
        self.assertFalse(ReviewDecision.objects.exists())
        self.assertFalse(MeetingInvitation.objects.exists())

    def test_mentor_ui_filters_post_csrf_and_applicant_persistence(self):
        self.submitted()
        self.client.force_login(self.teacher)
        manage=reverse('recruitment:project',args=[self.project.pk])
        self.assertContains(self.client.get(manage),'Submitted résumé')
        self.assertContains(self.client.get(manage,{'status':'invalid'}),'correct the filters')
        self.assertEqual(self.client.get(manage,{'status':'shortlisted'}).context['page'].paginator.count,0)
        url=reverse('recruitment:decision',args=[self.app.pk])
        self.assertEqual(self.client.get(url).status_code,405)
        strict=Client(enforce_csrf_checks=True);strict.force_login(self.teacher)
        self.assertEqual(strict.post(url,{'action':'shortlist','revision':1,'request_key':uuid.uuid4()}).status_code,403)
        response=self.client.post(url,{'action':'shortlist','revision':self.app.revision,'request_key':uuid.uuid4()})
        self.assertRedirects(response,reverse('recruitment:detail',args=[self.app.pk]))
        self.assertEqual(self.client.get(manage,{'status':'shortlisted'}).context['page'].paginator.count,1)
        self.client.post('/accounts/logout/')
        self.client.post('/accounts/login/',{'email':self.student.email,'password':'Testing!2026'})
        self.assertContains(self.client.get('/applications/'),'Shortlisted')
        self.assertContains(self.client.get(reverse('recruitment:detail',args=[self.app.pk])),'Review history')
        self.assertNotContains(self.client.get(reverse('recruitment:detail',args=[self.app.pk])),'Finalize selection')

    def test_meeting_cancel_is_private_post_only_and_nonduplicating(self):
        self.submitted()
        meeting=invite_to_meeting(self.teacher,self.app.pk,self.meeting_data())
        url=reverse('recruitment:cancel-meeting',args=[meeting.pk])
        self.client.force_login(self.student)
        self.assertEqual(self.client.post(url).status_code,404)
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(url).status_code,405)
        self.client.post(url)
        self.client.post(url)
        self.assertEqual(Notification.objects.filter(title='Meeting cancelled').count(),1)
