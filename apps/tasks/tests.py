import uuid
from pathlib import Path
from unittest.mock import patch
from django.test import TestCase,Client,override_settings
from django.urls import reverse
from django.http import Http404
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.conf import settings
from apps.collaboration import tests as fixtures
from apps.communities.models import Sprint,CommunityEvent
from apps.communities.services import appoint_leader
from apps.notifications.models import Notification
from .models import Task,Submission,Review,TaskFile,TaskComment
from .services import save_task,act
from .views import totals

@override_settings(DEBUG=True,AUTHENTICATION_MODE='demo',PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class TaskTests(TestCase):
    setUp=fixtures.ChatTests.setUp
    user=fixtures.ChatTests.user
    data=fixtures.ChatTests.data
    create=fixtures.ChatTests.create
    pdf=fixtures.ChatTests.pdf
    prepare=fixtures.ChatTests.prepare
    submitted=fixtures.ChatTests.submitted
    decision=fixtures.ChatTests.decision
    selected=fixtures.ChatTests.selected
    ready=fixtures.ChatTests.ready
    completion=fixtures.ChatTests.completion
    verified=fixtures.ChatTests.verified
    open=fixtures.ChatTests.open
    def task_data(self,**changes):
        return {'key':uuid.uuid4(),'revision':1,'title':'Build prototype','description':'Create an accessible first prototype.','milestone':'First demo','assignee':self.student,'sprint':None,'due_date':None,**changes}
    def task(self):
        self.c=self.open();self.sprint=Sprint.objects.create(community=self.c,title='Sprint one',goal='Prototype')
        return save_task(self.teacher,self.c.pk,self.task_data(sprint=self.sprint))
    def change(self,t,action,user=None,**changes):
        t.refresh_from_db();data={'key':uuid.uuid4(),'revision':t.revision,'summary':'Work completed','blocker':'','evidence':[],**changes}
        return act(user or self.student,self.c.pk,t.pk,action,data,data.pop('uploads',[]))
    def test_assignment_roles_retry_and_scope(self):
        t=self.task();data=self.task_data();a=save_task(self.teacher,self.c.pk,data);self.assertEqual(save_task(self.teacher,self.c.pk,data).pk,a.pk)
        with self.assertRaises(Http404):save_task(self.student,self.c.pk,self.task_data())
        with self.assertRaises(Http404):save_task(self.teacher,self.c.pk,self.task_data(assignee=self.other))
        appoint_leader(self.teacher,self.c.pk,self.student.pk,self.c.revision,uuid.uuid4())
        self.assertTrue(save_task(self.student,self.c.pk,self.task_data()))
        self.assertEqual(Notification.objects.filter(title='Research task assigned').count(),3)
        foreign=self.create(self.teacher)
        from apps.communities.models import Community
        c2=Community.objects.create(project=foreign,created_by=self.teacher)
        s2=Sprint.objects.create(community=c2,title='Other',goal='Other')
        with self.assertRaises(Http404):save_task(self.teacher,self.c.pk,self.task_data(sprint=s2))
    def test_complete_review_revision_reopen_counts(self):
        t=self.task();self.assertEqual(totals(self.c.tasks.all())['percent'],0)
        t=self.change(t,'work',blocker='Need dataset');self.assertEqual(t.status,'progress')
        with self.assertRaises(ValidationError):self.change(t,'submit',blocker='Need dataset')
        t=self.change(t,'submit',uploads=[self.pdf()]);first=t.submissions.first();original=first.files.get()
        self.assertEqual(totals(self.c.tasks.all())['approved'],0)
        t=self.change(t,'review',self.teacher,submission=first.pk,decision='changes',feedback='Add evaluation results')
        t=self.change(t,'submit',summary='Evaluation added',uploads=[self.pdf()]);second=t.submissions.first()
        self.assertEqual(first.files.get().pk,original.pk);self.assertNotEqual(second.files.get().pk,original.pk)
        t=self.change(t,'review',self.teacher,submission=second.pk,decision='approved',feedback='Accepted')
        self.assertEqual(totals(self.sprint.tasks.all())['percent'],100)
        save_task(self.teacher,self.c.pk,self.task_data(sprint=self.sprint));self.assertEqual(totals(self.sprint.tasks.all())['percent'],50)
        t=self.change(t,'reopen',self.teacher,feedback='New requirements');self.assertEqual(totals(self.sprint.tasks.all())['percent'],0)
        self.assertEqual(Review.objects.count(),2);self.assertEqual(Submission.objects.count(),2)
    def test_self_review_and_stale_or_repeated_actions(self):
        t=self.task();appoint_leader(self.teacher,self.c.pk,self.student.pk,self.c.revision,uuid.uuid4());t=self.change(t,'submit')
        with self.assertRaises(Http404):self.change(t,'review',submission=t.submissions.first().pk,decision='approved',feedback='Self')
        data={'key':uuid.uuid4(),'revision':t.revision,'submission':t.submissions.first().pk,'decision':'approved','feedback':'Good work'}
        act(self.teacher,self.c.pk,t.pk,'review',data);act(self.teacher,self.c.pk,t.pk,'review',data)
        self.assertEqual(Review.objects.count(),1)
        with self.assertRaises(ValidationError):act(self.teacher,self.c.pk,t.pk,'review',{**data,'key':uuid.uuid4()})
        with self.assertRaises(ValidationError):save_task(self.teacher,self.c.pk,self.task_data(revision=t.revision),t.pk)
    def test_only_assignee_can_update_and_submission_freezes(self):
        t=self.task()
        with self.assertRaises(Http404):self.change(t,'work',self.teacher)
        t=self.change(t,'submit')
        with self.assertRaises(ValidationError):self.change(t,'work')
        with self.assertRaises(ValidationError):save_task(self.teacher,self.c.pk,self.task_data(revision=t.revision),t.pk)
        sub=t.submissions.first();sub.summary='overwrite'
        with self.assertRaises(ValidationError):sub.save()
    def test_private_file_versions_comments_and_revocation(self):
        t=self.task();t=self.change(t,'work',uploads=[self.pdf()]);f=t.files.get()
        t=self.change(t,'comment',self.teacher,body='See slide two',file=f)
        self.assertEqual(TaskComment.objects.get().file,f)
        self.client.force_login(self.student);url=reverse('tasks:download',args=[self.c.pk,f.pk]);r=self.client.get(url)
        self.assertEqual(r.status_code,200);self.assertIn('no-store',r['Cache-Control']);r.close()
        self.client.force_login(self.other);self.assertEqual(self.client.get(url).status_code,404)
        from apps.agreements.services import review
        review(self.teacher,self.evidence.pk,'correction','Fix evidence',uuid.uuid4(),str(self.evidence.review.pk))
        self.client.force_login(self.student)
        for name,args in [('board',[self.c.pk]),('detail',[self.c.pk,t.pk]),('download',[self.c.pk,f.pk])]:self.assertEqual(self.client.get(reverse('tasks:'+name,args=args)).status_code,404)
        with self.assertRaises(Http404):self.change(t,'work')
    def test_storage_cleanup_on_transaction_failure(self):
        t=self.task()
        with patch('apps.tasks.models.TaskFile.save',side_effect=DatabaseError):
            with self.assertRaises(DatabaseError):self.change(t,'submit',uploads=[self.pdf()])
        self.assertFalse(TaskFile.objects.exists());self.assertFalse(Submission.objects.exists())
        self.assertFalse(list((Path(settings.MEDIA_ROOT)/'task-files').rglob('*.pdf')))
    def test_forms_pages_and_counts(self):
        t=self.task();self.client.force_login(self.teacher)
        for name,args in [('board',[self.c.pk]),('new',[self.c.pk]),('edit',[self.c.pk,t.pk]),('detail',[self.c.pk,t.pk])]:self.assertEqual(self.client.get(reverse('tasks:'+name,args=args)).status_code,200)
        self.client.force_login(self.student)
        url=reverse('tasks:action',args=[self.c.pk,t.pk,'submit'])
        response=self.client.post(url,{'key':uuid.uuid4(),'revision':t.revision,'summary':'Ready for review','blocker':'','uploads':self.pdf()})
        self.assertEqual(response.status_code,302)
        self.assertContains(self.client.get(reverse('tasks:detail',args=[self.c.pk,t.pk])),'Ready for review')
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(reverse('tasks:action',args=[self.c.pk,t.pk,'review'])).status_code,200)
        self.assertContains(self.client.get(reverse('communities:sprints',args=[self.c.pk])),'0 / 1 tasks approved')
        self.assertEqual(self.client.get(reverse('tasks:board',args=[self.c.pk]),{'sprint':'invalid'}).status_code,404)
    def test_cross_task_file_review_and_csrf(self):
        t=self.task();t=self.change(t,'submit',uploads=[self.pdf()]);sub=t.submissions.first();file=sub.files.get()
        other=save_task(self.teacher,self.c.pk,self.task_data())
        with self.assertRaises(Http404):self.change(other,'comment',body='Wrong file',file=file)
        with self.assertRaises(Http404):self.change(other,'submit',evidence=[file])
        other=self.change(other,'submit')
        with self.assertRaises(Http404):self.change(other,'review',self.teacher,submission=sub.pk,decision='approved',feedback='Wrong task')
        client=Client(enforce_csrf_checks=True);client.force_login(self.student)
        self.assertEqual(client.post(reverse('tasks:action',args=[self.c.pk,t.pk,'comment']),{'body':'No token'}).status_code,403)

    def test_leader_can_review_another_members_work(self):
        t=self.task();appoint_leader(self.teacher,self.c.pk,self.student.pk,self.c.revision,uuid.uuid4())
        t=save_task(self.student,self.c.pk,self.task_data(assignee=self.teacher))
        t=self.change(t,'submit',self.teacher)
        t=self.change(t,'review',self.student,submission=t.submissions.first().pk,decision='approved',feedback='Reviewed and accepted')
        self.assertEqual(t.status,'approved')
        self.assertEqual(t.submissions.first().review.reviewer,self.student)
