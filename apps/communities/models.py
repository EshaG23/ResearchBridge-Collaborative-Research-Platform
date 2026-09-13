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
    actor_name=models.CharField(max_length=120,blank=True)
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
        if not self.actor_name:self.actor_name=self.actor.profile.name
        return super().save(*args,**kwargs)

    @property
    def description(self):
        if self.action=='community_created':return 'Private community created'
        if self.action=='members_added':return 'New verified students admitted'
        if self.action=='leader_appointed':return 'Team leader appointed: '+self.details.get('leader_name','student #'+str(self.details.get('new_leader','')))
        return self.action.replace('_',' ').capitalize()

class ProjectSummary(models.Model):
    community=models.OneToOneField(Community,on_delete=models.PROTECT,related_name='summary')
    description=models.TextField(max_length=20000,blank=True)
    problem=models.TextField(max_length=10000,blank=True)
    objectives=models.TextField(max_length=10000,blank=True)
    existing_solutions=models.TextField(max_length=10000,blank=True)
    research_gap=models.TextField(max_length=10000,blank=True)
    progress_notes=models.TextField(max_length=10000,blank=True)

class SummarySection(models.Model):
    community=models.ForeignKey(Community,on_delete=models.PROTECT,related_name='summary_sections')
    title=models.CharField(max_length=160)
    content=models.TextField(max_length=20000)
    order=models.PositiveIntegerField(default=1)
    class Meta:
        ordering=['order','pk']

class Sprint(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    community=models.ForeignKey(Community,on_delete=models.PROTECT,related_name='sprints')
    title=models.CharField(max_length=160)
    goal=models.TextField(max_length=10000)
    order=models.PositiveIntegerField(default=1)
    start_date=models.DateField(null=True,blank=True)
    end_date=models.DateField(null=True,blank=True)
    status=models.CharField(max_length=10,choices=[('planned','Planned'),('active','Active'),('completed','Completed')],default='planned')
    notes=models.TextField(max_length=10000,blank=True)
    class Meta:
        ordering=['order','pk']
        constraints=[models.UniqueConstraint(fields=['community'],condition=models.Q(status='active'),name='one_active_sprint'),
            models.CheckConstraint(condition=models.Q(start_date__isnull=True)|models.Q(end_date__isnull=True)|models.Q(end_date__gte=models.F('start_date')),name='sprint_dates_ordered')]

def resource_path(instance,filename):
    return f'community-resources/{instance.community_id}/{instance.pk}/{filename}'

class SummaryResource(models.Model):
    replaces=models.OneToOneField('self',on_delete=models.PROTECT,null=True,blank=True,related_name='next_version')
    version=models.PositiveIntegerField(default=1)
    revision_note=models.CharField(max_length=1000,blank=True)
    uploader_name=models.CharField(max_length=120,blank=True)

    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    community=models.ForeignKey(Community,on_delete=models.PROTECT,related_name='resources')
    title=models.CharField(max_length=160)
    category=models.CharField(max_length=15,choices=[('presentation','Presentation'),('paper','Literature paper'),('reference','Reference')])
    url=models.URLField(max_length=500,blank=True)
    file=models.FileField(upload_to=resource_path,blank=True,max_length=255)
    filename=models.CharField(max_length=255,blank=True)
    mime_type=models.CharField(max_length=100,blank=True)
    sha256=models.CharField(max_length=64,blank=True)
    size=models.PositiveIntegerField(default=0)
    added_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-created_at','pk']
        constraints=[models.CheckConstraint(condition=(models.Q(url='') & ~models.Q(file=''))|(models.Q(file='') & ~models.Q(url='')),name='resource_one_source')]
    def save(self,*args,**kwargs):
        if not self._state.adding:
            from django.core.exceptions import ValidationError
            raise ValidationError('Resources are preserved. Add a revised resource instead.')
        return super().save(*args,**kwargs)
