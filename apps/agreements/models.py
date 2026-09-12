import uuid
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

class ImmutableRecord(models.Model):
    class Meta:
        abstract=True
    def save(self,*args,**kwargs):
        if not self._state.adding:
            raise ValidationError('Agreement history is immutable. Create a new version or review.')
        return super().save(*args,**kwargs)

class Agreement(ImmutableRecord):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    project=models.ForeignKey('projects.Project',on_delete=models.PROTECT,related_name='agreements')
    student=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='agreements')
    enrolled_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='+')
    enrollment_reason=models.CharField(max_length=300)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['project','student'],name='one_agreement_per_student_project')]
    @property
    def latest(self):
        return self.evidence.order_by('-created_at','-pk').first()

def evidence_path(instance,filename):
    return f'agreements/{instance.agreement_id}/{instance.pk}/{filename}'

class AgreementEvidence(ImmutableRecord):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    agreement=models.ForeignKey(Agreement,on_delete=models.PROTECT,related_name='evidence')
    request_key=models.UUIDField(unique=True)
    snapshot=models.JSONField()
    method=models.CharField(max_length=10,choices=[('typed','Typed signature'),('drawn','Drawn signature'),('physical','Physical signed copy')])
    name=models.CharField(max_length=120)
    signature=models.JSONField(default=list)
    consent=models.TextField()
    created_at=models.DateTimeField()
    pdf=models.FileField(upload_to=evidence_path)
    signed_copy=models.FileField(upload_to=evidence_path,blank=True)
    sha256=models.CharField(max_length=64)
    copy_sha256=models.CharField(max_length=64,blank=True)
    @property
    def review(self):
        return self.reviews.order_by('-created_at','-pk').first()
    @property
    def status(self):
        review=self.review
        return review.action if review else 'pending'

class AgreementReview(ImmutableRecord):
    evidence=models.ForeignKey(AgreementEvidence,on_delete=models.PROTECT,related_name='reviews')
    actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    action=models.CharField(max_length=10,choices=[('verified','Verified'),('correction','Correction requested')])
    reason=models.CharField(max_length=1000)
    request_key=models.UUIDField(unique=True)
    created_at=models.DateTimeField(auto_now_add=True)
