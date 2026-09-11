from django.conf import settings
from django.db import models

class MentorSearch(models.Model):
    project = models.OneToOneField('projects.Project', on_delete=models.CASCADE, related_name='mentor_search')
    state = models.CharField(max_length=12, default='pending', choices=[('pending','Pending response'),('accepted','Mentor attached'),('exhausted','No remaining candidate')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class MentorRequest(models.Model):
    search = models.ForeignKey(MentorSearch, on_delete=models.CASCADE, related_name='requests')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='mentor_requests')
    position = models.PositiveIntegerField()
    score = models.PositiveSmallIntegerField()
    reasons = models.JSONField(default=list)
    state = models.CharField(max_length=12, default='queued', choices=[
        ('queued','Queued'),('pending','Pending response'),('accepted','Accepted'),('rejected','Rejected'),('skipped','Skipped')])
    sent_at = models.DateTimeField(null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ['position','pk']
        constraints = [
            models.UniqueConstraint(fields=['search','teacher'],name='unique_mentor_candidate'),
            models.UniqueConstraint(fields=['search','position'],name='unique_mentor_position'),
            models.UniqueConstraint(fields=['search'],condition=models.Q(state='pending'),name='one_active_mentor_request'),
        ]
