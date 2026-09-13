import uuid
from datetime import timedelta
from django.test import TestCase,override_settings
from django.http import Http404
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse
from apps.tasks import tests as fixtures
from apps.communities.services import appoint_leader
from apps.communities.models import CommunityEvent
from .models import Completion,IPUpdate,Achievement
from .services import perform

@override_settings(DEBUG=True,AUTHENTICATION_MODE='demo',PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class OutcomeTests(TestCase):
    setUp=fixtures.TaskTests.setUp
    user=fixtures.TaskTests.user
    data=fixtures.TaskTests.data
    create=fixtures.TaskTests.create
    pdf=fixtures.TaskTests.pdf
    prepare=fixtures.TaskTests.prepare
    submitted=fixtures.TaskTests.submitted
    decision=fixtures.TaskTests.decision
    selected=fixtures.TaskTests.selected
    ready=fixtures.TaskTests.ready
    completion=fixtures.TaskTests.completion
    verified=fixtures.TaskTests.verified
    open=fixtures.TaskTests.open
    task=fixtures.TaskTests.task
    task_data=fixtures.TaskTests.task_data
    change=fixtures.TaskTests.change
    def outcome(self,**more):return {'key':uuid.uuid4(),'revision':1,'note':'Final work reviewed','confirm':True,**more}
    def ip(self,**more):return self.outcome(**{'title':'PRIVATE SENTINEL','status_label':'Prepared','message':'Confidential preparation notes','required_information':'Please provide results','reference':'SECRET-REF','task':None,**more})
    def achievement(self,**more):return self.outcome(**{'title':'Shareable milestone','status_label':'Submitted','public_summary':'Approved public summary','milestone_date':timezone.localdate(),**more})
    def test_leader_request_mentor_completion_reopen_and_history(self):
        self.task();appoint_leader(self.teacher,self.c.pk,self.student.pk,self.c.revision,uuid.uuid4())
        data=self.outcome();perform(self.student,self.c.pk,'request',data);perform(self.student,self.c.pk,'request',data)
        with self.assertRaises(Http404):perform(self.student,self.c.pk,'complete',self.outcome(revision=2))
        perform(self.teacher,self.c.pk,'complete',self.outcome(revision=2));record=Completion.objects.get();self.assertEqual(record.state,'completed');self.assertEqual(record.confirmed_by,self.teacher)
        self.c.project.refresh_from_db();self.assertEqual(self.c.project.status,'closed')
        self.assertEqual(self.c.tasks.count(),1)
        with self.assertRaises(ValidationError):perform(self.teacher,self.c.pk,'reopen',self.outcome(revision=2))
        perform(self.teacher,self.c.pk,'reopen',self.outcome(revision=3));self.assertEqual(Completion.objects.get().state,'active')
        self.assertEqual(CommunityEvent.objects.filter(action='outcome_complete').count(),1)
    def test_private_ip_and_explicit_shareable_approval(self):
        t=self.task();data=self.ip(file=self.pdf());perform(self.teacher,self.c.pk,'ip',data);perform(self.teacher,self.c.pk,'ip',data)
        self.assertEqual(IPUpdate.objects.count(),1);self.assertFalse(Achievement.objects.exists())
        self.client.force_login(self.student)
        self.assertContains(self.client.get(reverse('ip_progress:overview',args=[self.c.pk])),'PRIVATE SENTINEL')
        self.assertNotContains(self.client.get(reverse('dashboard')),'PRIVATE SENTINEL')
        with self.assertRaises(Http404):perform(self.student,self.c.pk,'ip',self.ip())
        with self.assertRaises(ValidationError):perform(self.teacher,self.c.pk,'achievement',self.achievement(confirm=False))
        perform(self.teacher,self.c.pk,'achievement',self.achievement())
        self.assertContains(self.client.get(reverse('dashboard')),'Shareable milestone');self.assertNotContains(self.client.get(reverse('dashboard')),'SECRET-REF')
        perform(self.teacher,self.c.pk,'withdraw',self.outcome(),Achievement.objects.get().pk)
        self.assertNotContains(self.client.get(reverse('dashboard')),'Shareable milestone')
    def test_files_scope_forms_and_window(self):
        self.task();perform(self.teacher,self.c.pk,'ip',self.ip(file=self.pdf()));update=IPUpdate.objects.get()
        self.client.force_login(self.student);r=self.client.get(reverse('ip_progress:download',args=[self.c.pk,update.pk]));self.assertEqual(r.status_code,200);r.close()
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse('ip_progress:download',args=[self.c.pk,update.pk])).status_code,404)
        self.assertEqual(self.client.get(reverse('ip_progress:overview',args=[self.c.pk])).status_code,404)
        self.client.force_login(self.teacher)
        for action in ['ip','achievement','complete','request']:
            self.assertEqual(self.client.get(reverse('ip_progress:action',args=[self.c.pk,action])).status_code,200)
        perform(self.teacher,self.c.pk,'achievement',self.achievement(milestone_date=timezone.localdate()-timedelta(days=400)))
        self.assertNotContains(self.client.get(reverse('dashboard')),'Shareable milestone')
        with self.assertRaises(ValidationError):perform(self.teacher,self.c.pk,'achievement',self.achievement(milestone_date=timezone.localdate()+timedelta(days=1)))

    def test_connected_research_workflow_to_shared_achievement(self):
        t=self.task();t=self.change(t,'submit',uploads=[self.pdf()]);t=self.change(t,'review',self.teacher,submission=t.submissions.first().pk,decision='approved',feedback='Final work accepted')
        perform(self.teacher,self.c.pk,'complete',self.outcome())
        perform(self.teacher,self.c.pk,'ip',self.ip(task=t))
        perform(self.teacher,self.c.pk,'achievement',self.achievement())
        self.client.force_login(self.student)
        for name in ['history','contributions','library']:
            self.assertEqual(self.client.get(reverse('communities:'+name,args=[self.c.pk])).status_code,200)
        self.assertContains(self.client.get(reverse('dashboard')),'Shareable milestone')
        self.assertContains(self.client.get(reverse('ip_progress:overview',args=[self.c.pk])),'Completed')
        self.assertEqual(self.client.get(reverse('health')).json(),{'status':'ok'})
        self.client.logout();self.client.force_login(self.student)
        self.assertEqual(Completion.objects.get().state,'completed');self.assertEqual(t.files.count(),1)
