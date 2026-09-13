import secrets
from uuid import UUID
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from django.db import transaction
from django.db.models import F
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.debug import sensitive_post_parameters
from .forms import LoginForm, EmailForm, CodeForm
from .models import OTPChallenge, User
from .services import password_login, request_code, verify_code, registered_user, AuthenticationError, digest, demo_mode

@never_cache
@sensitive_post_parameters('password')
@require_http_methods(['GET','POST'])
def sign_in(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form=LoginForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        try:
            user=password_login(request,form.cleaned_data['email'],form.cleaned_data['password'])
        except AuthenticationError as error:
            form.add_error(None,str(error))
        else:
            login(request,user)
            request.session.pop('reset_grant',None)
            return redirect('dashboard')
    return render(request,'accounts/login.html',{'form':form,'demo':demo_mode()})

@never_cache
@require_http_methods(['GET','POST'])
def forgot(request):
    form=EmailForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        request.session.pop('reset_grant',None)
        binding=secrets.token_urlsafe(32)
        request.session['otp_binding']=binding
        request.session['reset_email']=form.cleaned_data['email']
        try:
            challenge=request_code(form.cleaned_data['email'],binding,request.META.get('REMOTE_ADDR','unknown'))
        except AuthenticationError as error:
            form.add_error(None,str(error))
        else:
            request.session['otp_challenge']=str(challenge.pk) if challenge else ''
            return redirect('accounts:verify')
    return render(request,'accounts/forgot.html',{'form':form,'demo':demo_mode()})

def current_challenge(request):
    try:
        pk=UUID(request.session.get('otp_challenge',''))
    except (ValueError,TypeError,AttributeError):
        return None
    return OTPChallenge.objects.filter(pk=pk,binding=digest(request.session.get('otp_binding',''))).first()

@never_cache
@sensitive_post_parameters('code')
@require_http_methods(['GET','POST'])
def verify(request):
    if not request.session.get('reset_email'):
        return redirect('accounts:forgot')
    challenge=current_challenge(request)
    form=CodeForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        user,error=verify_code(challenge.pk,request.session.get('otp_binding',''),form.cleaned_data['code']) if challenge else (None,'This code is invalid or expired.')
        if user:
            request.session['reset_grant']=signing.dumps({'user':user.pk,'token':default_token_generator.make_token(user)},salt='password-reset')
            request.session.pop('otp_challenge',None)
            return redirect('accounts:reset')
        form.add_error(None,error)
        if challenge:
            challenge.refresh_from_db()
    now=timezone.now()
    return render(request,'accounts/verify.html',{'form':form,'challenge':challenge,'demo':demo_mode(),
        'reset_email':request.session['reset_email'],
        'remaining':max(0,int((challenge.expires_at-now).total_seconds())) if challenge else 180,
        'cooldown':max(0,60-int((now-challenge.created_at).total_seconds())) if challenge else 60})

@require_POST
@never_cache
def resend(request):
    email=request.session.get('reset_email')
    if not email:
        return redirect('accounts:forgot')
    try:
        challenge=request_code(email,request.session.get('otp_binding',''),request.META.get('REMOTE_ADDR','unknown'))
        request.session['otp_challenge']=str(challenge.pk) if challenge else ''
        messages.success(request,'If this email is registered, a reset code is available in demo mode.' if demo_mode() else 'If this email is registered, a reset code has been sent.')
    except AuthenticationError as error:
        messages.error(request,str(error))
    return redirect('accounts:verify')

def reset_user(request):
    try:
        grant=signing.loads(request.session.get('reset_grant',''),salt='password-reset',max_age=600)
        user=User.objects.get(pk=grant['user'])
        if registered_user(user.email) and default_token_generator.check_token(user,grant['token']):
            return user
    except (signing.BadSignature,User.DoesNotExist,KeyError,TypeError,ValueError):
        pass
    return None

@never_cache
@sensitive_post_parameters('new_password1','new_password2')
@require_http_methods(['GET','POST'])
def reset_password(request):
    user=reset_user(request)
    if not user:
        messages.error(request,'Verify a new reset code before changing your password.')
        return redirect('accounts:forgot')
    form=SetPasswordForm(user,request.POST or None)
    if request.method=='POST' and form.is_valid():
        with transaction.atomic():
            User.objects.filter(pk=user.pk).update(last_login=F('last_login'))
            user=reset_user(request)
            if not user:
                return redirect('accounts:forgot')
            user.set_password(form.cleaned_data['new_password1']); user.save(update_fields=['password'])
            OTPChallenge.objects.filter(email=user.email,consumed=False).update(consumed=True)
        logout(request)
        messages.success(request,'Password updated. Sign in with your new password.')
        return redirect('accounts:login')
    return render(request,'accounts/reset.html',{'form':form})

@require_POST
def sign_out(request):
    logout(request)
    messages.success(request,'You have signed out. Your saved work is retained.')
    return redirect('accounts:login')


@never_cache
@require_http_methods(['GET'])
def new_demo_session(request):
    from django.conf import settings
    from django.http import Http404, HttpResponseRedirect
    if not settings.DEBUG or not demo_mode():
        raise Http404
    return HttpResponseRedirect('/demo/' + secrets.token_hex(16) + '/accounts/login/')
