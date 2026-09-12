import uuid
from django.conf import settings
from django.db import models

class Community(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    project=models.OneToOneField('projects.Project',on_delete=models.PROTECT,related_name='community')
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    created_at=models.DateTimeField(auto_now_add=True)
    leader=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True,related_name='+')
    revision=models.PositiveIntegerField(default=1)

class Membership(models.Model):
    community=models.ForeignKey(Community,on_delete=models.PROTECT,related_name='memberships')
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='community_memberships')
    role=models.CharField(max_length=10,choices=[('mentor','Mentor'),('student','Student')])
    admitted_evidence=models.ForeignKey('agreements.AgreementEvidence',on_delete=models.PROTECT,null=True,blank=True)
    joined_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['community','user'],name='unique_community_member')]

class CommunityEvent(models.Model):
    community=models.ForeignKey(Community,on_delete=models.PROTECT,related_name='events')
    actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    action=models.CharField(max_length=40)
    details=models.JSONField(default=dict)
    request_key=models.UUIDField(unique=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-created_at','-pk']
    def save(self,*args,**kwargs):
        if not self._state.adding:
            from django.core.exceptions import ValidationError
            raise ValidationError('Community history is immutable.')
        return super().save(*args,**kwargs)

    @property
    def description(self):
        if self.action=='community_created':return 'Private community created'
        if self.action=='members_added':return 'New verified students admitted'
        if self.action=='leader_appointed':return 'Team leader appointed: '+self.details.get('leader_name','student #'+str(self.details.get('new_leader','')))
        return self.action.replace('_',' ').capitalize()
