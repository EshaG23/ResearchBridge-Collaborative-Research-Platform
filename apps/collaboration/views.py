import re
import uuid
from pathlib import Path
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import DatabaseError
from django.db.models import Count,Q
from django.http import JsonResponse,Http404,FileResponse,StreamingHttpResponse,HttpResponse
from django.shortcuts import get_object_or_404,render,redirect
from django.template.loader import render_to_string
from django.middleware.csrf import get_token
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET,require_POST,require_http_methods
from apps.communities.views import accessible
from apps.communities.permissions import can_edit
from apps.core.permissions import require_permission
from .models import ChatMessage,ChatAttachment,Poll,Announcement
from .services import send,vote,close_poll,announce

class AnnouncementForm(forms.Form):
    title=forms.CharField(max_length=160)
    message=forms.CharField(max_length=10000,widget=forms.Textarea(attrs={'rows':9}))
    key=forms.UUIDField(initial=uuid.uuid4,widget=forms.HiddenInput)
    revision=forms.IntegerField(initial=0,widget=forms.HiddenInput)

def number(value,default=0):
    try:return max(0,min(int(value),9223372036854775807))
    except (ValueError,TypeError):return default

def query(c):
    return c.chat_messages.select_related('sender','reply_to','poll').prefetch_related('attachments')

def poll_context(poll,user):
    opts=list(poll.options.annotate(count=Count('votes')))
    chosen=poll.votes.filter(voter=user).values_list('option_id',flat=True).first()
    total=sum(o.count for o in opts)
    for o in opts:o.chosen=o.pk==chosen;o.percent=round(100*o.count/total) if total else 0
    return {'poll':poll,'options':opts,'total':total,'can_close':poll.message.sender_id==user.pk or can_edit(user,poll.message.community.project)}

def message_html(m,request):
    poll=getattr(m,'poll',None)
    return render_to_string('collaboration/message.html',{'m':m,**(poll_context(poll,request.user) if poll else {})},request=request)

@login_required
@never_cache
@require_GET
def chat(request,pk):
    c=accessible(request,pk)
    items=list(query(c).order_by('-pk')[:40]);items.reverse()
    return render(request,'collaboration/chat.html',{'page_title':'Internal Chat','community':c,
        'messages_html':''.join(message_html(m,request) for m in items),'latest':items[-1].pk if items else 0,
        'oldest':items[0].pk if items else 0,'older':bool(items and c.chat_messages.filter(pk__lt=items[0].pk).exists())})

@login_required
@never_cache
@require_GET
def feed(request,pk):
    c=accessible(request,pk);after=number(request.GET.get('after'));before=number(request.GET.get('before'))
    if before:items=list(query(c).filter(pk__lt=before).order_by('-pk')[:40]);items.reverse()
    else:items=list(query(c).filter(pk__gt=after).order_by('pk')[:40])
    ids=[number(v) for v in request.GET.get('polls','').split(',')[:100]]
    polls={str(p.pk):render_to_string('collaboration/poll.html',poll_context(p,request.user),request=request) for p in Poll.objects.filter(pk__in=ids,message__community=c).select_related('message__community__project')}
    return JsonResponse({'user_id':str(request.user.pk),'csrf_token':get_token(request),'messages':[{'id':m.pk,'html':message_html(m,request)} for m in items],
        'older':bool(items and c.chat_messages.filter(pk__lt=items[0].pk).exists()),'polls':polls})

@login_required
@never_cache
@require_POST
def post(request,pk):
    accessible(request,pk)
    if request.headers.get('X-Chat-User') not in (None,str(request.user.pk)):
        return JsonResponse({'error':'The signed-in account changed in another tab. Reload this chat before continuing.','code':'account_changed'},status=409)
    try:
        key=uuid.UUID(request.POST.get('key',''))
        m=send(request.user,pk,key,request.POST.get('text',''),request.FILES.getlist('files'),number(request.POST.get('reply')) or None,
            request.POST.get('question',''),request.POST.get('options','').splitlines())
        return JsonResponse({'id':m.pk,'html':message_html(query(m.community).get(pk=m.pk),request)})
    except (ValueError,ValidationError) as exc:return JsonResponse({'error':' '.join(exc.messages) if isinstance(exc,ValidationError) else 'Invalid send confirmation. Reload the page.'},status=400)
    except (DatabaseError,OSError):return JsonResponse({'error':'Message could not be saved. Retry with your draft unchanged.'},status=503)

@login_required
@never_cache
@require_POST
def poll_action(request,pk,poll_id):
    accessible(request,pk)
    if request.headers.get('X-Chat-User') not in (None,str(request.user.pk)):
        return JsonResponse({'error':'The signed-in account changed in another tab. Reload this chat before continuing.','code':'account_changed'},status=409)
    try:
        action=request.POST.get('action','vote')
        poll=close_poll(request.user,pk,poll_id,closed=action=='close') if action in ('close','reopen') else vote(request.user,pk,poll_id,number(request.POST.get('option')))
        return JsonResponse({'poll':render_to_string('collaboration/poll.html',poll_context(poll,request.user),request=request)})
    except ValidationError as exc:return JsonResponse({'error':' '.join(exc.messages)},status=400)
    except DatabaseError:return JsonResponse({'error':'Vote could not be saved. Please retry.'},status=503)

