import uuid
from django.utils import timezone
from django.db.models import Count,Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import DatabaseError
from django.shortcuts import get_object_or_404,render,redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET,require_http_methods
from apps.core.permissions import require_permission,approved_teacher
from apps.projects.models import Project
from apps.documents.security import private_download
from .models import Application
from .forms import ApplicationForm
from .permissions import can_apply,can_view_application,can_review_applications,can_view_applicant_overview
from .review_forms import ApplicantFilterForm
from .services import prepare_application,submit_application

@login_required
@never_cache
@require_http_methods(['GET','POST'])
def apply(request,project_pk):
    project=get_object_or_404(Project.objects.select_related('mentor__profile','creator'),pk=project_pk)
    existing=Application.objects.filter(project=project,applicant=request.user).first()
    if existing and existing.status!='draft':
        return redirect('recruitment:detail',pk=existing.pk)
    require_permission(can_apply(request.user,project))
    form=ApplicationForm(request.POST if request.method=='POST' else None,request.FILES or None,user=request.user,
        initial={'motivation':existing.motivation if existing else '', 'academic_score':existing.academic_score if existing else ''})
    if request.method=='POST' and form.is_valid():
        try:
            app=prepare_application(request.user,project.pk,form.cleaned_data)
        except (DatabaseError,OSError):
            form.add_error(None,'Your draft could not be saved. Check the résumé file and try again.')
        else:
            return redirect('recruitment:detail',pk=app.pk)
    return render(request,'recruitment/apply.html',{'page_title':'Apply to project','project':project,'form':form,
        'resumes':request.user.profile.resumes.all()})

@login_required
@never_cache
@require_http_methods(['GET','POST'])
def detail(request,pk):
    app=get_object_or_404(Application.objects.select_related('project__mentor__profile','profile_resume'),pk=pk)
    require_permission(can_view_application(request.user,app))
    error=None
    if request.method=='POST':
        require_permission(app.applicant_id==request.user.pk)
        try:
            revision=int(request.POST.get('revision',''))
            submit_application(request.user,pk,revision)
        except (ValueError,ValidationError):
            error='Your draft changed or the confirmation was invalid. Reload and review before submitting.'
        except (DatabaseError,OSError):
            error='Your application could not be submitted. Please try again.'
        else:
            messages.success(request,'Application submitted. Your résumé and details are preserved.')
            return redirect('recruitment:detail',pk=pk)
    return render(request,'recruitment/detail.html',{'page_title':'Your application' if app.applicant_id==request.user.pk else 'Application details',
        'application':app,'error':error,'is_reviewer':can_review_applications(request.user,app.project),
        'review_key':uuid.uuid4(),'meetings':app.meetings.all(),'decisions':app.decisions.select_related('actor__profile'), 'now':timezone.now()})

@login_required
@never_cache
@require_GET
def resume(request,pk):
    app=get_object_or_404(Application.objects.select_related('project__mentor__profile','profile_resume'),pk=pk)
    require_permission(can_view_application(request.user,app))
    return private_download(app.resume_file,app.resume_name)

@login_required
@never_cache
@require_GET
def index(request,project_pk=None):
    project=None
    if project_pk:
        project=get_object_or_404(Project,pk=project_pk)
        require_permission(can_view_applicant_overview(request.user,project))
        rows=project.applications.exclude(status='draft')
        counts=rows.aggregate(total=Count('pk'),shortlisted=Count('pk',filter=Q(status='shortlisted')),
            selected=Count('pk',filter=Q(status='selected')),not_selected=Count('pk',filter=Q(status='not_selected')))
        form=ApplicantFilterForm(request.GET)
        valid=form.is_valid()
        if valid:
            if form.cleaned_data['q']:
                rows=rows.filter(snapshot__name__icontains=form.cleaned_data['q'])
            if form.cleaned_data['status']:
                rows=rows.filter(status=form.cleaned_data['status'])
        else:
            rows=rows.none()
        # Proposer overview fetches only permitted fields; no phone/email/private statements.
        rows=rows.order_by('-submitted_at','-pk').values('id','status','submitted_at','snapshot__name',
            'snapshot__department','snapshot__year','snapshot__skills','snapshot__availability')
        page=Paginator(rows,12).get_page(request.GET.get('page'))
        labels=dict(Application._meta.get_field('status').choices)
        for row in page:
            row['status_label']=labels[row['status']]
        query=request.GET.copy();query.pop('page',None)
        return render(request,'recruitment/manage.html',{'page_title':'Applicant management','project':project,
            'page':page,'counts':counts,'is_reviewer':can_review_applications(request.user,project),
            'filter_form':form,'filters_valid':valid,'extra_query':query.urlencode()+'&' if query else ''})

    else:
        rows=Application.objects.filter(applicant=request.user)
    return render(request,'recruitment/index.html',{'page_title':'Project applications' if project else 'My applications',
        'project':project,'page':Paginator(rows.select_related('project'),12).get_page(request.GET.get('page'))})
