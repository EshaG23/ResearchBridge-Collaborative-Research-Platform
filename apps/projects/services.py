from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth import get_user_model
from django.db.models import F
from apps.core.permissions import can_create_idea, can_manage_project, approved_teacher, require_permission
from apps.notifications.services import notify
from .models import Project, ConfidentialIdea

@transaction.atomic
def save_idea(user, form, action, project=None):
    require_permission(can_manage_project(user, project) if project else can_create_idea(user), conceal=False)
    if action not in ('draft', 'submit', 'save'):
        raise ValidationError('Choose a valid save action.')
    if project is None:
        # Acquire a write lock before checking a repeated submission under SQLite.
        get_user_model().objects.filter(pk=user.pk).update(is_active=F('is_active'))
        existing = Project.objects.filter(creator=user, creation_key=form.cleaned_data['creation_key']).first()
        if existing:
            return existing
        record = form.save(commit=False)
        record.creator = user
        record.creation_key = form.cleaned_data['creation_key']
        record.mentor = user if approved_teacher(user) else None
    else:
        changed = Project.objects.filter(pk=project.pk, revision=form.cleaned_data['revision']).update(revision=F('revision')+1)
        if not changed:
            raise ValidationError('This idea changed in another window. Reload the page before saving again.')
        record = form.save(commit=False)
        record.revision = form.cleaned_data['revision'] + 1
    if action == 'submit' and record.status == Project.Status.DRAFT:
        record.status = Project.Status.RECRUITING if record.mentor_id else Project.Status.PENDING
    record.save()
    form.save_m2m()
    from apps.notifications.services import notify_departments
    notify_departments(record)
    ConfidentialIdea.objects.update_or_create(project=record, defaults={'details':form.cleaned_data['confidential_details']})
    notify(user, f'idea:{record.pk}:saved:{record.revision}', 'Idea saved',
           'Your idea and recruitment details have been saved.', record)
    if record.mentor_id and record.mentor_id != user.pk:
        notify(record.mentor, f'idea:{record.pk}:updated:{record.revision}',
               'Project details updated', 'Recruitment and idea records were updated.', record)
    return record

