import uuid
from django.test import TestCase,override_settings
from django.urls import reverse
from django.core.exceptions import ValidationError
from apps.tasks import tests as fixtures
from apps.tasks.services import save_task
from apps.communities.history_views import file_rows,activity
from apps.collaboration.services import send
from apps.collaboration.views import unread_context

@override_settings(DEBUG=True,AUTHENTICATION_MODE='demo',PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class HistoryTests(TestCase):
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
    def test_file_versions_preserve_review_and_comments(self):
        t=self.task();t=self.change(t,'submit',uploads=[self.pdf()]);first=t.submissions.first();f=first.files.get()
        t=self.change(t,'review',self.teacher,submission=first.pk,decision='changes',feedback='Revise')
        t=self.change(t,'comment',self.teacher,body='Keep this version for comparison',file=f)
        t=self.change(t,'submit',uploads=[self.pdf()],replaces=f,revision_note='Added results')
        second=t.submissions.first();f2=second.files.get()
        self.assertEqual(f2.replaces_id,f.pk);self.assertEqual(f2.version,2);self.assertEqual(first.files.get().pk,f.pk)
        rows=file_rows(self.c);self.assertEqual(len({r['group'] for r in rows}),1);self.assertEqual(sum(r['latest'] for r in rows),1)
        t=self.change(t,'review',self.teacher,submission=second.pk,decision='approved',feedback='Accepted')
        self.client.force_login(self.student)
        response=self.client.get(reverse('communities:contributions',args=[self.c.pk]));people=response.context['people'];student=next(p for p in people if p['id']==str(self.student.pk))
        self.assertEqual((student['submissions'],student['uploads'],student['revisions'],student['approved']),(2,2,1,1))
        self.student.profile.name='Renamed person';self.student.profile.save()
        self.assertContains(self.client.get(reverse('communities:library',args=[self.c.pk])),'Added results')
        self.assertNotContains(self.client.get(reverse('communities:contributions',args=[self.c.pk])),'Renamed person')
        t=self.change(t,'reopen',self.teacher,feedback='More work')
        with self.assertRaises(ValidationError):self.change(t,'work',uploads=[self.pdf()],replaces=f)
    def test_history_filters_and_private_scope(self):
        t=self.task();t=self.change(t,'work',blocker='Missing data');t=self.change(t,'work',blocker='')
        self.client.force_login(self.teacher)
        for name in ['history','library','contributions']:self.assertEqual(self.client.get(reverse('communities:'+name,args=[self.c.pk])).status_code,200)
        url=reverse('communities:history',args=[self.c.pk]);self.assertContains(self.client.get(url),'Blocker resolved')
        response=self.client.get(url,{'kind':'task','member':self.student.pk});self.assertTrue(all(r['user']==str(self.student.pk) for r in response.context['page']))
        self.assertContains(self.client.get(url,{'start':'2030-01-02','end':'2020-01-01'}),'end date must be on or after')
        self.client.force_login(self.other)
        for name in ['history','library','contributions']:self.assertEqual(self.client.get(reverse('communities:'+name,args=[self.c.pk])).status_code,404)
    def test_summary_resource_revisions(self):
        self.task()
        from apps.communities.summary_services import save_resource
        from apps.communities.models import SummaryResource
        self.c.refresh_from_db();data={'key':uuid.uuid4(),'revision':self.c.revision,'title':'Research notes','category':'paper','file':self.pdf(),'url':''}
        first=SummaryResource.objects.get(pk=save_resource(self.teacher,self.c.pk,data));self.c.refresh_from_db()
        data.update(key=uuid.uuid4(),revision=self.c.revision,file=self.pdf(),replaces=first,revision_note='Expanded')
        second=SummaryResource.objects.get(pk=save_resource(self.teacher,self.c.pk,data))
        self.assertEqual(second.version,2);self.assertTrue(first.file.storage.exists(first.file.name))
        self.assertEqual(save_resource(self.teacher,self.c.pk,data),str(second.pk))
    def test_chat_unread_is_per_user_persistent_and_scoped(self):
        self.task();m=send(self.teacher,self.c.pk,uuid.uuid4(),'New message');send(self.student,self.c.pk,uuid.uuid4(),'My own message')
        self.assertEqual(unread_context(self.student)['chat_unread'],1);self.assertEqual(unread_context(self.other)['chat_unread'],0)
        self.client.force_login(self.student);url=reverse('collaboration:read',args=[self.c.pk])
        self.assertEqual(self.client.post(url,{'last':m.pk},HTTP_X_CHAT_USER=str(self.teacher.pk)).status_code,409)
        self.assertEqual(self.client.post(url,{'last':m.pk},HTTP_X_CHAT_USER=str(self.student.pk)).status_code,200)
        self.client.logout();self.client.force_login(self.student);self.assertEqual(unread_context(self.student)['chat_unread'],0)
        self.assertEqual(unread_context(self.teacher)['chat_unread'],1)
        self.assertContains(self.client.get(reverse('dashboard')),'0 new messages')
        self.assertContains(self.client.get(reverse('tasks:board',args=[self.c.pk])),'Completed (0)')
