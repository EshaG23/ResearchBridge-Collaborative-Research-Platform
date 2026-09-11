import secrets
from uuid import UUID
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.debug import sensitive_post_parameters
from .forms import EmailForm, CodeForm
from .models import OTPChallenge
from .services import request_code, verify_code, AuthenticationError, digest, demo_mode

@never_cache
@sensitive_post_parameters('code')
@require_http_methods(['GET', 'POST'])
def sign_in(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = EmailForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        binding = request.session.get('otp_binding') or secrets.token_urlsafe(32)
        request.session['otp_binding'] = binding
        try:
            challenge = request_code(form.cleaned_data['email'], binding, request.META.get('REMOTE_ADDR', 'unknown'))
        except AuthenticationError as error:
            form.add_error(None, str(error))
        else:
            request.session['otp_challenge'] = str(challenge.id)
            return redirect('accounts:verify')
    return render(request, 'accounts/login.html', {'form': form, 'demo': demo_mode()})

def current_challenge(request):
    try:
        pk = UUID(request.session.get('otp_challenge', ''))
    except (ValueError, TypeError, AttributeError):
        return None
    return OTPChallenge.objects.filter(pk=pk, binding=digest(request.session.get('otp_binding', ''))).first()

@never_cache
@sensitive_post_parameters('code')
@require_http_methods(['GET', 'POST'])
def verify(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    challenge = current_challenge(request)
    if not challenge:
        return redirect('accounts:login')
    form = CodeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user, error = verify_code(challenge.id, request.session.get('otp_binding', ''), form.cleaned_data['code'])
        if user:
            request.session.pop('otp_challenge', None)
            request.session.pop('otp_binding', None)
            login(request, user)
            return redirect('dashboard')
        form.add_error(None, error)
        challenge.refresh_from_db()
    now = timezone.now()
    return render(request, 'accounts/verify.html', {'form': form, 'challenge': challenge,
        'demo': challenge.mode == 'demo', 'remaining': max(0, int((challenge.expires_at-now).total_seconds())),
        'cooldown': max(0, 60-int((now-challenge.created_at).total_seconds()))})

@require_POST
@never_cache
def resend(request):
    challenge = current_challenge(request)
    if not challenge:
        return redirect('accounts:login')
    try:
        replacement = request_code(challenge.email, request.session.get('otp_binding', ''), request.META.get('REMOTE_ADDR', 'unknown'))
        request.session['otp_challenge'] = str(replacement.id)
        messages.success(request, 'A new demo challenge is ready.' if demo_mode() else 'A new code has been sent.')
    except AuthenticationError as error:
        messages.error(request, str(error))
    return redirect('accounts:verify')

@require_POST
def sign_out(request):
    logout(request)
    messages.success(request, 'You have signed out. Your saved work is retained.')
    return redirect('accounts:login')
