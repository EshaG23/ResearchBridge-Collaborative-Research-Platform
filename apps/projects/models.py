import uuid
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PENDING = 'pending_mentor', 'Awaiting mentor'
        RECRUITING = 'recruiting', 'Recruiting'
        CLOSED = 'closed', 'Recruitment closed'
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_ideas')
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name='mentored_projects')
    creation_key = models.UUIDField(default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=160)
    domain = models.ForeignKey('profiles.ResearchInterest', on_delete=models.PROTECT)
    departments = models.ManyToManyField('profiles.Department')
    skills = models.ManyToManyField('profiles.Skill')
    short_description = models.CharField(max_length=240)
    open_positions = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    available_roles = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    revision = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-updated_at', '-id']
        constraints = [
            models.UniqueConstraint(fields=['creator', 'creation_key'], name='unique_idea_submission'),
            models.CheckConstraint(condition=models.Q(open_positions__gte=1, open_positions__lte=100), name='valid_project_positions'),
            models.CheckConstraint(condition=~models.Q(status__in=['recruiting', 'closed']) | models.Q(mentor__isnull=False), name='published_project_has_mentor'),
        ]
    def __str__(self):
        return self.title

class ConfidentialIdea(models.Model):
    project = models.OneToOneField(Project, primary_key=True, on_delete=models.CASCADE, related_name='confidential')
    details = models.TextField(blank=True, max_length=20000)
    updated_at = models.DateTimeField(auto_now=True)

