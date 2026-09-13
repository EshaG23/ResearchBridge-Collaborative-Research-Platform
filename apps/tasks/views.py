from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.db.models import Count,Q
from django.core.paginator import Paginator
from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET,require_http_methods
from apps.communities.views import accessible
from apps.communities.permissions import can_edit
from apps.core.permissions import require_permission
from apps.documents.security import private_download
from .models import Task,TaskFile
from .forms import TaskForm,WorkForm,ReviewForm,ReopenForm,CommentForm
from .services import save_task,act,EDITABLE

def totals(query):
    counts=query.aggregate(total=Count('pk'),approved=Count('pk',filter=Q(status='approved')))
    counts['percent']=round(100*counts['approved']/counts['total']) if counts['total'] else 0
    return counts

@login_required
@never_cache
@require_GET
def board(request,pk):
    c=accessible(request,pk);query=c.tasks.select_related('assignee__profile','sprint');stats=totals(query)
    state=request.GET.get('state','');mine=request.GET.get('mine')=='1';sprint=request.GET.get('sprint','');term=request.GET.get('q','')[:160]
    if state in dict(Task.STATES):query=query.filter(status=state)
    else:state=''
    if mine:query=query.filter(assignee=request.user)
    if sprint:
        try:selected=get_object_or_404(c.sprints,pk=sprint)
        except ValidationError:
            from django.http import Http404
            raise Http404
        query=query.filter(sprint=selected)
    if term:query=query.filter(Q(title__icontains=term)|Q(description__icontains=term))
    return render(request,'tasks/board.html',{'community':c,'page_title':'Tasks and review','stats':stats,'page':Paginator(query.exclude(status='approved'),24).get_page(request.GET.get('page')),'completed_page':Paginator(query.filter(status='approved'),24).get_page(request.GET.get('completed_page')),'states':Task.STATES,'state':state,'mine':mine,'sprint_filter':sprint,'term':term,'can_edit':can_edit(request.user,c.project)})

@login_required
@never_cache
@require_http_methods(['GET','POST'])
def edit(request,pk,task_id=None):
    c=accessible(request,pk);require_permission(can_edit(request.user,c.project))
    t=get_object_or_404(Task,pk=task_id,community=c) if task_id else Task(community=c)
    form=TaskForm(request.POST or None,instance=t,community=c,initial={'revision':t.revision})
    if request.method=='POST' and form.is_valid():
        try:result=save_task(request.user,pk,form.cleaned_data,task_id)
        except ValidationError as exc:form.add_error(None,' '.join(exc.messages))
        except DatabaseError:form.add_error(None,'The task could not be saved. Please retry.')
        else:return redirect('tasks:detail',pk=pk,task_id=result.pk)
    return render(request,'tasks/form.html',{'community':c,'page_title':'Edit task' if task_id else 'Create task','form':form,'button':'Save task'})

@login_required
@never_cache
@require_GET
def detail(request,pk,task_id):
    c=accessible(request,pk);t=get_object_or_404(Task.objects.select_related('assignee__profile','sprint'),pk=task_id,community=c)
    latest=t.submissions.first();manager=can_edit(request.user,c.project)
    return render(request,'tasks/detail.html',{'community':c,'task':t,'page_title':t.title,'can_edit':manager and t.status in EDITABLE,
        'can_work':t.assignee_id==request.user.pk and t.status in EDITABLE,'can_review':manager and t.assignee_id!=request.user.pk and t.status=='submitted' and latest and latest.submitter_id!=request.user.pk,
        'can_reopen':manager and t.status=='approved','submissions':t.submissions.select_related('submitter__profile','review__reviewer__profile').prefetch_related('files'),
        'files':t.files.select_related('uploader__profile'),'comments':t.comments.select_related('author__profile','file'),
        'history':c.events.filter(details__task_id=str(t.pk)).select_related('actor__profile')})

@login_required
@never_cache
@require_http_methods(['GET','POST'])
def action(request,pk,task_id,action):
    c=accessible(request,pk);t=get_object_or_404(Task,pk=task_id,community=c)
    require_permission(action in ('work','submit','review','reopen','comment'))
    if action in ('work','submit'):require_permission(t.assignee_id==request.user.pk)
    if action in ('review','reopen'):require_permission(can_edit(request.user,c.project))
    if action=='review':require_permission(t.assignee_id!=request.user.pk)
    classes={'work':WorkForm,'submit':WorkForm,'review':ReviewForm,'reopen':ReopenForm,'comment':CommentForm}
    latest=t.submissions.first();initial={'revision':t.revision,'summary':t.progress_notes,'blocker':t.blocker,'submission':latest.pk if latest else None}
    if latest:initial['evidence']=list(latest.files.values_list('pk',flat=True))
    form=classes[action](request.POST or None,request.FILES or None,initial=initial,**({'task':t} if action in ('work','submit','comment') else {}))
    if request.method=='POST' and form.is_valid():
        try:act(request.user,pk,task_id,action,form.cleaned_data,form.cleaned_data.get('uploads',[]))
        except ValidationError as exc:form.add_error(None,' '.join(exc.messages))
        except (DatabaseError,OSError):form.add_error(None,'Your update could not be saved. Please retry.')
        else:
            messages.success(request,'Task update saved.');return redirect('tasks:detail',pk=pk,task_id=task_id)
    titles={'work':'Update progress','submit':'Submit work for review','review':'Review latest submission','reopen':'Reopen approved task','comment':'Discuss this task'}
    return render(request,'tasks/form.html',{'community':c,'task':t,'latest':latest if action=='review' else None,'page_title':titles[action],'form':form,'button':titles[action]})

@login_required
@never_cache
@require_GET
def download(request,pk,file_id):
    c=accessible(request,pk);f=get_object_or_404(TaskFile,pk=file_id,task__community=c)
    response=private_download(f.file,f.filename);response['Content-Type']=f.mime;return response
