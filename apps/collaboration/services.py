import hashlib
from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from apps.communities.models import Community,CommunityEvent
from apps.communities.permissions import can_enter,can_edit
from apps.projects.models import Project
from apps.core.permissions import require_permission
from apps.notifications.services import notify
from .models import ChatMessage,ChatAttachment,Poll,PollOption,PollVote,Announcement,AnnouncementRevision
from .uploads import inspect_upload

def lock(user,pk,edit=False):
    project_id=Community.objects.values_list('project_id',flat=True).get(pk=pk)
    Project.objects.filter(pk=project_id).update(revision=F('revision'))
    c=Community.objects.select_related('project').get(pk=pk)
    require_permission((can_edit if edit else can_enter)(user,c.project))
    return c

def send(user,pk,key,text='',files=(),reply=None,question='',options=()):
    stored=[]
    try:
        with transaction.atomic():
            c=lock(user,pk)
            existing=ChatMessage.objects.filter(community=c,sender=user,request_key=key).first()
            if existing:return existing
            text=text.strip();question=question.strip();options=[o.strip() for o in options if o.strip()]
            if len(text)>10000 or len(question)>300:raise ValidationError('Message or poll question is too long.')
            if not text and not files and not question:raise ValidationError('Write a message, attach a file or create a poll.')
            if len(files)>5 or sum(f.size for f in files)>60*1024*1024:raise ValidationError('Send up to 5 files and 60 MB total per message.')
            if question and (not 2<=len(options)<=10 or len({o.casefold() for o in options})!=len(options) or any(len(o)>160 for o in options)):
                raise ValidationError('A poll needs 2–10 different options, each up to 160 characters.')
            parent=ChatMessage.objects.filter(community=c,pk=reply).first() if reply else None
            require_permission(not reply or parent is not None)
            inspected=[inspect_upload(f) for f in files]
            m=ChatMessage.objects.create(community=c,sender=user,sender_name=user.profile.name,text=text,reply_to=parent,request_key=key)
            for name,kind,mime,raw in inspected:
                a=ChatAttachment(message=m,filename=name,kind=kind,mime=mime,size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
                a.file.save('attachment'+name[name.rfind('.'):].lower(),ContentFile(raw),save=False);stored.append(a.file);a.save()
            if question:
                poll=Poll.objects.create(message=m,question=question)
                PollOption.objects.bulk_create([PollOption(poll=poll,text=option,order=i) for i,option in enumerate(options)])
            return m
    except Exception:
        for file in stored:file.storage.delete(file.name)
        raise

@transaction.atomic
def vote(user,pk,poll_id,option_id):
    c=lock(user,pk);poll=Poll.objects.filter(pk=poll_id,message__community=c).first();require_permission(poll is not None)
    if poll.closed:raise ValidationError('This poll is closed.')
    option=PollOption.objects.filter(pk=option_id,poll=poll).first();require_permission(option is not None)
    PollVote.objects.update_or_create(poll=poll,voter=user,defaults={'option':option})
    return poll

@transaction.atomic
def close_poll(user,pk,poll_id):
    c=lock(user,pk);poll=Poll.objects.select_related('message').filter(pk=poll_id,message__community=c).first();require_permission(poll is not None)
    require_permission(poll.message.sender_id==user.pk or can_edit(user,c.project))
    poll.closed=True;poll.save(update_fields=['closed']);return poll

@transaction.atomic
def announce(user,pk,key,title,body,record_id=None,revision=0):
    c=lock(user,pk,edit=True)
    old=AnnouncementRevision.objects.filter(request_key=key).first()
    if old:
        require_permission(old.actor_id==user.pk and old.announcement.community_id==c.pk)
        return old.announcement
    title=title.strip();body=body.strip()
    if not title or not body or len(title)>160 or len(body)>10000:raise ValidationError('Provide a title (up to 160 characters) and message (up to 10,000).')
    a=Announcement.objects.filter(pk=record_id,community=c).first() if record_id else Announcement(community=c,author=user)
    require_permission(a is not None)
    if record_id and a.revision!=revision:raise ValidationError('The announcement changed. Reload before saving.')
    a.title=title;a.message=body
    if record_id:a.revision+=1
    a.save();r=AnnouncementRevision.objects.create(announcement=a,actor=user,title=title,message=body,request_key=key)
    CommunityEvent.objects.create(community=c,actor=user,action='announcement_updated' if record_id else 'announcement_published',details={'title':title,'announcement_id':a.pk},request_key=key)
    people={m.user_id:m.user for m in c.memberships.select_related('user')};people[c.project.mentor_id]=c.project.mentor
    for member in people.values():
        if member.pk!=user.pk and can_enter(member,c.project):notify(member,f'announcement:{r.pk}','Project announcement updated' if record_id else 'New project announcement', 'Open your community announcements to read the update.',c.project)
    return a
