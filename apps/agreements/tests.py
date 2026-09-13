import uuid
from io import BytesIO
from pathlib import Path
from unittest.mock import patch
from django.test import TestCase,Client,override_settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import DatabaseError
from django.http import Http404
from django.urls import reverse
from pypdf import PdfReader
from PIL import Image
from apps.recruitment import test_letters as fixtures
from apps.recruitment.letter_services import issue_letter
from apps.notifications.models import Notification
from apps.core.permissions import can_view_confidential
from .models import Agreement,AgreementEvidence,AgreementReview
from .services import context,preview,submit,review,enroll_proposer,physical_pdf
from .permissions import agreement_gate
from .forms import SigningForm

@override_settings(DEBUG=True,AUTHENTICATION_MODE='demo',PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class AgreementTests(TestCase):
    setUp=fixtures.OfferLetterTests.setUp
    user=fixtures.OfferLetterTests.user
    data=fixtures.OfferLetterTests.data
    create=fixtures.OfferLetterTests.create
    pdf=fixtures.OfferLetterTests.pdf
    prepare=fixtures.OfferLetterTests.prepare
    submitted=fixtures.OfferLetterTests.submitted
    decision=fixtures.OfferLetterTests.decision
    selected=fixtures.OfferLetterTests.selected
    def ready(self):
        _,token=self.selected();issue_letter(self.teacher,self.app.pk,token)
        self.client.force_login(self.student)
    def completion(self,method='typed'):
        _,token=context(self.student,self.project)
        data={'name':self.student.profile.name,'method':method,'signature':[[[.1,.5],[.2,.2],[.3,.6],[.4,.2],[.6,.5]]],'consent':True}
        _,token=preview(token,self.student,self.project,data)
        return token
    def verified(self):
        self.ready();e=submit(self.student,self.project.pk,self.completion())
        review(self.teacher,e.pk,'verified','Reviewed identity, terms and signature.',uuid.uuid4(),'')
        return e

    def test_electronic_preview_confirm_pdf_and_idempotency(self):
        self.ready();url=reverse('agreements:sign',args=[self.project.pk])
        response=self.client.get(url);self.assertEqual(response.status_code,200)
        token=response.context['form']['token'].value()
        response=self.client.post(url,{'method':'drawn','name':'student','signature':'[[[0.1,0.5],[0.2,0.2],[0.3,0.6],[0.4,0.2],[0.6,0.5]]]','consent':'on','password':'Testing!2026','token':token})
        self.assertContains(response,'Confirm signature &amp; submit')
        self.assertFalse(AgreementEvidence.objects.exists())
        token=response.context['confirmation']
        response=self.client.post(url,{'action':'confirm','token':token});self.assertEqual(response.status_code,302)
        evidence=AgreementEvidence.objects.get()
        self.client.post(url,{'action':'confirm','token':token})
        self.assertEqual(AgreementEvidence.objects.count(),1)
        self.assertEqual(evidence.status,'pending')
        text=' '.join(p.extract_text() for p in PdfReader(evidence.pdf.path).pages)
        for phrase in ['drawn','student','confidentiality','Account password confirmed']:self.assertIn(phrase,text)
        self.assertNotIn('Testing!2026',text)
        self.assertFalse(agreement_gate(self.project)['ready'])
        self.assertFalse(can_view_confidential(self.student,self.project))
        self.assertEqual(Notification.objects.filter(title='Agreement awaiting verification').count(),1)

    def test_verification_gate_and_correction_history(self):
        evidence=self.verified();self.assertTrue(agreement_gate(self.project)['ready'])
        key=uuid.uuid4();previous=str(evidence.review.pk)
        review(self.teacher,evidence.pk,'correction','Please use complete signature.',key,previous)
        review(self.teacher,evidence.pk,'correction','Please use complete signature.',key,previous)
        self.assertFalse(agreement_gate(self.project)['ready'])
        new=submit(self.student,self.project.pk,self.completion('drawn'))
        self.assertNotEqual(new.pk,evidence.pk)
        self.assertEqual(AgreementEvidence.objects.count(),2)
        self.assertTrue(Path(evidence.pdf.path).exists())
        with self.assertRaises(ValidationError):review(self.teacher,evidence.pk,'verified','old version',uuid.uuid4(),str(evidence.review.pk))
        review(self.teacher,new.pk,'verified','Corrected version inspected.',uuid.uuid4(),'')
        self.assertTrue(agreement_gate(self.project)['ready'])
        self.assertEqual(AgreementReview.objects.count(),3)
        with self.assertRaises(ValidationError):new.save()

    def test_selected_unsigned_student_blocks_gate(self):
        self.verified()
        # Another selected student is retained even without a letter or an agreement.
        from apps.recruitment.models import Application
        Application.objects.create(project=self.project,applicant=self.other,status='selected',uploaded_resume='existing.pdf',resume_name='existing.pdf')
        gate=agreement_gate(self.project)
        self.assertEqual(len(gate['rows']),2);self.assertFalse(gate['ready'])

    def test_access_controls_eligibility_and_revoked_mentor(self):
        self.submitted()
        with self.assertRaises(Http404):context(self.student,self.project)
        self.decision('shortlist');self.app.refresh_from_db()
        with self.assertRaises(Http404):context(self.student,self.project)
        self.decision('select');self.app.refresh_from_db()
        with self.assertRaises(Http404):context(self.student,self.project)
        from apps.recruitment.letter_services import preview_letter
        _,token=preview_letter(self.teacher,self.app,'Research assistant');issue_letter(self.teacher,self.app.pk,token)
        evidence=submit(self.student,self.project.pk,self.completion())
        for user,code in [(self.student,200),(self.teacher,200),(self.other,404)]:
            self.client.force_login(user)
            for name in ('evidence','download'):
                response=self.client.get(reverse('agreements:'+name,args=[evidence.pk]));self.assertEqual(response.status_code,code);response.close()
        self.project.creator=self.other;self.project.save()
        self.assertEqual(self.client.get(reverse('agreements:evidence',args=[evidence.pk])).status_code,404)
        with self.assertRaises(Http404):review(self.other,evidence.pk,'verified','unauthorised',uuid.uuid4(),'')
        self.project.mentor=self.user('replacement','teacher');self.project.save()
        with self.assertRaises(Http404):review(self.teacher,evidence.pk,'verified','revoked',uuid.uuid4(),'')

    def test_physical_pdf_and_image_require_verification(self):
        self.ready();evidence=submit(self.student,self.project.pk,self.completion('physical'),self.pdf())
        self.assertEqual(evidence.status,'pending');self.assertTrue(evidence.signed_copy)
        self.assertFalse(agreement_gate(self.project)['ready'])
        buf=BytesIO();Image.new('RGB',(100,100),'white').save(buf,'PNG')
        data=physical_pdf(SimpleUploadedFile('scan.png',buf.getvalue()))
        self.assertEqual(len(PdfReader(BytesIO(data)).pages),1)
        for upload in [SimpleUploadedFile('wrong.pdf',b'not pdf'),SimpleUploadedFile('wrong.png',b'not image'),SimpleUploadedFile('scan.html',b'<script>')]:
            with self.assertRaises(ValidationError):physical_pdf(upload)

    def test_wrong_password_tamper_expiry_name_and_stale_submission(self):
        self.ready();url=reverse('agreements:sign',args=[self.project.pk]);_,token=context(self.student,self.project)
        response=self.client.post(url,{'method':'typed','name':'student','password':'wrong','consent':'on','token':token})
        self.assertContains(response,'password is incorrect');self.assertFalse(AgreementEvidence.objects.exists())
        token=self.completion()
        with self.assertRaises(ValidationError):submit(self.student,self.project.pk,token+'x')
        with patch('django.core.signing.time.time',return_value=99999999999):
            with self.assertRaises(ValidationError):submit(self.student,self.project.pk,token)
        other=self.completion();submit(self.student,self.project.pk,token)
        with self.assertRaises(ValidationError):submit(self.student,self.project.pk,other)
        self.student.set_password('changed');self.student.save()
        with self.assertRaises(Http404):submit(self.student,self.project.pk,token)

    def test_blank_signature_validation_csrf_and_template_change(self):
        self.ready();_,token=context(self.student,self.project)
        form=SigningForm({'method':'drawn','name':'student','signature':'[]','password':'Testing!2026','consent':'on','token':token})
        self.assertFalse(form.is_valid());self.assertIn('signature',form.errors)
        client=Client(enforce_csrf_checks=True);client.force_login(self.student)
        self.assertEqual(client.post(reverse('agreements:sign',args=[self.project.pk]),{}).status_code,403)
        from .templates import SAMPLE
        token=self.completion()
        with patch('apps.agreements.services.current_template',return_value=SAMPLE|{'version':'new'}):
            with self.assertRaises(ValidationError):submit(self.student,self.project.pk,token)

    def test_failed_write_cleans_files_and_notifications(self):
        self.ready()
        with patch('apps.agreements.services.notify',side_effect=DatabaseError):
            with self.assertRaises(DatabaseError):submit(self.student,self.project.pk,self.completion('physical'),self.pdf())
        self.assertFalse(AgreementEvidence.objects.exists());self.assertFalse(Agreement.objects.exists())
        from django.conf import settings
        self.assertEqual(list((Path(settings.MEDIA_ROOT)/'agreements').rglob('*.pdf')),[])

    def test_missing_or_changed_evidence_cannot_be_verified(self):
        self.ready();e=submit(self.student,self.project.pk,self.completion())
        Path(e.pdf.path).write_bytes(b'changed')
        with self.assertRaises(ValidationError):review(self.teacher,e.pk,'verified','inspected',uuid.uuid4(),'')
        self.assertEqual(e.status,'pending')

    def test_student_proposer_requires_explicit_enrollment(self):
        self.project=self.create(self.student)
        self.project.mentor=self.teacher;self.project.status='recruiting';self.project.save()
        with self.assertRaises(Http404):context(self.student,self.project)
        enroll_proposer(self.teacher,self.project);enroll_proposer(self.teacher,self.project)
        self.assertEqual(Agreement.objects.count(),1)
        self.assertFalse(agreement_gate(self.project)['ready'])
        evidence=submit(self.student,self.project.pk,self.completion())
        review(self.teacher,evidence.pk,'verified','Proposer signed.',uuid.uuid4(),'')
        self.assertTrue(agreement_gate(self.project)['ready'])
    def test_physical_submission_and_verification_http_flow(self):
        self.ready();url=reverse('agreements:sign',args=[self.project.pk])
        token=self.client.get(url).context['form']['token'].value()
        response=self.client.post(url,{'method':'physical','name':'student','consent':'on','password':'Testing!2026','token':token,'signed_copy':self.pdf()})
        self.assertEqual(response.status_code,302)
        record=AgreementEvidence.objects.get()
        self.client.force_login(self.teacher)
        endpoint=reverse('agreements:verify',args=[record.pk])
        data={'request_key':str(uuid.uuid4()),'previous':'','action':'verified','reason':'All pages, identity, date and signature inspected.'}
        self.client.post(endpoint,data)
        self.assertEqual(record.status,'pending')
        self.client.post(endpoint,data|{'inspected':'yes'})
        self.assertEqual(record.status,'verified')
        self.assertTrue(agreement_gate(self.project)['ready'])
        response=self.client.get(reverse('agreements:download',args=[record.pk])+'?file=copy')
        self.assertEqual(response.status_code,200);response.close()


    def test_selected_student_sees_pending_agreement_then_signing(self):
        _,token=self.selected()
        self.client.force_login(self.student)
        page=self.client.get(reverse('recruitment:detail',args=[self.app.pk]))
        self.assertContains(page,'Confidentiality agreement &amp; status')
        url=reverse('agreements:project',args=[self.project.pk])
        self.assertContains(self.client.get(url),'Waiting for offer letter')
        self.assertEqual(self.client.get(reverse('agreements:sign',args=[self.project.pk])).status_code,404)
        issue_letter(self.teacher,self.app.pk,token)
        self.assertContains(self.client.get(url),'Read &amp; sign agreement')
