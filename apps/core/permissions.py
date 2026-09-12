"""Shared, deny-by-default policies. Staff status never grants project access."""
from django.core.exceptions import PermissionDenied
from django.http import Http404

def college_member(user, complete=True):
    if not user.is_authenticated or not user.is_active or user.roster_role not in ('student', 'teacher'):
        return False
    profile = getattr(user, 'profile', None)
    return bool(profile and profile.role == user.roster_role and (profile.completed_at or not complete))

def approved_teacher(user):
    return college_member(user) and user.roster_role == 'teacher' and user.profile.teacher_approved

def can_create_idea(user):
    return college_member(user) and (user.roster_role == 'student' or approved_teacher(user))

def can_manage_project(user, project):
    if not can_create_idea(user):
        return False
    return project.creator_id == user.pk or (project.mentor_id == user.pk and approved_teacher(user))

def can_view_confidential(user, project):
    from apps.communities.permissions import can_enter
    return can_manage_project(user, project) or can_enter(user, project)

def can_view_project(user, project):
    if not college_member(user):
        return False
    if project.status in ('recruiting', 'closed') or can_manage_project(user, project):
        return True
    from apps.mentorship.models import MentorRequest
    return approved_teacher(user) and MentorRequest.objects.filter(search__project=project,search__state='pending',teacher=user,state='pending').exists()

def can_view_resume(user, resume):
    # Future application reviewers must use an application-scoped, snapshot download.
    return college_member(user, complete=False) and resume.profile.user_id == user.pk

def require_permission(allowed, conceal=True):
    if not allowed:
        raise Http404 if conceal else PermissionDenied

