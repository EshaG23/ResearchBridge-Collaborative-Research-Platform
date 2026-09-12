import hashlib
from io import BytesIO
from pathlib import Path
from unittest.mock import patch
from django.test import TestCase,override_settings,Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.http import Http404
from django.db import DatabaseError
from pypdf import PdfReader
from apps.notifications.models import Notification
from apps.core.permissions import can_view_confidential
from . import test_review as fixtures
from .models import OfferLetter
from .letter_services import preview_letter,issue_letter

@override_settings(DEBUG=True,AUTHENTICATION_MODE='demo',PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class OfferLetterTests(TestCase):
    setUp=fixtures.ApplicantReviewTests.setUp
    user=fixtures.ApplicantReviewTests.user
    data=fixtures.ApplicantReviewTests.data
    create=fixtures.ApplicantReviewTests.create
    pdf=fixtures.ApplicantReviewTests.pdf
    prepare=fixtures.ApplicantReviewTests.prepare
    submitted=fixtures.ApplicantReviewTests.submitted
    decision=fixtures.ApplicantReviewTests.decision

    def selected(self):
        self.submitted();self.decision('shortlist');self.app.refresh_from_db()
        self.decision('select');self.app.refresh_from_db()
        return preview_letter(self.teacher,self.app,'Research assistant')

    def test_issue_preserves_pdf_and_snapshot_and_notifies_once(self):
        snapshot,token=self.selected()
        letter=issue_letter(self.teacher,self.app.pk,token)
        retry=issue_letter(self.teacher,self.app.pk,token)
        self.assertEqual(letter.pk,retry.pk)
        self.assertEqual(OfferLetter.objects.count(),1)
        self.assertEqual(Notification.objects.filter(title='Your offer letter is ready').count(),1)
        content=Path(letter.pdf.path).read_bytes()
        self.assertEqual(hashlib.sha256(content).hexdigest(),letter.sha256)
        text=' '.join(p.extract_text() for p in PdfReader(BytesIO(content)).pages)
        for value in (snapshot['student'],snapshot['project'],snapshot['role'],snapshot['mentor'],snapshot['reference']):
            self.assertIn(value,text)
        self.app.project.title='Changed after issue';self.app.project.save()
        self.teacher.profile.name='Changed mentor';self.teacher.profile.save()
        letter.refresh_from_db()
        self.assertEqual(letter.snapshot,snapshot)
        self.assertEqual(Path(letter.pdf.path).read_bytes(),content)
        with self.assertRaises(ValidationError):letter.save()
        self.assertFalse(can_view_confidential(self.student,self.app.project))

    def test_only_selected_and_current_mentor_can_issue(self):
        self.submitted()
        with self.assertRaises(Http404):preview_letter(self.teacher,self.app,'Research assistant')
        self.decision('shortlist');self.app.refresh_from_db()
        with self.assertRaises(Http404):preview_letter(self.teacher,self.app,'Research assistant')
        self.decision('select');self.app.refresh_from_db()
        _,token=preview_letter(self.teacher,self.app,'Research assistant')
        for user in (self.student,self.other):
            with self.assertRaises(Http404):issue_letter(user,self.app.pk,token)
        self.assertEqual(OfferLetter.objects.count(),0)

    def test_preview_confirm_download_and_access_matrix(self):
        self.selected();self.client.force_login(self.teacher)
        url=reverse('recruitment:issue-letter',args=[self.app.pk])
        response=self.client.post(url,{'role':'Research assistant'})
        self.assertContains(response,'Review before issuing')
        self.assertEqual(OfferLetter.objects.count(),0)
        self.client.post(url,{'confirm':'issue','token':response.context['token']})
        letter=OfferLetter.objects.get()
        detail=reverse('recruitment:letter',args=[letter.pk]);download=reverse('recruitment:letter-download',args=[letter.pk])
        for user in (self.student,self.teacher):
            self.client.force_login(user)
            self.assertContains(self.client.get(detail),'Confidentiality agreement pending')
            response=self.client.get(download)
            self.assertEqual(response.status_code,200)
            self.assertIn('no-store',response['Cache-Control'])
            self.assertEqual(hashlib.sha256(b''.join(response.streaming_content)).hexdigest(),letter.sha256)
            response.close()
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(detail).status_code,404)
        self.assertEqual(self.client.get(download).status_code,404)
        self.app.project.creator=self.other;self.app.project.save()
        self.assertEqual(self.client.get(detail).status_code,404)
        self.client.logout();self.assertEqual(self.client.get(download).status_code,302)
        self.client.force_login(self.student)
        Path(letter.pdf.path).unlink();self.assertEqual(self.client.get(download).status_code,404)

    def test_stale_tampered_and_expired_previews(self):
        _,token=self.selected()
        with self.assertRaises(ValidationError):issue_letter(self.teacher,self.app.pk,token+'tampered')
        with patch('django.core.signing.time.time',return_value=99999999999):
            with self.assertRaises(ValidationError):issue_letter(self.teacher,self.app.pk,token)
        self.app.project.revision+=1;self.app.project.save()
        with self.assertRaises(ValidationError):issue_letter(self.teacher,self.app.pk,token)
        self.assertFalse(OfferLetter.objects.exists())

    def test_storage_cleanup_on_database_failure(self):
        _,token=self.selected()
        with patch('apps.recruitment.letter_services.notify',side_effect=DatabaseError('failure')):
            with self.assertRaises(DatabaseError):issue_letter(self.teacher,self.app.pk,token)
        self.assertFalse(OfferLetter.objects.exists())
        from django.conf import settings
        self.assertEqual(list((Path(settings.MEDIA_ROOT)/'letters').rglob('*.pdf')),[])
        self.assertEqual(Notification.objects.filter(title='Your offer letter is ready').count(),0)
        issue_letter(self.teacher,self.app.pk,token)

    def test_csrf_and_readonly_get(self):
        self.selected()
        client=Client(enforce_csrf_checks=True);client.force_login(self.teacher)
        url=reverse('recruitment:issue-letter',args=[self.app.pk])
        self.assertEqual(client.get(url).status_code,200)
        self.assertFalse(OfferLetter.objects.exists())
        self.assertEqual(client.post(url,{'role':'Research assistant'}).status_code,403)

    def test_styled_copy_preserves_original_and_is_private(self):
        snapshot,token=self.selected()
        letter=issue_letter(self.teacher,self.app.pk,token)
        original=Path(letter.pdf.path).read_bytes()
        url=reverse('recruitment:letter-download',args=[letter.pk])+'?design=studio'
        self.client.force_login(self.student)
        response=self.client.get(url)
        self.assertEqual(response.status_code,200)
        self.assertIn('no-store',response['Cache-Control'])
        data=b''.join(response.streaming_content);response.close()
        text=' '.join(p.extract_text() for p in PdfReader(BytesIO(data)).pages)
        for key in ('student','project','role','mentor','reference','date'):
            self.assertIn(snapshot[key],text)
        self.assertEqual(Path(letter.pdf.path).read_bytes(),original)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(url).status_code,404)
