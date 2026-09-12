import uuid
from datetime import date
from io import BytesIO
from zipfile import ZipFile
from unittest.mock import patch
from pathlib import Path
from django.test import TestCase,override_settings,Client
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404
from django.db import DatabaseError
from django.urls import reverse
from . import tests as fixtures
from .models import ProjectSummary,SummaryResource,CommunityEvent
from .services import appoint_leader
from .summary_services import save_text,save_resource,validate_resource

@override_settings(DEBUG=True,AUTHENTICATION_MODE='demo',PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class SummarySprintTests(TestCase):
    setUp=fixtures.CommunityTests.setUp
    user=fixtures.CommunityTests.user
    data=fixtures.CommunityTests.data
    create=fixtures.CommunityTests.create
    pdf=fixtures.CommunityTests.pdf
    prepare=fixtures.CommunityTests.prepare
    submitted=fixtures.CommunityTests.submitted
    decision=fixtures.CommunityTests.decision
    selected=fixtures.CommunityTests.selected
    ready=fixtures.CommunityTests.ready
    completion=fixtures.CommunityTests.completion
    verified=fixtures.CommunityTests.verified
    open=fixtures.CommunityTests.open
    def meta(self,c):
        c.refresh_from_db();return {'key':uuid.uuid4(),'revision':c.revision}
    def summary_data(self,c):
        return self.meta(c)|dict(description='Private research context',problem='Research question',objectives='Measure effectiveness',existing_solutions='Prior work',research_gap='Unknown accuracy',progress_notes='Early research stage')
    def sprint_data(self,c,**changes):
        return self.meta(c)|dict(title='Research sprint',goal='Study prior work',order=1,start_date=None,end_date=None,status='planned',notes='')|changes
    def resource_data(self,c,**changes):
        return self.meta(c)|dict(title='Research reference',category='paper',url='https://example.org/paper',file=None)|changes

    def test_summary_edit_leader_readonly_member_and_history(self):
        c=self.open();data=self.summary_data(c)
        with self.assertRaises(Http404):save_text(self.student,c.pk,data,'summary')
        appoint_leader(self.teacher,c.pk,self.student.pk,c.revision,uuid.uuid4())
        data=self.summary_data(c);save_text(self.student,c.pk,data,'summary');save_text(self.student,c.pk,data,'summary')
        self.assertEqual(ProjectSummary.objects.count(),1)
        self.assertEqual(CommunityEvent.objects.filter(action='summary_saved').count(),1)
        save_text(self.teacher,c.pk,self.summary_data(c)|{'problem':'Revised question'},'summary')
        event=CommunityEvent.objects.filter(action='summary_saved').latest('created_at')
        self.assertEqual(event.details['before']['problem'],'Research question')
        self.assertEqual(event.details['after']['problem'],'Revised question')
        self.client.force_login(self.student)
        self.assertContains(self.client.get(reverse('communities:summary',args=[c.pk])),'Revised question')
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse('communities:summary',args=[c.pk])).status_code,404)

    def test_stale_summary_and_section_reorder(self):
        c=self.open();stale=self.summary_data(c);save_text(self.teacher,c.pk,self.summary_data(c),'summary')
        with self.assertRaises(ValidationError):save_text(self.teacher,c.pk,stale,'summary')
        a=save_text(self.teacher,c.pk,self.meta(c)|{'title':'A','content':'First','order':2},'section')
        save_text(self.teacher,c.pk,self.meta(c)|{'title':'B','content':'Second','order':1},'section')
        self.assertEqual(list(c.summary_sections.values_list('title',flat=True)),['B','A'])
        save_text(self.teacher,c.pk,self.meta(c)|{'title':'A','content':'Revised','order':0},'section',a)
        self.assertEqual(list(c.summary_sections.values_list('title',flat=True)),['A','B'])
        with self.assertRaises(Http404):save_text(self.teacher,c.pk,self.meta(c)|{'title':'Missing','content':'x','order':1},'section',99999)

    def test_sprint_states_single_current_and_real_progress(self):
        c=self.open();a=save_text(self.teacher,c.pk,self.sprint_data(c,status='active'),'sprint')
        with self.assertRaises(ValidationError):save_text(self.teacher,c.pk,self.sprint_data(c,status='active'),'sprint')
        save_text(self.teacher,c.pk,self.sprint_data(c,status='completed'),'sprint',a)
        save_text(self.teacher,c.pk,self.sprint_data(c,status='active',title='Build prototype',order=2),'sprint')
        self.client.force_login(self.student)
        response=self.client.get(reverse('communities:sprints',args=[c.pk]))
        self.assertEqual(response.context['sprint_done'],1);self.assertEqual(response.context['sprint_total'],2)
        self.assertEqual(response.context['sprint_percent'],50)
        self.assertNotContains(response,'Plan a sprint')
        with self.assertRaises(ValidationError):save_text(self.teacher,c.pk,self.sprint_data(c,start_date=date(2026,9,20),end_date=date(2026,9,19)),'sprint')

    def test_forms_actual_post_and_private_get_no_write(self):
        c=self.open();self.client.force_login(self.teacher)
        url=reverse('communities:edit',args=[c.pk,'summary'])
        self.assertContains(self.client.get(url),'PRIVATE-SENTINEL');self.assertFalse(ProjectSummary.objects.exists())
        response=self.client.post(url,self.summary_data(c));self.assertEqual(response.status_code,302)
        url=reverse('communities:edit',args=[c.pk,'sprint'])
        response=self.client.post(url,self.sprint_data(c,start_date='2026-09-10',end_date='2026-09-05'))
        self.assertContains(response,'End date cannot be before start date')
        response=self.client.post(url,self.sprint_data(c,start_date='',end_date=''));self.assertEqual(response.status_code,302)
        client=Client(enforce_csrf_checks=True);client.force_login(self.teacher)
        self.assertEqual(client.post(url,{}).status_code,403)

    def test_private_resources_retries_links_and_uploads(self):
        c=self.open();data=self.resource_data(c,url='',file=self.pdf('paper.pdf'))
        pk=save_resource(self.teacher,c.pk,data);save_resource(self.teacher,c.pk,data)
        self.assertEqual(SummaryResource.objects.count(),1)
        url=reverse('communities:resource-download',args=[c.pk,pk])
        self.client.force_login(self.student);response=self.client.get(url)
        self.assertEqual(response.status_code,200);self.assertIn('no-store',response['Cache-Control']);response.close()
        self.client.force_login(self.other);self.assertEqual(self.client.get(url).status_code,404)
        from .summary_forms import ResourceForm
        self.assertFalse(ResourceForm(self.resource_data(c,url='http://example.org')).is_valid())
        self.assertFalse(ResourceForm(self.resource_data(c),{'file':self.pdf()}).is_valid())
        with self.assertRaises(Http404):save_resource(self.student,c.pk,self.resource_data(c))

    def test_pptx_validation_and_database_failure_cleanup(self):
        out=BytesIO()
        with ZipFile(out,'w') as z:
            z.writestr('[Content_Types].xml','<Types/>');z.writestr('ppt/presentation.xml','<presentation/>')
        file=SimpleUploadedFile('slides.pptx',out.getvalue())
        self.assertIn('presentationml',validate_resource(file))
        with self.assertRaises(ValidationError):validate_resource(SimpleUploadedFile('broken.pptx',b'fake'))
        c=self.open()
        with patch('apps.communities.summary_services.record_edit',side_effect=DatabaseError):
            with self.assertRaises(DatabaseError):save_resource(self.teacher,c.pk,self.resource_data(c,url='',file=self.pdf()))
        self.assertFalse(SummaryResource.objects.exists())
        from django.conf import settings
        self.assertEqual(list((Path(settings.MEDIA_ROOT)/'community-resources').rglob('*.pdf')),[])

    def test_revoked_agreement_removes_summary_edit_and_file_access(self):
        c=self.open();appoint_leader(self.teacher,c.pk,self.student.pk,c.revision,uuid.uuid4())
        pk=save_resource(self.student,c.pk,self.resource_data(c,url='',file=self.pdf()))
        from apps.agreements.services import review
        review(self.teacher,self.evidence.pk,'correction','New signature needed',uuid.uuid4(),str(self.evidence.review.pk))
        with self.assertRaises(Http404):save_text(self.student,c.pk,self.summary_data(c),'summary')
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse('communities:resource-download',args=[c.pk,pk])).status_code,404)
