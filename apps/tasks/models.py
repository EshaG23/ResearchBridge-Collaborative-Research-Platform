import uuid
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

class Immutable(models.Model):
    class Meta: abstract=True
    def save(self,*args,**kwargs):
        if not self._state.adding:raise ValidationError('History and uploaded versions cannot be overwritten.')
        return super().save(*args,**kwargs)

class Task(models.Model):
    STATES=[('assigned','Assigned'),('progress','In progress'),('submitted','Awaiting review'),('changes','Changes requested'),('approved','Approved')]
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    community=models.ForeignKey('communities.Community',on_delete=models.PROTECT,related_name='tasks')
    sprint=models.ForeignKey('communities.Sprint',on_delete=models.PROTECT,related_name='tasks',null=True,blank=True)
    title=models.CharField(max_length=160)
    description=models.TextField(max_length=10000)
    milestone=models.CharField(max_length=200,blank=True)
    assignee=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='research_tasks')
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='+')
    due_date=models.DateField(null=True,blank=True)
    status=models.CharField(max_length=12,choices=STATES,default='assigned')
    progress_notes=models.TextField(max_length=10000,blank=True)
    blocker=models.TextField(max_length=3000,blank=True)
    revision=models.PositiveIntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=['-created_at','pk']

class TaskFile(Immutable):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    task=models.ForeignKey(Task,on_delete=models.PROTECT,related_name='files')
    uploader=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    file=models.FileField(upload_to='task-files/%Y/%m/',max_length=255)
    filename=models.CharField(max_length=255)
    mime=models.CharField(max_length=120)
    sha256=models.CharField(max_length=64)
    size=models.PositiveIntegerField()
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created_at','pk']

class Submission(Immutable):
    task=models.ForeignKey(Task,on_delete=models.PROTECT,related_name='submissions')
    submitter=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    number=models.PositiveIntegerField()
    summary=models.TextField(max_length=10000)
    files=models.ManyToManyField(TaskFile,related_name='submissions',blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-number']
        constraints=[models.UniqueConstraint(fields=['task','number'],name='task_submission_number')]

class Review(Immutable):
    submission=models.OneToOneField(Submission,on_delete=models.PROTECT,related_name='review')
    reviewer=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    decision=models.CharField(max_length=10,choices=[('approved','Approve'),('changes','Request changes')])
    feedback=models.TextField(max_length=10000)
    created_at=models.DateTimeField(auto_now_add=True)

class TaskComment(Immutable):
    task=models.ForeignKey(Task,on_delete=models.PROTECT,related_name='comments')
    author=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    file=models.ForeignKey(TaskFile,on_delete=models.PROTECT,null=True,blank=True,related_name='comments')
    body=models.TextField(max_length=5000)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['created_at','pk']
