from django.urls import reverse
from apps.core.permissions import can_view_project
from .models import Notification

def notify(recipient, event_key, title, message='', project=None):
    # Call within the business transaction so rollback cannot leave phantom notices.
    # Stable event keys make retried writes idempotent at database level.
    return Notification.objects.get_or_create(recipient=recipient, event_key=event_key,
        defaults={'title':title, 'message':message, 'project':project})[0]

def authorised_url(notification, user):
    if notification.recipient_id != user.pk:
        return None
    if notification.project_id and can_view_project(user, notification.project):
        return reverse('projects:detail', args=[notification.project_id])
    return None

