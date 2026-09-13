import uuid,hashlib
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from apps.collaboration.services import lock
from apps.collaboration.uploads import inspect_upload
from apps.communities.models import CommunityEvent,Sprint
from apps.communities.permissions import can_enter,can_edit
from apps.core.permissions import require_permission
from apps.notifications.services import notify
from .models import Task,TaskFile,Submission,Review,TaskComment

EDITABLE=('assigned','progress','changes')

def check_revision(task,data):
    if task.revision!=data['revision']:raise ValidationError('This task changed in another window. Reload before saving.')

def event(c,user,key,action,task,details=None):
    return CommunityEvent.objects.create(community=c,actor=user,request_key=key,action=action,details={'task_id':str(task.pk),'title':task.title,**(details or {})})

def replay(c,user,key,action,task_id=None):
    old=CommunityEvent.objects.filter(request_key=key).first()
    if old:
        require_permission(old.community_id==c.pk and old.actor_id==user.pk and old.action==action and (task_id is None or old.details.get('task_id')==str(task_id)))
        return get_object_or_404(Task,pk=old.details['task_id'],community=c)

def alert(user,task,key,title):
    if can_enter(user,task.community.project):notify(user,f'task:{key}:{user.pk}',title,task.title,task.community.project)

@transaction.atomic
def save_task(user,pk,data,task_id=None):
    c=lock(user,pk,edit=True);old=replay(c,user,data['key'],'task_saved',task_id)
    if old:return old
    t=get_object_or_404(Task,pk=task_id,community=c) if task_id else Task(community=c,created_by=user)
    if task_id:
        check_revision(t,data)
        if t.status not in EDITABLE:raise ValidationError('Request changes or reopen approved work before editing its assignment or scope.')
    require_permission(can_enter(data['assignee'],c.project))
    sprint=data.get('sprint')
    require_permission(not sprint or Sprint.objects.filter(pk=sprint.pk,community=c).exists())
    before={f:str(getattr(t,f,None)) for f in ['title','description','assignee_id','sprint_id','due_date','milestone']}
    previous=t.assignee_id
    for field in ['title','description','milestone','assignee','sprint','due_date']:setattr(t,field,data.get(field))
    if task_id:t.revision+=1
    if previous and previous!=t.assignee_id:t.status='assigned';t.blocker='';t.progress_notes=''
    t.full_clean();t.save()
    event(c,user,data['key'],'task_saved',t,{'before':before,'after':{f:str(getattr(t,f)) for f in before}})
    if not task_id or previous!=t.assignee_id:alert(t.assignee,t,data['key'],'Research task assigned')
    return t

def act(user,pk,task_id,action,data,uploads=()):
    stored=[]
    try:
        with transaction.atomic():
            c=lock(user,pk);t=get_object_or_404(Task.objects.select_related('assignee'),pk=task_id,community=c)
            old=replay(c,user,data['key'],'task_'+action,task_id)
            if old:return old
            check_revision(t,data)
            details={}
            if action in ('work','submit'):
                require_permission(t.assignee_id==user.pk)
                if t.status not in EDITABLE:raise ValidationError('This work is awaiting review or already approved. It cannot be changed now.')
                if len(uploads)>5 or sum(f.size for f in uploads)>60*1024*1024:raise ValidationError('Use up to 5 files, 25 MB each and 60 MB total.')
                selected=list(data.get('evidence',[]))
                require_permission(all(f.task_id==t.pk for f in selected))
                for upload in uploads:
                    name,kind,mime,raw=inspect_upload(upload)
                    f=TaskFile(task=t,uploader=user,filename=name,mime=mime,size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
                    f.file.save(str(uuid.uuid4())+name[name.rfind('.'):],ContentFile(raw),save=False);stored.append(f.file);f.save();selected.append(f)
                t.progress_notes=data['summary'];t.blocker=data.get('blocker','')
                details={'summary':t.progress_notes,'blocker':t.blocker,'files':[str(f.pk) for f in selected]}
                if action=='work':t.status='progress' if t.status=='assigned' else t.status
                else:
                    if t.blocker:raise ValidationError('Resolve or clear the blocker before submitting for approval.')
                    n=(t.submissions.first().number if t.submissions.exists() else 0)+1
                    sub=Submission.objects.create(task=t,submitter=user,number=n,summary=t.progress_notes);sub.files.set(selected)
                    t.status='submitted';details['submission_id']=sub.pk
                    for person in [c.project.mentor,c.leader]:
                        if person and person.pk!=user.pk and can_edit(person,c.project):alert(person,t,data['key'],'Task ready for review')
            elif action=='review':
                require_permission(can_edit(user,c.project) and t.assignee_id!=user.pk)
                sub=get_object_or_404(Submission,pk=data['submission'],task=t)
                require_permission(sub.submitter_id!=user.pk)
                if t.status!='submitted' or t.submissions.first().pk!=sub.pk or hasattr(sub,'review'):raise ValidationError('This submission is no longer awaiting review.')
                if data['decision'] not in ('approved','changes') or not data['feedback'].strip():raise ValidationError('Choose a review decision and provide feedback.')
                Review.objects.create(submission=sub,reviewer=user,decision=data['decision'],feedback=data['feedback'])
                t.status=data['decision'];details={'submission_id':sub.pk,'decision':data['decision'],'feedback':data['feedback']}
                alert(t.assignee,t,data['key'],'Task approved' if t.status=='approved' else 'Task changes requested')
            elif action=='reopen':
                require_permission(can_edit(user,c.project))
                if t.status!='approved':raise ValidationError('Only approved tasks can be reopened.')
                t.status='changes';details={'reason':data['feedback']};alert(t.assignee,t,data['key'],'Approved task reopened')
            elif action=='comment':
                f=data.get('file');require_permission(not f or f.task_id==t.pk)
                comment=TaskComment.objects.create(task=t,author=user,file=f,body=data['body']);details={'comment_id':comment.pk,'file_id':str(f.pk) if f else None,'body':data['body']}
            else:raise ValidationError('Unknown task action.')
            t.revision+=1;t.full_clean();t.save();event(c,user,data['key'],'task_'+action,t,details)
            return t
    except Exception:
        for f in stored:f.storage.delete(f.name)
        raise
