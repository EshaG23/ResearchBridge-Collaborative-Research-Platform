from datetime import timedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET,require_http_methods
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from apps.communities.views import accessible
from apps.communities.permissions import can_edit
from apps.recruitment.permissions import can_review_applications
from apps.core.permissions import require_permission
from apps.documents.security import private_download
from .models import Completion,IPUpdate,Achievement
from .forms import CompletionForm,IPForm,AchievementForm
from .services import perform

def approved_achievements(user):
    since=timezone.localdate()-timedelta(days=getattr(settings,'ACHIEVEMENT_DAYS',365))
    return Achievement.objects.filter(visible=True,milestone_date__gte=since,milestone_date__lte=timezone.localdate(),community__project__creator__is_demo=user.is_demo).order_by('-milestone_date','-pk')[:12]

@login_required
@never_cache
@require_GET
def overview(request,pk):
    c=accessible(request,pk);state=Completion.objects.filter(community=c).select_related('confirmed_by__profile').first()
    return render(request,'ip_progress/overview.html',{'community':c,'page_title':'IP progress and completion','completion':state,'mentor':can_review_applications(request.user,c.project),'manager':can_edit(request.user,c.project),'updates':c.ip_updates.select_related('task'),'achievements':c.achievements.all(),'unfinished':c.tasks.exclude(status='approved').count()})

@login_required
@never_cache
@require_http_methods(['GET','POST'])
def action(request,pk,action,record_id=None):
    c=accessible(request,pk);require_permission(action in ('request','complete','reopen','ip','achievement','withdraw'))
    require_permission(can_edit(request.user,c.project) if action=='request' else can_review_applications(request.user,c.project))
    state=Completion.objects.filter(community=c).first();initial={'revision':state.revision if state else 1}
    cls=IPForm if action=='ip' else AchievementForm if action=='achievement' else CompletionForm
    form=cls(request.POST or None,request.FILES or None,initial=initial,**({'community':c} if action=='ip' else {}))
    if request.method=='POST' and form.is_valid():
        try:perform(request.user,pk,action,form.cleaned_data,record_id)
        except ValidationError as exc:form.add_error(None,' '.join(exc.messages))
        except (DatabaseError,OSError):form.add_error(None,'The update could not be saved. Please retry.')
        else:return redirect('ip_progress:overview',pk=pk)
    titles={'request':'Request project completion','complete':'Confirm project completion','reopen':'Reopen project / return request','ip':'Publish private IP update','achievement':'Approve shareable achievement','withdraw':'Withdraw shared achievement'}
    return render(request,'ip_progress/form.html',{'community':c,'page_title':titles[action],'form':form,'action':action,'unfinished':c.tasks.exclude(status='approved').count()})

@login_required
@never_cache
@require_GET
def download(request,pk,record_id):
    c=accessible(request,pk);record=get_object_or_404(IPUpdate,pk=record_id,community=c);require_permission(bool(record.file));r=private_download(record.file,record.filename);r['Content-Type']=record.mime;return r
