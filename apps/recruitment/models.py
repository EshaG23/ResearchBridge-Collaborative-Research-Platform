import uuid
from django.conf import settings
from django.db import models

def application_path(instance,filename):
    return f'applications/{instance.applicant_id}/{uuid.uuid4().hex}.pdf'

class Application(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    project=models.ForeignKey('projects.Project',on_delete=models.PROTECT,related_name='applications')
    applicant=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='applications')
    status=models.CharField(max_length=16,default='draft',choices=[('draft','Draft'),('submitted','Submitted')])
    profile_resume=models.ForeignKey('profiles.ResumeVersion',null=True,blank=True,on_delete=models.PROTECT)
    uploaded_resume=models.FileField(upload_to=application_path,blank=True)
    resume_name=models.CharField(max_length=255)
    snapshot=models.JSONField(default=dict)
    motivation=models.TextField(max_length=3000)
    academic_score=models.CharField(max_length=40,blank=True)
    revision=models.PositiveIntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)
    submitted_at=models.DateTimeField(null=True,blank=True)
    class Meta:
        ordering=['-created_at']
        constraints=[models.UniqueConstraint(fields=['project','applicant'],name='one_application_per_student'),
            models.CheckConstraint(condition=(models.Q(profile_resume__isnull=False,uploaded_resume='') |
                (models.Q(profile_resume__isnull=True) & ~models.Q(uploaded_resume=''))),name='application_one_resume_source')]
    @property
    def resume_file(self):
        return self.profile_resume.file if self.profile_resume_id else self.uploaded_resume
