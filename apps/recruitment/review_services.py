from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from apps.core.permissions import require_permission
from apps.projects.models import Project
from apps.notifications.services import notify
from .models import Application, ReviewDecision, MeetingInvitation
from .permissions import can_review_applications

def lock_application(pk):
    project_id=Application.objects.values_list('project_id',flat=True).get(pk=pk)
    Project.objects.filter(pk=project_id).update(revision=F('revision'))
    return Application.objects.select_related('project','applicant').get(pk=pk)

TRANSITIONS={
    'shortlist':({'submitted'},'shortlisted'),
    'remove_shortlist':({'shortlisted'},'submitted'),
    'not_selected':({'submitted','shortlisted'},'not_selected'),
    'reopen':({'not_selected'},'submitted'),
    'select':({'shortlisted'},'selected'),
}

@transaction.atomic
def review_application(user,pk,action,revision,key):
    app=lock_application(pk)
    require_permission(can_review_applications(user,app.project))
    existing=ReviewDecision.objects.filter(application=app,request_key=key).first()
    if existing:
        if existing.actor_id!=user.pk or existing.action!=action:
            raise ValidationError('This confirmation was already used for another decision. Reload the application.')
        return app
    if action not in TRANSITIONS:
        raise ValidationError('Choose a valid review action.')
    allowed,target=TRANSITIONS[action]
    if app.revision!=revision:
        raise ValidationError('This application changed in another window. Reload before deciding.')
    if app.status not in allowed:
        raise ValidationError('This action is not available for the current application status.')
    if target=='selected' and app.project.applications.filter(status='selected').count()>=app.project.open_positions:
        raise ValidationError('All listed positions have been selected. Update the project capacity before selecting another student.')
    before=app.status
    app.status=target
    app.revision+=1
    app.save(update_fields=['status','revision'])
    decision=ReviewDecision.objects.create(application=app,actor=user,action=action,previous_status=before,
        new_status=target,request_key=key)
    notify(app.applicant,f'application-review:{decision.pk}','Application status updated',
        f'Your application is now {app.get_status_display().lower()}.',app.project,application=app)
    return app

@transaction.atomic
def invite_to_meeting(user,pk,data):
    app=lock_application(pk)
    require_permission(can_review_applications(user,app.project))
    existing=MeetingInvitation.objects.filter(application=app,request_key=data['request_key']).first()
    if existing:
        return existing
    if app.status not in ('submitted','shortlisted'):
        raise ValidationError('Meetings can be scheduled for submitted or shortlisted applications.')
    if app.revision!=data['revision']:
        raise ValidationError('This application changed. Reload before sending the invitation.')
    if data['scheduled_at']<=timezone.now():
        raise ValidationError('Choose a future meeting date and time.')
    invite=MeetingInvitation(application=app,created_by=user,request_key=data['request_key'],
        message=data['message'],scheduled_at=data['scheduled_at'],venue=data['venue'],online_url=data['online_url'])
    invite.full_clean()
    invite.save()
    notify(app.applicant,f'meeting:{invite.pk}:invited','Meeting invitation',
        'Your project mentor invited you to a meeting. Open your application for the date, time and venue.',
        app.project,application=app)
    return invite

@transaction.atomic
def cancel_meeting(user,pk):
    invitation=MeetingInvitation.objects.get(pk=pk)
    app=lock_application(invitation.application_id)
    require_permission(can_review_applications(user,app.project))
    invitation.refresh_from_db()
    if invitation.cancelled_at:
        return invitation
    invitation.cancelled_at=timezone.now()
    invitation.cancelled_by=user
    invitation.save(update_fields=['cancelled_at','cancelled_by'])
    notify(app.applicant,f'meeting:{invitation.pk}:cancelled','Meeting cancelled',
        'A meeting invitation was cancelled. Open your application to see which meeting changed.',
        app.project,application=app)
    return invitation
