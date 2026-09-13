from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.http import FileResponse,Http404
from django.shortcuts import get_object_or_404,render,redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET,require_http_methods
from apps.core.permissions import require_permission
from apps.documents.security import private_download
from .models import ProjectSummary,SummarySection,Sprint,SummaryResource
from .permissions import can_edit
from .views import accessible
from .summary_forms import SummaryForm,SectionForm,SprintForm,ResourceForm
from .summary_services import save_text,save_resource


def workspace_context(community):
    from django.db.models import Count,Q
    from apps.tasks.views import totals
    sprints=list(community.sprints.annotate(task_total=Count('tasks'),task_approved=Count('tasks',filter=Q(tasks__status='approved'))))
    for sprint in sprints:sprint.task_percent=round(100*sprint.task_approved/sprint.task_total) if sprint.task_total else 0
    completed=[s for s in sprints if s.status=='completed'];active=next((s for s in sprints if s.status=='active'),None)
    planned=[s for s in sprints if s.status=='planned']
    return {'task_stats':totals(community.tasks.all()),'sprints':sprints,'completed':completed,'active_sprint':active,'planned':planned,
        'next_sprint':planned[0] if planned else None,'sprint_total':len(sprints),'sprint_done':len(completed),
        'sprint_percent':round(100*len(completed)/len(sprints)) if sprints else 0}

@login_required
@never_cache
@require_GET
def summary(request,pk):
    community=accessible(request,pk)
    record=ProjectSummary.objects.filter(community=community).first()
    if not record:record=ProjectSummary(community=community,description=community.project.confidential.details)
    blocks=[('Project description',record.description),('Problem statement',record.problem),('Objectives',record.objectives),
        ('Existing solutions',record.existing_solutions),('Research gap',record.research_gap),('Research progress narrative',record.progress_notes)]
    return render(request,'communities/summary.html',{'community':community,'page_title':'Project summary','blocks':blocks,
        'can_edit':can_edit(request.user,community.project),'custom_sections':community.summary_sections.all(),
        'resources':community.resources.all(),'history':community.events.filter(action__in=['summary_saved','section_saved','resource_added','sprint_saved']).select_related('actor__profile')[:40],**workspace_context(community)})

@login_required
@never_cache
@require_GET
def sprints(request,pk):
    community=accessible(request,pk)
    return render(request,'communities/sprints.html',{'community':community,'page_title':'Sprints and planning','can_edit':can_edit(request.user,community.project),**workspace_context(community)})

@login_required
@never_cache
@require_http_methods(['GET','POST'])
def edit(request,pk,kind,record_pk=None):
    community=accessible(request,pk);require_permission(can_edit(request.user,community.project))
    if kind=='summary':
        record=ProjectSummary.objects.filter(community=community).first() or ProjectSummary(community=community,description=community.project.confidential.details)
        form_class=SummaryForm
    elif kind in ('section','sprint'):
        model,form_class=(SummarySection,SectionForm) if kind=='section' else (Sprint,SprintForm)
        record=get_object_or_404(model,community=community,pk=record_pk) if record_pk else model(community=community)
    else:raise Http404
    form=form_class(request.POST or None,instance=record,initial={'revision':community.revision})
    if request.method=='POST' and form.is_valid():
        try:save_text(request.user,pk,form.cleaned_data,kind,record_pk)
        except ValidationError as exc:form.add_error(None,' '.join(exc.messages))
        except DatabaseError:form.add_error(None,'Your changes could not be saved. Please try again.')
        else:
            messages.success(request,'Workspace changes saved.')
            return redirect('communities:sprints' if kind=='sprint' else 'communities:summary',pk=pk)
    return render(request,'communities/edit.html',{'community':community,'page_title':'Edit '+kind,'form':form,'kind':kind})

@login_required
@never_cache
@require_http_methods(['GET','POST'])
def resource(request,pk):
    community=accessible(request,pk);require_permission(can_edit(request.user,community.project))
    form=ResourceForm(request.POST or None,request.FILES or None,initial={'revision':community.revision})
    if request.method=='POST' and form.is_valid():
        try:save_resource(request.user,pk,form.cleaned_data)
        except ValidationError as exc:form.add_error(None,' '.join(exc.messages))
        except (DatabaseError,OSError):form.add_error(None,'The resource could not be saved. Please try again.')
        else:return redirect('communities:summary',pk=pk)
    return render(request,'communities/edit.html',{'community':community,'page_title':'Add research resource','form':form,'kind':'resource'})

@login_required
@never_cache
@require_GET
def download(request,pk,resource_pk):
    community=accessible(request,pk)
    resource=get_object_or_404(SummaryResource,pk=resource_pk,community=community)
    require_permission(bool(resource.file))
    response=private_download(resource.file,resource.filename)
    response['Content-Type']=resource.mime_type
    return response
