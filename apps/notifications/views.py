from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST
from .models import Notification
from .services import authorised_url

@login_required
@never_cache
@require_GET
def index(request):
    rows = request.user.notifications.select_related('project')
    if request.GET.get('filter') == 'unread':
        rows = rows.filter(read_at__isnull=True)
    page = Paginator(rows,20).get_page(request.GET.get('page'))
    for row in page:
        row.can_open = bool(authorised_url(row,request.user))
    return render(request,'notifications/index.html',{'page_title':'Notifications','page':page,'unread_only':request.GET.get('filter') == 'unread'})

@login_required
@never_cache
@require_GET
def poll(request):
    rows = request.user.notifications.select_related('project')[:8]
    return JsonResponse({'unread_count':request.user.notifications.filter(read_at__isnull=True).count(),
        'items':[{'id':row.pk,'title':row.title,'message':row.message,
                  'read':row.read_at is not None,'url':authorised_url(row,request.user)} for row in rows]})

@login_required
@never_cache
@require_POST
def read(request, pk):
    row = get_object_or_404(Notification.objects.select_related('project'),pk=pk,recipient=request.user)
    Notification.objects.filter(pk=row.pk,read_at__isnull=True).update(read_at=timezone.now())
    if request.POST.get('open') == '1':
        url = authorised_url(row,request.user)
        if url:
            return redirect(url)
        messages.info(request,'This destination is no longer available to your account.')
    return redirect('notifications:index')

@login_required
@never_cache
@require_POST
def read_all(request):
    request.user.notifications.filter(read_at__isnull=True).update(read_at=timezone.now())
    return redirect('notifications:index')

