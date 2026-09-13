from collections import defaultdict
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from django.shortcuts import render
from .views import accessible
from .models import SummaryResource
from apps.tasks.models import TaskFile,Submission,Review
from apps.documents.models import DocumentVersion

class Filters(forms.Form):
    member=forms.ChoiceField(required=False)
    sprint=forms.ChoiceField(required=False)
    kind=forms.ChoiceField(required=False,choices=[('','All activity'),('lifecycle','Project milestones'),('workspace','Workspace updates'),('task','Task activity'),('file','Files and revisions')])
    start=forms.DateField(required=False,widget=forms.DateInput(attrs={'type':'date'}))
    end=forms.DateField(required=False,widget=forms.DateInput(attrs={'type':'date'}))
    def clean(self):
        data=super().clean()
        if data.get('start') and data.get('end') and data['start']>data['end']:raise forms.ValidationError('The end date must be on or after the start date.')
        return data

def file_rows(c):
    rows=[]
    for source,records in [('task',TaskFile.objects.filter(task__community=c).select_related('uploader__profile','task')),('summary',c.resources.select_related('added_by__profile'))]:
        items=list(records);byid={f.pk:f for f in items};parents={f.replaces_id for f in items if f.replaces_id}
        for f in items:
            root=f
            while root.replaces_id in byid:root=byid[root.replaces_id]
            user=f.uploader if source=='task' else f.added_by
            url=reverse('tasks:download',args=[c.pk,f.pk]) if source=='task' else reverse('communities:resource-download',args=[c.pk,f.pk]) if f.file else f.url
            rows.append({'group':str(root.pk),'version':f.version,'latest':f.pk not in parents,'name':f.filename or f.title,'actor':f.uploader_name or user.profile.name,'user':str(user.pk),'time':f.created_at,'note':f.revision_note,'url':url,'scope':f.task.title if source=='task' else 'Summary: '+f.title,'task':str(f.task_id) if source=='task' else '', 'sprint':str(f.task.sprint_id) if source=='task' and f.task.sprint_id else '', 'source':source})
    for f in DocumentVersion.objects.filter(document__project=c.project).select_related('document','uploader__profile'):
        rows.append({'group':str(f.document_id),'version':f.version,'latest':not f.document.versions.filter(version__gt=f.version).exists(),'name':f.original_name,'actor':f.uploader_name or f.uploader.profile.name,'user':str(f.uploader_id),'time':f.created_at,'note':'','url':reverse('documents:download',args=[c.project_id,f.pk]),'scope':f.document.title,'task':'','sprint':'','source':'project'})
    return rows

def activity(c,files):
    rows=[]
    def add(when,user,title,kind='lifecycle',url='',name='',sprint='',detail=''):
        if when:rows.append({'time':when,'user':str(user.pk),'actor':name or user.profile.name,'title':title,'kind':kind,'url':url,'sprint':sprint,'detail':detail})
    add(c.project.created_at,c.project.creator,'Project created',url=reverse('projects:detail',args=[c.project_id]))
    from apps.mentorship.models import MentorRequest
    from apps.recruitment.models import ReviewDecision
    from apps.agreements.models import AgreementEvidence,AgreementReview
    for r in MentorRequest.objects.filter(search__project=c.project,state='accepted').select_related('teacher__profile'):add(r.decided_at,r.teacher,'Mentor accepted project')
    for r in ReviewDecision.objects.filter(application__project=c.project,new_status='selected').select_related('actor__profile'):add(r.created_at,r.actor,'Team selection recorded')
    for r in AgreementEvidence.objects.filter(agreement__project=c.project).select_related('agreement__student__profile'):add(r.created_at,r.agreement.student,'Agreement evidence submitted',name=r.name)
    for r in AgreementReview.objects.filter(evidence__agreement__project=c.project).select_related('actor__profile'):add(r.created_at,r.actor,'Agreement '+r.get_action_display().lower())
    tasks={str(t.pk):t for t in c.tasks.all()}
    for e in c.events.select_related('actor__profile'):
        d=e.details;task=tasks.get(d.get('task_id'));sprint=d.get('sprint_id','') or (str(task.sprint_id) if task and task.sprint_id else '')
        title={'outcome_request':'Completion requested','outcome_complete':'Project completion confirmed','outcome_reopen':'Project reopened','outcome_ip':'Private IP progress updated','outcome_achievement':'Shareable achievement approved','outcome_withdraw':'Shared achievement withdrawn'}.get(e.action,e.description);detail=''
        changes=[]
        for field in ['title','status','assignee_id','due_date','start_date','end_date']:
            before=d.get('before',{});after=d.get('after',{})
            if field in after and before.get(field)!=after[field]:changes.append(field.replace('_',' ')+': '+str(before.get(field) or 'not set')+' → '+str(after[field] or 'not set'))
        detail='; '.join(changes[:3])
        if e.action=='sprint_saved':
            after=d.get('after',{});before=d.get('before',{});sprint=d.get('record_id','')
            title='Sprint '+('started' if after.get('status')=='active' and before.get('status')!='active' else 'completed' if after.get('status')=='completed' and before.get('status')!='completed' else 'saved')
            detail=after.get('title','')+' · '+before.get('status','new')+' → '+after.get('status','')
        if e.action=='task_work':detail=('Blocker resolved. ' if d.get('previous_blocker') and not d.get('blocker') else 'Blocker reported. ' if d.get('blocker') else '')+d.get('summary','')
        if e.action=='task_review':detail=d.get('decision','')+': '+d.get('feedback','')
        if e.action=='task_reopen':detail=d.get('reason','')
        if e.action.startswith('outcome_'):detail=d.get('title','')+' '+d.get('status','')+' '+d.get('note','')
        add(e.created_at,e.actor,title+(': '+d.get('title',task.title) if task else ''),'task' if task else 'workspace',reverse('tasks:detail',args=[c.pk,task.pk]) if task else '',e.actor_name,sprint,detail)
    for f in files:rows.append({'time':f['time'],'user':f['user'],'actor':f['actor'],'title':('New document version' if f['version']>1 else 'File / reference added')+': '+f['name']+' · v'+str(f['version']),'kind':'file','url':f['url'],'sprint':f['sprint'],'detail':f['note']})
    return sorted(rows,key=lambda r:r['time'],reverse=True)

