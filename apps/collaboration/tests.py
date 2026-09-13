import uuid
from io import BytesIO
from unittest.mock import patch
from pathlib import Path
import wave
from PIL import Image
from django.test import TestCase,override_settings,Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.http import Http404
from django.db import DatabaseError
from django.urls import reverse
from apps.communities import tests as fixtures
from apps.communities.services import appoint_leader
from apps.notifications.models import Notification
from .models import ChatMessage,ChatAttachment,PollVote,AnnouncementRevision
from .services import send,vote,close_poll,announce

@override_settings(DEBUG=True,AUTHENTICATION_MODE='demo',PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class ChatTests(TestCase):
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
    def photo(self):
        out=BytesIO();Image.new('RGB',(20,20),'green').save(out,'PNG');return SimpleUploadedFile('photo.png',out.getvalue(),content_type='image/png')
    def audio(self):
        out=BytesIO()
        with wave.open(out,'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(8000);f.writeframes(b'\0\0'*800)
        return SimpleUploadedFile('note.wav',out.getvalue(),content_type='audio/wav')
    def test_all_members_send_reply_retry_and_persist(self):
        c=self.open();key=uuid.uuid4()
        m=send(self.student,c.pk,key,'Student message https://example.org')
        send(self.student,c.pk,key,'retry');send(self.teacher,c.pk,uuid.uuid4(),'Mentor reply',reply=m.pk)
        self.assertEqual(ChatMessage.objects.count(),2)
        self.client.force_login(self.student)
        self.assertContains(self.client.get(reverse('collaboration:chat',args=[c.pk])),'Mentor reply')
        self.client.logout();self.client.force_login(self.teacher)
        self.assertContains(self.client.get(reverse('collaboration:chat',args=[c.pk])),'Student message')
        with self.assertRaises(Http404):send(self.other,c.pk,uuid.uuid4(),'outsider')
        c2=self.create(self.teacher)
        with self.assertRaises(Http404):send(self.student,c.pk,uuid.uuid4(),'reply',reply=999999)
    def test_feed_order_pagination_and_send_endpoint(self):
        c=self.open();self.client.force_login(self.student)
        ChatMessage.objects.bulk_create([ChatMessage(community=c,sender=self.teacher,sender_name='teacher',request_key=uuid.uuid4(),text=str(i)) for i in range(85)])
        response=self.client.get(reverse('collaboration:feed',args=[c.pk]),{'after':0}).json()
        self.assertEqual(len(response['messages']),40)
        ids=[m['id'] for m in response['messages']];self.assertEqual(ids,sorted(ids))
        nextpage=self.client.get(reverse('collaboration:feed',args=[c.pk]),{'after':ids[-1]}).json()
        self.assertTrue(all(m['id']>ids[-1] for m in nextpage['messages']))
        old=self.client.get(reverse('collaboration:feed',args=[c.pk]),{'before':ids[-1]}).json()
        self.assertTrue(all(m['id']<ids[-1] for m in old['messages']))
        response=self.client.post(reverse('collaboration:send',args=[c.pk]),{'key':uuid.uuid4(),'text':'Sent through HTTP'})
        self.assertEqual(response.status_code,200)
        self.assertIn('Sent through HTTP',response.json()['html'])
    def test_poll_vote_change_close_and_cross_poll_rejection(self):
        c=self.open();m=send(self.student,c.pk,uuid.uuid4(),question='Meeting day?',options=['Monday','Tuesday'])
        a,b=list(m.poll.options.all());vote(self.student,c.pk,m.poll.pk,a.pk);vote(self.student,c.pk,m.poll.pk,a.pk)
        vote(self.student,c.pk,m.poll.pk,b.pk);vote(self.teacher,c.pk,m.poll.pk,a.pk)
        self.assertEqual(PollVote.objects.count(),2);self.assertEqual(b.votes.count(),1)
        other=send(self.teacher,c.pk,uuid.uuid4(),question='Time?',options=['AM','PM'])
        with self.assertRaises(Http404):vote(self.student,c.pk,m.poll.pk,other.poll.options.first().pk)
        self.client.force_login(self.student)
        response=self.client.get(reverse('collaboration:feed',args=[c.pk]),{'polls':m.poll.pk}).json()
        self.assertIn(str(m.poll.pk),response['polls'])
        close_poll(self.student,c.pk,m.poll.pk)
        with self.assertRaises(ValidationError):vote(self.teacher,c.pk,m.poll.pk,a.pk)
    def test_attachments_media_library_and_byte_ranges(self):
        c=self.open();m=send(self.student,c.pk,uuid.uuid4(),'Media',files=[self.photo(),self.pdf(),self.audio()])
        self.assertEqual(m.attachments.count(),3)
        self.client.force_login(self.teacher)
        media=self.client.get(reverse('collaboration:media',args=[c.pk]),{'kind':'audio','q':'note'})
        self.assertContains(media,'note.wav');self.assertNotContains(media,'photo.png')
        a=m.attachments.get(kind='audio');url=reverse('collaboration:attachment',args=[c.pk,a.pk])
        r=self.client.get(url,HTTP_RANGE='bytes=0-9');self.assertEqual(r.status_code,206)
        self.assertEqual(len(b''.join(r.streaming_content)),10);r.close()
        self.assertIn('no-store',r['Cache-Control'])
        r=self.client.head(url);self.assertEqual(int(r['Content-Length']),a.size)
        self.assertEqual(self.client.get(url,HTTP_RANGE='bytes=999999-').status_code,416)
        self.client.force_login(self.other);self.assertEqual(self.client.get(url).status_code,404)
        self.assertEqual(self.client.get(reverse('collaboration:media',args=[c.pk])).status_code,404)
    def test_failed_file_transaction_cleans_storage(self):
        c=self.open()
        with patch('apps.collaboration.models.ChatAttachment.save',side_effect=DatabaseError):
            with self.assertRaises(DatabaseError):send(self.student,c.pk,uuid.uuid4(),files=[self.photo()])
        self.assertFalse(ChatMessage.objects.exists());self.assertFalse(ChatAttachment.objects.exists())
        from django.conf import settings
        self.assertEqual(list((Path(settings.MEDIA_ROOT)/'chat').rglob('*.png')),[])
    def test_validation_csrf_and_escaped_message(self):
        c=self.open()
        with self.assertRaises(ValidationError):send(self.student,c.pk,uuid.uuid4())
        with self.assertRaises(ValidationError):send(self.student,c.pk,uuid.uuid4(),files=[SimpleUploadedFile('fake.png',b'bad')])
        with self.assertRaises(ValidationError):send(self.student,c.pk,uuid.uuid4(),question='Choices',options=['Same','same'])
        self.client.force_login(self.student)
        response=self.client.post(reverse('collaboration:send',args=[c.pk]),{'key':uuid.uuid4(),'text':'<b>literal markup</b>'})
        self.assertIn('&lt;b&gt;',response.json()['html'])
        client=Client(enforce_csrf_checks=True);client.force_login(self.student)
        self.assertEqual(client.post(reverse('collaboration:send',args=[c.pk]),{}).status_code,403)
    def test_announcement_permissions_edits_history_and_notifications(self):
        c=self.open()
        with self.assertRaises(Http404):announce(self.student,c.pk,uuid.uuid4(),'Title','Message')
        appoint_leader(self.teacher,c.pk,self.student.pk,c.revision,uuid.uuid4())
        key=uuid.uuid4();a=announce(self.student,c.pk,key,'Weekly update','Read this update')
        announce(self.student,c.pk,key,'Weekly update','Read this update')
        self.assertEqual(AnnouncementRevision.objects.count(),1)
        announce(self.teacher,c.pk,uuid.uuid4(),'Updated title','Corrected message',a.pk,a.revision)
        with self.assertRaises(ValidationError):announce(self.teacher,c.pk,uuid.uuid4(),'Stale','old',a.pk,1)
        self.assertEqual(AnnouncementRevision.objects.count(),2)
        self.assertTrue(Notification.objects.filter(title='New project announcement').exists())
        self.client.force_login(self.student)
        self.assertContains(self.client.get(reverse('collaboration:announcements',args=[c.pk])),'Corrected message')
    def test_agreement_revocation_denies_every_chat_operation(self):
        c=self.open();m=send(self.student,c.pk,uuid.uuid4(),files=[self.photo()],question='Poll',options=['A','B'])
        from apps.agreements.services import review
        review(self.teacher,self.evidence.pk,'correction','Correction required',uuid.uuid4(),str(self.evidence.review.pk))
        with self.assertRaises(Http404):send(self.student,c.pk,uuid.uuid4(),'denied')
        with self.assertRaises(Http404):vote(self.student,c.pk,m.poll.pk,m.poll.options.first().pk)
        self.client.force_login(self.student)
        for name,args in [('feed',[c.pk]),('chat',[c.pk]),('media',[c.pk]),('attachment',[c.pk,m.attachments.first().pk]),('announcements',[c.pk])]:
            self.assertEqual(self.client.get(reverse('collaboration:'+name,args=args)).status_code,404)
