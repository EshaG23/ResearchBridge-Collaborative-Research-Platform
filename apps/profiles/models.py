import uuid
from django.conf import settings
from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=120, unique=True)
    is_demo = models.BooleanField(default=False)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name

class Skill(models.Model):
    name = models.CharField(max_length=80, unique=True)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name

class ResearchInterest(models.Model):
    name = models.CharField(max_length=100, unique=True)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=[('student','Student'), ('teacher','Teacher')])
    name = models.CharField(max_length=120, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    interests = models.ManyToManyField(ResearchInterest, blank=True)
    availability = models.PositiveSmallIntegerField(null=True, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    previous_research = models.TextField(blank=True)
    scholar_url = models.URLField(blank=True)
    teacher_approved = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    @property
    def is_verified_teacher(self):
        return self.role == 'teacher' and self.teacher_approved
    @property
    def latest_resume(self):
        return self.resumes.order_by('-created_at', '-id').first()


def resume_path(instance, filename):
    return f'resumes/{instance.profile.user_id}/{uuid.uuid4().hex}.pdf'

class ResumeVersion(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to=resume_path)
    original_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    # Future application snapshots reference these immutable records with PROTECT.

    def save(self, *args, **kwargs):
        if not self._state.adding:
            from django.core.exceptions import ValidationError
            raise ValidationError('Resume versions are immutable. Upload a new version.')
        return super().save(*args, **kwargs)