@login_required
@never_cache
@require_GET
def media(request,pk):
    c=accessible(request,pk);kind=request.GET.get('kind','all');term=request.GET.get('q','')[:150]
    attachments=ChatAttachment.objects.filter(message__community=c).select_related('message')
    if kind in ('image','audio','video','document'):attachments=attachments.filter(kind=kind)
    if term:attachments=attachments.filter(Q(filename__icontains=term)|Q(message__text__icontains=term))
    links=c.chat_messages.filter(Q(text__icontains='https://')|Q(text__icontains='http://')).filter(text__icontains=term).order_by('-pk')
    page=Paginator(links if kind=='links' else attachments.order_by('-message_id','pk'),24).get_page(request.GET.get('page'))
    return render(request,'collaboration/media.html',{'community':c,'page_title':'Chat media','page':page,'kind':kind,'term':term})

@login_required
@never_cache
@require_http_methods(['GET','HEAD'])
def attachment(request,pk,attachment_id):
    c=accessible(request,pk);a=get_object_or_404(ChatAttachment,pk=attachment_id,message__community=c)
    path=Path(a.file.path).resolve()
    if not path.is_relative_to(Path(a.file.storage.location).resolve()) or not path.is_file():raise Http404
    size=path.stat().st_size;inline=a.kind in ('image','audio','video') and request.GET.get('download')!='1'
    start,end=0,size-1;partial=False
    header=request.headers.get('Range','') if inline else ''
    if header:
        match=re.fullmatch(r'bytes=(\d*)-(\d*)',header)
        if not match or not any(match.groups()):return HttpResponse(status=416,headers={'Content-Range':f'bytes */{size}'})
        left,right=match.groups()
        if left:start=int(left);end=min(int(right),end) if right else end
        else:start=max(0,size-int(right))
        if start>end or start>=size:return HttpResponse(status=416,headers={'Content-Range':f'bytes */{size}'})
        partial=True
    if request.method=='HEAD':response=HttpResponse(content_type=a.mime)
    elif partial:
        def chunks():
            with path.open('rb') as f:
                f.seek(start);remaining=end-start+1
                while remaining:
                    chunk=f.read(min(65536,remaining))
                    if not chunk:break
                    remaining-=len(chunk);yield chunk
        response=StreamingHttpResponse(chunks(),status=206,content_type=a.mime)
    else:response=FileResponse(path.open('rb'),as_attachment=not inline,filename=a.filename,content_type=a.mime)
    if partial:response.status_code=206;response['Content-Range']=f'bytes {start}-{end}/{size}'
    response['Content-Length']=str(end-start+1);response['Accept-Ranges']='bytes'
    response['Cache-Control']='private, no-store';response['X-Content-Type-Options']='nosniff';response['Content-Security-Policy']="sandbox; default-src 'none'"
    return response

@login_required
@never_cache
@require_GET
def announcements(request,pk):
    c=accessible(request,pk)
    return render(request,'collaboration/announcements.html',{'community':c,'page_title':'Announcements','can_edit':can_edit(request.user,c.project),
        'page':Paginator(c.announcements.select_related('author__profile').prefetch_related('history__actor__profile'),15).get_page(request.GET.get('page'))})

@login_required
@never_cache
@require_http_methods(['GET','POST'])
def announcement_edit(request,pk,record_id=None):
    c=accessible(request,pk);require_permission(can_edit(request.user,c.project))
    record=get_object_or_404(Announcement,community=c,pk=record_id) if record_id else None
    form=AnnouncementForm(request.POST or None,initial={'title':record.title,'message':record.message,'revision':record.revision} if record else {})
    if request.method=='POST' and form.is_valid():
        try:announce(request.user,pk,form.cleaned_data['key'],form.cleaned_data['title'],form.cleaned_data['message'],record_id,form.cleaned_data['revision'])
        except ValidationError as exc:form.add_error(None,' '.join(exc.messages))
        except DatabaseError:form.add_error(None,'The announcement could not be saved. Please retry.')
        else:return redirect('collaboration:announcements',pk=pk)
    return render(request,'collaboration/announcement_form.html',{'community':c,'page_title':'Edit announcement' if record else 'New announcement','form':form})


def unread_context(user):
    from apps.communities.models import Community
    from apps.communities.permissions import can_enter
    from .models import ChatReadState
    seen=dict(ChatReadState.objects.filter(user=user).values_list('community_id','last_message_id'))
    chats=[]
    for c in Community.objects.filter(Q(project__mentor=user)|Q(memberships__user=user)).select_related('project').distinct():
        if not can_enter(user,c.project):continue
        count=c.chat_messages.filter(pk__gt=seen.get(c.pk,0)).exclude(sender=user).count()
        if count:chats.append({'community':c,'count':count})
    return {'chat_unread':sum(c['count'] for c in chats),'unread_chats':chats}

@login_required
@never_cache
@require_GET
def unread(request):
    return JsonResponse({'html':render_to_string('collaboration/unread.html',unread_context(request.user),request=request)})

@login_required
@never_cache
@require_POST
def mark_read(request,pk):
    from django.db import transaction
    from .services import lock
    from .models import ChatReadState
    with transaction.atomic():
        c=lock(request.user,pk)
        if request.headers.get('X-Chat-User')!=str(request.user.pk):return JsonResponse({'code':'account_changed'},status=409)
        last=number(request.POST.get('last'))
        if not c.chat_messages.filter(pk=last).exists():return JsonResponse({'error':'Message not found.'},status=400)
        state,_=ChatReadState.objects.get_or_create(community=c,user=request.user)
        if last>state.last_message_id:state.last_message_id=last;state.save(update_fields=['last_message_id'])
    return JsonResponse({'ok':True})
