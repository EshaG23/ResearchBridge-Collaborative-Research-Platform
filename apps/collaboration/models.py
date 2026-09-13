import uuid
from django.conf import settings
from django.db import models

class ChatMessage(models.Model):
    community=models.ForeignKey('communities.Community',on_delete=models.PROTECT,related_name='chat_messages')
    sender=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    sender_name=models.CharField(max_length=120)
    text=models.TextField(max_length=10000,blank=True)
    reply_to=models.ForeignKey('self',on_delete=models.PROTECT,null=True,blank=True)
    request_key=models.UUIDField()
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['pk']
        constraints=[models.UniqueConstraint(fields=['community','sender','request_key'],name='unique_chat_send')]
        indexes=[models.Index(fields=['community','id'],name='chat_community_cursor')]

def attachment_path(instance,filename):
    return f'chat/{instance.message.community_id}/{instance.pk}/{filename}'

class ChatAttachment(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    message=models.ForeignKey(ChatMessage,on_delete=models.PROTECT,related_name='attachments')
    file=models.FileField(upload_to=attachment_path,max_length=255)
    filename=models.CharField(max_length=255)
    kind=models.CharField(max_length=12)
    mime=models.CharField(max_length=120)
    size=models.PositiveIntegerField()
    sha256=models.CharField(max_length=64)

class Poll(models.Model):
    revision=models.PositiveIntegerField(default=1)
    message=models.OneToOneField(ChatMessage,on_delete=models.PROTECT,related_name='poll')
    question=models.CharField(max_length=300)
    closed=models.BooleanField(default=False)

class PollOption(models.Model):
    poll=models.ForeignKey(Poll,on_delete=models.PROTECT,related_name='options')
    text=models.CharField(max_length=160)
    order=models.PositiveSmallIntegerField()
    class Meta:
        ordering=['order','pk']

class PollVote(models.Model):
    poll=models.ForeignKey(Poll,on_delete=models.PROTECT,related_name='votes')
    voter=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    option=models.ForeignKey(PollOption,on_delete=models.PROTECT,related_name='votes')
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['poll','voter'],name='one_vote_per_poll_member')]

class Announcement(models.Model):
    community=models.ForeignKey('communities.Community',on_delete=models.PROTECT,related_name='announcements')
    author=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    title=models.CharField(max_length=160)
    message=models.TextField(max_length=10000)
    revision=models.PositiveIntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        ordering=['-created_at','-pk']

class AnnouncementRevision(models.Model):
    announcement=models.ForeignKey(Announcement,on_delete=models.PROTECT,related_name='history')
    actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    title=models.CharField(max_length=160)
    message=models.TextField()
    request_key=models.UUIDField(unique=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-pk']

class ChatReadState(models.Model):
    community=models.ForeignKey('communities.Community',on_delete=models.PROTECT,related_name='chat_read_states')
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    last_message_id=models.PositiveBigIntegerField(default=0)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['community','user'],name='unique_chat_read_state')]
