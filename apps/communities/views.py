import uuid
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.shortcuts import get_object_or_404,render,redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET,require_http_methods,require_POST
from apps.projects.models import Project
from apps.core.permissions import require_permission
from apps.recruitment.permissions import can_review_applications
from .models import Community
from .permissions import can_enter
from .services import checklist,confirmation,create_or_sync,appoint_leader

@login_required
@never_cache
@require_http_methods(['GET','POST'])
def create(request,pk):
    project=get_object_or_404(Project,pk=pk);require_permission(can_review_applications(request.user,project))
    if request.method=='POST':
        try:
            community=create_or_sync(request.user,pk,request.POST.get('token',''),sync=request.POST.get('action')=='sync')
            return redirect('communities:detail',pk=community.pk)
        except ValidationError as exc:messages.error(request,' '.join(exc.messages))
        except DatabaseError:messages.error(request,'The community could not be saved. Please try again.')
    return render(request,'communities/create.html',{'page_title':'Create private community','project':project,'token':confirmation(request.user,project),**checklist(project)})

def accessible(request,pk):
    community=get_object_or_404(Community.objects.select_related('project__mentor__profile','project__creator__profile','leader__profile'),pk=pk)
    require_permission(can_enter(request.user,community.project))
    return community

@login_required
@never_cache
@require_GET
def detail(request,pk):
    community=accessible(request,pk)
    from .summary_views import workspace_context
    progress=workspace_context(community)
    members=list(community.memberships.filter(role='student').select_related('user__profile'))
    for m in members:m.has_access=can_enter(m.user,community.project)
    return render(request,'communities/detail.html',{'page_title':'Private project community','community':community,'members':members,
        'is_mentor':can_review_applications(request.user,community.project),'leader_active':bool(community.leader and can_enter(community.leader,community.project)),
        **progress,'key':uuid.uuid4(),'events':community.events.select_related('actor__profile')[:30]})

@login_required
@never_cache
@require_GET
def section(request,pk,section):
    names={'summary':'Summary','chat':'Internal Chat','todo':'To-do','announcements':'Announcements','ip':'IP Progress'}
    require_permission(section in names);community=accessible(request,pk)
    return render(request,'communities/section.html',{'page_title':names[section],'section':section,'community':community,
        'title':names[section],'documents':community.project.documents.all() if section=='summary' else []})

@login_required
@never_cache
@require_POST
def leader(request,pk):
    community=get_object_or_404(Community,pk=pk)
    require_permission(can_review_applications(request.user,community.project))
    try:
        appoint_leader(request.user,pk,int(request.POST.get('student','')),int(request.POST.get('revision','')),uuid.UUID(request.POST.get('key','')))
        messages.success(request,'Team leader appointment saved.')
    except (ValueError,ValidationError) as exc:messages.error(request,str(exc))
    except DatabaseError:messages.error(request,'The appointment could not be saved. Try again.')
    return redirect('communities:detail',pk=pk)
