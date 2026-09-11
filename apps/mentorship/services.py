from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from apps.accounts.models import User
from apps.core.permissions import college_member, approved_teacher, require_permission
from apps.projects.models import Project
from apps.notifications.services import notify
from .models import MentorSearch, MentorRequest

def rank_mentors(project):
    skills = set(project.skills.values_list('pk',flat=True))
    departments = set(project.departments.values_list('pk',flat=True))
    candidates = User.objects.filter(is_active=True,roster_role='teacher',is_demo=project.creator.is_demo,
        profile__role='teacher',profile__teacher_approved=True,profile__completed_at__isnull=False
    ).exclude(pk=project.creator_id).select_related('profile__department').prefetch_related('profile__skills','profile__interests')
    results=[]
    for teacher in candidates:
        profile=teacher.profile
        common=[skill.name for skill in profile.skills.all() if skill.pk in skills]
        domain_match=project.domain_id in {interest.pk for interest in profile.interests.all()}
        department_match=profile.department_id in departments
        score=(50 if domain_match else 0)+(20 if department_match else 0)+(round(30*len(common)/len(skills)) if skills else 0)
        reasons=[]
        if domain_match:
            reasons.append('Research interest matches '+str(project.domain))
        if department_match:
            reasons.append('Department matches '+str(profile.department))
        if common:
            reasons.append('Shared skills: '+', '.join(common))
        if not reasons:
            reasons.append('No shared tags yet; available for a cross-disciplinary approach.')
        results.append({'teacher':teacher,'score':score,'reasons':reasons})
    return sorted(results,key=lambda row:(-row['score'],row['teacher'].profile.name.casefold(),row['teacher'].pk))

def _lock_project(pk):
    # Write first: serialises competing decisions on SQLite and row-locks on PostgreSQL.
    Project.objects.filter(pk=pk).update(revision=F('revision'))
    return Project.objects.select_related('creator__profile','mentor__profile').get(pk=pk)

def _advance(search, project):
    for candidate in search.requests.filter(state='queued').select_related('teacher__profile'):
        if not approved_teacher(candidate.teacher):
            candidate.state='skipped'
            candidate.decided_at=timezone.now()
            candidate.save(update_fields=['state','decided_at'])
            continue
        candidate.state='pending'
        candidate.sent_at=timezone.now()
        candidate.save(update_fields=['state','sent_at'])
        notify(candidate.teacher,f'mentor:{candidate.pk}:requested','Mentor request',
            f'{project.creator.profile.name} requests your mentorship for {project.title}.'[:500],project)
        return candidate
    search.state='exhausted'
    search.save(update_fields=['state','updated_at'])
    notify(project.creator,f'mentor-search:{search.pk}:exhausted','No remaining mentor candidate',
        'All candidates in this request list have declined or become ineligible. No mentor has been attached.',project)
    return None

@transaction.atomic
def start_search(user, project_pk, teacher_id):
    project=_lock_project(project_pk)
    require_permission(college_member(user) and user.roster_role=='student' and project.creator_id==user.pk)
    existing=MentorSearch.objects.filter(project=project).first()
    if existing:
        return existing
    if project.mentor_id or project.status != Project.Status.PENDING:
        raise ValidationError('Save your student idea for mentorship before sending a request.')
    ranked=rank_mentors(project)
    chosen=next((row for row in ranked if row['teacher'].pk==teacher_id),None)
    if chosen is None:
        raise ValidationError('That teacher is no longer eligible. Refresh the recommendations.')
    ordered=[chosen]+[row for row in ranked if row is not chosen]
    search=MentorSearch.objects.create(project=project)
    MentorRequest.objects.bulk_create([MentorRequest(search=search,teacher=row['teacher'],position=position,
        score=row['score'],reasons=row['reasons']) for position,row in enumerate(ordered,1)])
    Project.objects.filter(pk=project.pk).update(revision=F('revision')+1)
    _advance(search,project)
    notify(user,f'mentor-search:{search.pk}:started','Mentor request sent',
        'Your chosen teacher has been notified. Remaining teachers will be approached in priority order only after rejection.',project)
    return search

@transaction.atomic
def decide(user, request_pk, action, expected_revision):
    candidate=MentorRequest.objects.select_related('search').get(pk=request_pk)
    project=_lock_project(candidate.search.project_id)
    candidate=MentorRequest.objects.select_related('search').get(pk=request_pk)
    require_permission(approved_teacher(user) and candidate.teacher_id==user.pk)
    if action not in ('accept','reject'):
        raise ValidationError('Choose Accept or Decline.')
    desired='accepted' if action=='accept' else 'rejected'
    if candidate.state==desired:
        return candidate  # Network retries do not resend events or advance twice.
    if candidate.state!='pending' or candidate.search.state!='pending' or project.mentor_id:
        raise ValidationError('This request is no longer awaiting your decision.')
    if project.revision!=expected_revision:
        raise ValidationError('The idea changed since you opened it. Reload and review the current details before deciding.')
    candidate.state=desired
    candidate.decided_at=timezone.now()
    candidate.save(update_fields=['state','decided_at'])
    if action=='accept':
        project.mentor=user
        project.status=Project.Status.RECRUITING
        project.revision+=1
        project.save(update_fields=['mentor','status','revision','updated_at'])
        candidate.search.state='accepted'
        candidate.search.save(update_fields=['state','updated_at'])
        candidate.search.requests.filter(state='queued').update(state='skipped',decided_at=timezone.now())
        notify(project.creator,f'mentor:{candidate.pk}:accepted','Mentor accepted',
            f'{user.profile.name} accepted your request. Recruitment is now open.',project)
        notify(user,f'mentor:{candidate.pk}:confirmed','Mentorship confirmed',
            'You are now the project mentor. This project is available in My Projects.',project)
    else:
        notify(project.creator,f'mentor:{candidate.pk}:rejected','Mentor request declined',
            f'{user.profile.name} declined. The next eligible teacher in your saved priority list will be approached.',project)
        _advance(candidate.search,project)
    return candidate
