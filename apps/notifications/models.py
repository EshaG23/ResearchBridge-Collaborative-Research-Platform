from django.conf import settings
from django.db import models

class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    event_key = models.CharField(max_length=180)
    title = models.CharField(max_length=160)
    message = models.CharField(max_length=500, blank=True)
    project = models.ForeignKey('projects.Project', null=True, blank=True, on_delete=models.SET_NULL)
    application = models.ForeignKey('recruitment.Application', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ['-created_at', '-pk']
        constraints = [models.UniqueConstraint(fields=['recipient','event_key'], name='unique_notification_event')]
        indexes = [models.Index(fields=['recipient','read_at'], name='notification_unread_idx')]

