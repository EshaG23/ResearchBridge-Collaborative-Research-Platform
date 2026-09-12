from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import DatabaseError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods
from apps.core.permissions import college_member, approved_teacher, can_create_idea, can_manage_project, can_view_project, can_view_confidential, require_permission
from .models import Project
from .forms import IdeaForm
from .services import save_idea

@login_required
@never_cache
@require_GET
def index(request):
    require_permission(college_member(request.user), conceal=False)
    created = request.GET.get('view') == 'created'
    scope = Q(creator=request.user)
    if not created and approved_teacher(request.user):
        scope |= Q(mentor=request.user)
    records = Project.objects.filter(scope) if can_create_idea(request.user) else Project.objects.none()
    records = records.select_related('domain','creator__profile','mentor__profile').prefetch_related('skills','departments')
    return render(request, 'projects/index.html', {'page_title':'Created Ideas' if created else 'My Projects',
        'created_view':created, 'page':Paginator(records,12).get_page(request.GET.get('page')), 'can_create':can_create_idea(request.user)})

@login_required
@never_cache
@require_http_methods(['GET','POST'])
def edit(request, pk=None):
    project = get_object_or_404(Project,pk=pk) if pk else None
    require_permission(can_manage_project(request.user,project) if project else can_create_idea(request.user), conceal=bool(project))
    form = IdeaForm(request.POST if request.method == 'POST' else None, instance=project)
    if request.method == 'POST' and form.is_valid():
        try:
            record = save_idea(request.user,form,request.POST.get('action','save'),project)
        except ValidationError as exc:
            form.add_error(None,exc)
        except DatabaseError:
            form.add_error(None,'Your idea could not be saved. Please try again.')
        else:
            messages.success(request,'Your idea has been saved.')
            return redirect('projects:detail',pk=record.pk)
    return render(request,'projects/form.html',{'page_title':'Edit idea' if project else 'Create idea',
        'form':form, 'project':project, 'is_teacher':request.user.roster_role == 'teacher'})

@login_required
@never_cache
@require_GET
def detail(request, pk):
    project = get_object_or_404(Project.objects.select_related('creator__profile','mentor__profile','domain').prefetch_related('departments','skills'),pk=pk)
    require_permission(can_view_project(request.user,project))
    from apps.recruitment.permissions import can_apply,can_view_applicant_overview
    from apps.recruitment.models import Application
    application = Application.objects.filter(project=project,applicant=request.user).first()
    from apps.mentorship.models import MentorRequest
    mentor_request = MentorRequest.objects.filter(search__project=project, teacher=request.user, state='pending').first() if approved_teacher(request.user) else None
    from apps.agreements.permissions import eligible_student
    has_agreement_access=eligible_student(request.user,project)
    # Never load the confidential relation on the recruitment page.
    return render(request,'projects/detail.html',{'page_title':'Project overview','project':project,
        'can_manage':can_manage_project(request.user,project), 'has_agreement_access':has_agreement_access,
        'can_private':can_view_confidential(request.user,project), 'mentor_request':mentor_request, 'can_apply':can_apply(request.user,project), 'application':application, 'can_review_applications':can_view_applicant_overview(request.user,project)})

@login_required
@never_cache
@require_GET
def private(request, pk):
    project = get_object_or_404(Project,pk=pk)
    require_permission(can_view_confidential(request.user,project))
    return render(request,'projects/private.html',{'page_title':'Confidential idea','project':project,
        'details':project.confidential.details, 'documents':project.documents.prefetch_related('versions__uploader').all()})



@login_required
@never_cache
@require_GET
def discover(request):
    from .discovery import discovery_context
    require_permission(college_member(request.user), conceal=False)
    return render(request, 'projects/discover.html', discovery_context(request) | {
        'page_title': 'Discover projects', 'can_create': can_create_idea(request.user)})
