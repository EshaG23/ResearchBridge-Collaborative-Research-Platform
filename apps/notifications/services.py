from django.urls import reverse
from apps.core.permissions import can_view_project
from .models import Notification

def notify(recipient, event_key, title, message='', project=None, application=None):
    # Call within the business transaction so rollback cannot leave phantom notices.
    # Stable event keys make retried writes idempotent at database level.
    return Notification.objects.get_or_create(recipient=recipient, event_key=event_key,
        defaults={'title':title, 'message':message, 'project':project, 'application':application})[0]

def authorised_url(notification, user):
    if notification.recipient_id != user.pk:
        return None
    if notification.project_id and notification.event_key.startswith(('outcome:','task:')):
        from apps.communities.models import Community,CommunityEvent
        from apps.communities.permissions import can_enter
        c=Community.objects.filter(project_id=notification.project_id).first()
        if not c or not can_enter(user,c.project):return None
        if notification.event_key.startswith('outcome:'):return reverse('ip_progress:overview',args=[c.pk])
        import uuid
        try:key=uuid.UUID(notification.event_key.split(':')[1])
        except (ValueError,IndexError):return None
        event=CommunityEvent.objects.filter(community=c,request_key=key).first()
        if event and c.tasks.filter(pk=event.details.get('task_id')).exists():return reverse('tasks:detail',args=[c.pk,event.details['task_id']])
        return None
    if notification.application_id:
        from apps.recruitment.permissions import can_view_application
        if can_view_application(user,notification.application):
            return reverse('recruitment:detail',args=[notification.application_id])
        return None
    if notification.project_id and can_view_project(user, notification.project):
        return reverse('projects:detail', args=[notification.project_id])
    return None



def notify_departments(project):
    from django.contrib.auth import get_user_model
    if project.status!='recruiting':return
    from apps.core.permissions import college_member
    users=get_user_model().objects.filter(is_active=True,roster_role='student',is_demo=project.creator.is_demo,profile__department__in=project.departments.all()).exclude(pk=project.creator_id).select_related('profile')
    for user in users:
        if college_member(user):notify(user,f'project-published:{project.pk}','New research opportunity',project.short_description,project)
