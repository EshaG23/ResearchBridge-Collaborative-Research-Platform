from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_GET

@require_GET
def ui_preview(request, section="discover"):
    # Synthetic presentation only: no project or user records are queried.
    if not settings.DEBUG or section not in {"discover", "projects", "communities", "components"}:
        raise Http404
    labels = {"discover": "Discover projects", "projects": "My projects", "communities": "Communities", "components": "Interface components"}
    return render(request, "core/preview.html", {"section": section, "page_title": labels[section], "ui_preview": True})



from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

@login_required
@never_cache
@require_GET
def dashboard(request):
    from apps.projects.discovery import discovery_context
    from apps.core.permissions import can_create_idea, college_member, require_permission
    require_permission(college_member(request.user), conceal=False)
    from apps.collaboration.views import unread_context
    from apps.ip_progress.views import approved_achievements
    return render(request, 'core/dashboard.html', discovery_context(request) | unread_context(request.user) | {
        'achievements':approved_achievements(request.user),'page_title': 'Your workspace', 'profile': request.user.profile,
        'can_create': can_create_idea(request.user)})

@require_GET
@never_cache
def health(request):
    from django.db import connection,DatabaseError
    from django.http import JsonResponse
    try:
        with connection.cursor() as cursor:cursor.execute('SELECT 1')
    except DatabaseError:return JsonResponse({'status':'unavailable'},status=503)
    return JsonResponse({'status':'ok'})
