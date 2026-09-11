import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

def document_path(instance, filename):
    return f'projects/{instance.document.project_id}/{uuid.uuid4().hex}.pdf'

class ProjectDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project',on_delete=models.PROTECT,related_name='documents')
    title = models.CharField(max_length=160)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']

class DocumentVersion(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    document = models.ForeignKey(ProjectDocument,on_delete=models.PROTECT,related_name='versions')
    version = models.PositiveIntegerField()
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    file = models.FileField(upload_to=document_path)
    original_name = models.CharField(max_length=255)
    size = models.PositiveIntegerField()
    sha256 = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-version']
        constraints = [models.UniqueConstraint(fields=['document','version'],name='unique_document_version')]
    def save(self,*args,**kwargs):
        if not self._state.adding:
            raise ValidationError('Document versions are immutable. Upload a new version.')
        return super().save(*args,**kwargs)

