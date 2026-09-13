import uuid
from django.conf import settings
from django.db import models
from apps.tasks.models import Immutable

class Completion(models.Model):
    community=models.OneToOneField('communities.Community',on_delete=models.PROTECT,related_name='completion')
    state=models.CharField(max_length=12,default='active',choices=[('active','Active research'),('requested','Completion requested'),('completed','Completed')])
    note=models.TextField(max_length=10000,blank=True)
    confirmed_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True,related_name='+')
    completed_at=models.DateTimeField(null=True,blank=True)
    revision=models.PositiveIntegerField(default=1)

class IPUpdate(Immutable):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    community=models.ForeignKey('communities.Community',on_delete=models.PROTECT,related_name='ip_updates')
    author=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    author_name=models.CharField(max_length=120)
    title=models.CharField(max_length=160)
    status_label=models.CharField(max_length=100)
    message=models.TextField(max_length=10000)
    required_information=models.TextField(max_length=5000,blank=True)
    reference=models.CharField(max_length=200,blank=True)
    task=models.ForeignKey('tasks.Task',on_delete=models.PROTECT,null=True,blank=True)
    file=models.FileField(upload_to='ip-updates/%Y/%m/',blank=True,max_length=255)
    filename=models.CharField(max_length=255,blank=True)
    mime=models.CharField(max_length=120,blank=True)
    sha256=models.CharField(max_length=64,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:ordering=['-created_at','pk']

class Achievement(models.Model):
    community=models.ForeignKey('communities.Community',on_delete=models.PROTECT,related_name='achievements')
    approved_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    title=models.CharField(max_length=160)
    status_label=models.CharField(max_length=100)
    public_summary=models.TextField(max_length=1000)
    milestone_date=models.DateField()
    visible=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:ordering=['-milestone_date','-pk']