@login_required
@never_cache
@require_GET
def history(request,pk):
    c=accessible(request,pk);files=file_rows(c);rows=activity(c,files)
    people={r['user']:r['actor'] for r in reversed(rows)}
    form=Filters(request.GET);form.fields['member'].choices=[('','All contributors')]+sorted(people.items(),key=lambda p:p[1].lower());form.fields['sprint'].choices=[('','All sprints')]+[(str(s.pk),s.title) for s in c.sprints.all()]
    if form.is_valid():
        d=form.cleaned_data
        rows=[r for r in rows if (not d['member'] or r['user']==d['member']) and (not d['sprint'] or r['sprint']==d['sprint']) and (not d['kind'] or r['kind']==d['kind']) and (not d['start'] or timezone.localtime(r['time']).date()>=d['start']) and (not d['end'] or timezone.localtime(r['time']).date()<=d['end'])]
    else:rows=[]
    params=request.GET.copy();params.pop('page',None)
    return render(request,'communities/history.html',{'community':c,'page_title':'Project history','form':form,'page':Paginator(rows,30).get_page(request.GET.get('page')),'params':params.urlencode()})

@login_required
@never_cache
@require_GET
def library(request,pk):
    c=accessible(request,pk);rows=file_rows(c);groups=defaultdict(list)
    term=request.GET.get('q','')[:160]
    for row in rows:groups[(row['source'],row['group'])].append(row)
    items=[sorted(values,key=lambda r:r['version'],reverse=True) for values in groups.values() if not term or any(term.casefold() in (r['name']+' '+r['scope']).casefold() for r in values)]
    items.sort(key=lambda versions:versions[0]['time'],reverse=True)
    return render(request,'communities/library.html',{'community':c,'page_title':'Document version library','page':Paginator(items,15).get_page(request.GET.get('page')),'term':term})

@login_required
@never_cache
@require_GET
def contributions(request,pk):
    c=accessible(request,pk);people={}
    def person(user,name=''):
        return people.setdefault(user.pk,{'id':str(user.pk),'name':name or user.profile.name,'submissions':0,'uploads':0,'revisions':0,'approved':0,'reviews':0})
    snapshots={e.actor_id:e.actor_name for e in c.events.exclude(actor_name='').order_by('created_at')}
    for sub in Submission.objects.filter(task__community=c).select_related('submitter__profile'):person(sub.submitter,snapshots.get(sub.submitter_id,''))['submissions']+=1
    for f in TaskFile.objects.filter(task__community=c).select_related('uploader__profile'):
        row=person(f.uploader,f.uploader_name);row['uploads']+=1;row['revisions']+=int(f.version>1)
    for f in c.resources.select_related('added_by__profile'):
        row=person(f.added_by,f.uploader_name);row['uploads']+=1;row['revisions']+=int(f.version>1)
    for f in DocumentVersion.objects.filter(document__project=c.project).select_related('uploader__profile'):
        row=person(f.uploader,f.uploader_name or snapshots.get(f.uploader_id,''));row['uploads']+=1;row['revisions']+=int(f.version>1)
    for review in Review.objects.filter(submission__task__community=c).select_related('reviewer__profile'):person(review.reviewer,snapshots.get(review.reviewer_id,''))['reviews']+=1
    for task in c.tasks.filter(status='approved'):
        sub=task.submissions.select_related('submitter__profile').first()
        if sub:person(sub.submitter,snapshots.get(sub.submitter_id,''))['approved']+=1
    return render(request,'communities/contributions.html',{'community':c,'page_title':'Recorded contributions','people':sorted(people.values(),key=lambda p:(p['name'].lower(),p['id']))})
