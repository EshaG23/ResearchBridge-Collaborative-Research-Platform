from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect

class ProfileGateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        if request.user.is_authenticated and not request.user.roster_role and not request.path.startswith('/admin/'):
            logout(request)
            return redirect('accounts:login')
        exempt = request.path.startswith(('/accounts/', '/profile/', '/admin/', '/static/'))
        preview = settings.DEBUG and request.path.startswith('/dev/ui/')
        if request.user.is_authenticated and not exempt and not preview:
            from .models import Profile
            if not Profile.objects.filter(user=request.user, completed_at__isnull=False).exists():
                return redirect('profiles:edit')
        return self.get_response(request)
