import uuid
from django.test import TestCase,override_settings
from django.core.exceptions import ValidationError
from django.http import Http404
from django.urls import reverse
from apps.agreements import tests as fixtures
from apps.agreements.services import review
from apps.recruitment.models import Application
from apps.core.permissions import can_view_confidential
from .services import confirmation,create_or_sync,appoint_leader
from .models import Community,Membership,CommunityEvent
from .permissions import can_enter,can_edit

@override_settings(DEBUG=True,AUTHENTICATION_MODE='demo',PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class CommunityTests(TestCase):
    setUp=fixtures.AgreementTests.setUp
    user=fixtures.AgreementTests.user
    data=fixtures.AgreementTests.data
    create=fixtures.AgreementTests.create
    pdf=fixtures.AgreementTests.pdf
    prepare=fixtures.AgreementTests.prepare
    submitted=fixtures.AgreementTests.submitted
    decision=fixtures.AgreementTests.decision
    selected=fixtures.AgreementTests.selected
    ready=fixtures.AgreementTests.ready
    completion=fixtures.AgreementTests.completion
    verified=fixtures.AgreementTests.verified
    def open(self):
        self.evidence=self.verified()
        return create_or_sync(self.teacher,self.project.pk,confirmation(self.teacher,self.project))
    def test_create_retry_members_and_private_pages(self):
        c=self.open()
        create_or_sync(self.teacher,self.project.pk,'already-created-retry')
        self.assertEqual(Community.objects.count(),1);self.assertEqual(Membership.objects.count(),2)
        self.assertEqual(CommunityEvent.objects.count(),1);self.assertIsNone(c.leader)
        self.assertTrue(can_enter(self.student,self.project));self.assertTrue(can_view_confidential(self.student,self.project))
        self.client.force_login(self.student)
        self.assertContains(self.client.get(reverse('communities:detail',args=[c.pk])),'Internal Chat')
        for section in ['summary','chat','todo','announcements','ip']:
            self.assertEqual(self.client.get(reverse('communities:section',args=[c.pk,section])).status_code,200)
        self.assertContains(self.client.get(reverse('communities:section',args=[c.pk,'summary'])),'PRIVATE-SENTINEL')
        self.client.force_login(self.other)
        for name,args in [('detail',[c.pk]),('section',[c.pk,'summary'])]:self.assertEqual(self.client.get(reverse('communities:'+name,args=args)).status_code,404)
    def test_missing_and_stale_roster_block_creation(self):
        self.ready()
        with self.assertRaises(ValidationError):create_or_sync(self.teacher,self.project.pk,confirmation(self.teacher,self.project))
        from apps.agreements.services import submit
        e=submit(self.student,self.project.pk,self.completion());review(self.teacher,e.pk,'verified','Reviewed',uuid.uuid4(),'')
        token=confirmation(self.teacher,self.project)
        Application.objects.create(project=self.project,applicant=self.other,status='selected',uploaded_resume='fixture.pdf',resume_name='fixture.pdf')
        with self.assertRaises(ValidationError):create_or_sync(self.teacher,self.project.pk,token)
        with self.assertRaises(ValidationError):create_or_sync(self.teacher,self.project.pk,confirmation(self.teacher,self.project))
        self.assertFalse(Community.objects.exists())
    def test_mentor_only_and_project_scoped_leader(self):
        c=self.open()
        with self.assertRaises(Http404):appoint_leader(self.student,c.pk,self.student.pk,c.revision,uuid.uuid4())
        with self.assertRaises(ValidationError):appoint_leader(self.teacher,c.pk,self.other.pk,c.revision,uuid.uuid4())
        key=uuid.uuid4();appoint_leader(self.teacher,c.pk,self.student.pk,c.revision,key)
        appoint_leader(self.teacher,c.pk,self.student.pk,c.revision,key)
        self.assertTrue(can_edit(self.student,self.project))
        self.assertEqual(CommunityEvent.objects.filter(action='leader_appointed').count(),1)
        other_project=self.create(self.teacher)
        self.assertFalse(can_edit(self.student,other_project))
    def test_correction_revokes_access_and_leader_privileges(self):
        c=self.open();appoint_leader(self.teacher,c.pk,self.student.pk,c.revision,uuid.uuid4())
        review(self.teacher,self.evidence.pk,'correction','A corrected signature is required.',uuid.uuid4(),str(self.evidence.review.pk))
        self.assertFalse(can_enter(self.student,self.project));self.assertFalse(can_edit(self.student,self.project))
        self.assertFalse(can_view_confidential(self.student,self.project))
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse('projects:private',args=[self.project.pk])).status_code,404)
        self.assertEqual(self.client.get(reverse('communities:section',args=[c.pk,'chat'])).status_code,404)
    def test_creation_get_and_csrf_and_unauthorised_post(self):
        self.verified();url=reverse('communities:create',args=[self.project.pk])
        self.client.force_login(self.teacher)
        self.assertContains(self.client.get(url),'Create Private Project Community');self.assertFalse(Community.objects.exists())
        from django.test import Client
        client=Client(enforce_csrf_checks=True);client.force_login(self.teacher)
        self.assertEqual(client.post(url,{}).status_code,403)
        self.client.force_login(self.student)
        self.assertEqual(self.client.post(url,{}).status_code,404)

    def test_member_project_list_and_document_controls(self):
        c=self.open();self.client.force_login(self.student)
        self.assertContains(self.client.get('/projects/'),self.project.title)
        response=self.client.get(reverse('projects:private',args=[self.project.pk]))
        self.assertEqual(response.status_code,200)
        self.assertNotContains(response,'Upload document');self.assertNotContains(response,'Edit notes')
        self.assertEqual(self.client.get(reverse('documents:upload',args=[self.project.pk])).status_code,404)
        self.assertNotContains(self.client.get('/projects/?view=created'),self.project.title)
