import uuid,hashlib
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils import timezone
from django.shortcuts import get_object_or_404
from apps.collaboration.services import lock
from apps.collaboration.uploads import inspect_upload
from apps.communities.models import CommunityEvent
from apps.communities.permissions import can_edit,can_enter
from apps.recruitment.permissions import can_review_applications
from apps.core.permissions import require_permission
from apps.notifications.services import notify
from .models import Completion,IPUpdate,Achievement

def perform(user,pk,action,data,record_id=None):
    stored=None
    try:
        with transaction.atomic():
            c=lock(user,pk)
            mentor=can_review_applications(user,c.project)
            require_permission(can_edit(user,c.project) if action=='request' else mentor)
            old=CommunityEvent.objects.filter(request_key=data['key']).first()
            if old:
                require_permission(old.actor_id==user.pk and old.community_id==c.pk and old.action=='outcome_'+action and old.details.get('target')==record_id)
                return
            details={'target':record_id}
            if action in ('request','complete','reopen'):
                state,_=Completion.objects.get_or_create(community=c)
                if state.revision!=data['revision']:raise ValidationError('The completion record changed. Reload before continuing.')
                if action=='request' and state.state!='active':raise ValidationError('Completion is already requested or confirmed.')
                if action=='complete' and state.state=='completed':raise ValidationError('The project is already completed.')
                if action=='reopen' and state.state=='active':raise ValidationError('The project is already active.')
                if not data.get('confirm'):raise ValidationError('Confirm this action first.')
                details.update(previous=state.state,note=data['note'],previous_completed_at=str(state.completed_at or ''),previous_confirmer=state.confirmed_by_id)
                state.state={'request':'requested','complete':'completed','reopen':'active'}[action];state.note=data['note'];state.revision+=1
                if action=='complete':
                    state.completed_at=timezone.now();state.confirmed_by=user;c.project.status='closed';c.project.revision+=1;c.project.save(update_fields=['status','revision'])
                elif action=='reopen':state.completed_at=None;state.confirmed_by=None
                state.save();details['state']=state.state
            elif action=='ip':
                task=data.get('task');require_permission(not task or task.community_id==c.pk)
                update=IPUpdate(community=c,author=user,author_name=user.profile.name,**{f:data.get(f) for f in ['title','status_label','message','required_information','reference','task']})
                if data.get('file'):
                    name,kind,mime,raw=inspect_upload(data['file']);update.filename=name;update.mime=mime;update.sha256=hashlib.sha256(raw).hexdigest()
                    update.file.save(str(uuid.uuid4())+name[name.rfind('.'):],ContentFile(raw),save=False);stored=update.file
                update.full_clean();update.save();details.update(title=update.title,status=update.status_label,update_id=str(update.pk))
            elif action=='achievement':
                if not data.get('confirm'):raise ValidationError('Explicit approval for shared display is required.')
                if data['milestone_date']>timezone.localdate():raise ValidationError('A milestone cannot be in the future.')
                record=Achievement(community=c,approved_by=user,**{f:data[f] for f in ['title','status_label','public_summary','milestone_date']});record.full_clean();record.save();details.update(achievement_id=record.pk,title=record.title)
            elif action=='withdraw':
                record=get_object_or_404(Achievement,pk=record_id,community=c);record.visible=False;record.save(update_fields=['visible']);details['achievement_id']=record.pk
            else:raise ValidationError('Unknown outcome action.')
            CommunityEvent.objects.create(community=c,actor=user,request_key=data['key'],action='outcome_'+action,details=details)
            for m in c.memberships.select_related('user'):
                if m.user_id!=user.pk and can_enter(m.user,c.project):notify(m.user,f'outcome:{data["key"]}',{'ip':'Private IP progress updated','request':'Project completion requested','complete':'Project completion confirmed','reopen':'Project reopened','achievement':'Shareable achievement approved','withdraw':'Shared achievement withdrawn'}[action],'Open your community IP Progress page for details.',c.project)
    except Exception:
        if stored:stored.storage.delete(stored.name)
        raise
