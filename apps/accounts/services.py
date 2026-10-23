"""Roster-only authentication and password-reset challenges."""
import secrets
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.utils.crypto import salted_hmac, constant_time_compare
from django.views.decorators.debug import sensitive_variables
from .models import User, OTPChallenge, AuthThrottle
from .validators import normalise_college_email

class AuthenticationError(Exception):
    pass

def digest(value):
    return salted_hmac('researchbridge.otp', str(value), algorithm='sha256').hexdigest()

def demo_mode():
    return settings.AUTHENTICATION_MODE == 'demo' and settings.DEBUG

def registered_user(email):
    if settings.AUTHENTICATION_MODE not in {'demo', 'real'}:
        return None
    if settings.AUTHENTICATION_MODE == 'demo' and not demo_mode():
        return None
    return User.objects.filter(email=email, is_active=True, roster_role__in=['student','teacher'],
                               is_demo=(settings.AUTHENTICATION_MODE == 'demo')).first()

def rate_limit(scope, email, ip, email_limit=5, ip_limit=30):
    now = timezone.now()
    exceeded = False
    with transaction.atomic():
        for key, limit in [(digest(scope+':ip:'+ip),ip_limit),(digest(scope+':email:'+email),email_limit)]:
            row,_ = AuthThrottle.objects.get_or_create(key=key,defaults={'started_at':now})
            AuthThrottle.objects.filter(pk=key).update(count=F('count')+1)
            row.refresh_from_db()
            if now-row.started_at >= timedelta(minutes=15):
                row.count=1; row.started_at=now; row.save(update_fields=['count','started_at'])
            exceeded = exceeded or row.count>limit
    if exceeded:
        raise AuthenticationError('Too many attempts. Please wait 15 minutes before trying again.')

@sensitive_variables()
def password_login(request, email, password):
    email=normalise_college_email(email)
    rate_limit('login',email,request.META.get('REMOTE_ADDR','unknown'),10,60)
    user=authenticate(request,email=email,password=password)
    if not user or not registered_user(email):
        raise AuthenticationError('Email or password is incorrect, or the account is not registered.')
    return user

@sensitive_variables()
def request_code(email, binding, ip):
    if not settings.PASSWORD_RESET_ENABLED:
        raise AuthenticationError('Password reset by email is unavailable. Contact the project administrator.')
    email=normalise_college_email(email)
    rate_limit('reset',email,ip)
    user=registered_user(email)
    if not user:
        return None
    mode=settings.AUTHENTICATION_MODE
    if mode=='real' and settings.EMAIL_BACKEND not in {'django.core.mail.backends.smtp.EmailBackend','django.core.mail.backends.locmem.EmailBackend'}:
        raise AuthenticationError('Password reset email delivery is not configured.')
    now=timezone.now()
    with transaction.atomic():
        # Lock account before replacement, including on SQLite.
        User.objects.filter(pk=user.pk).update(last_login=F('last_login'))
        latest=OTPChallenge.objects.filter(email=email).order_by('-created_at').first()
        if latest and (now-latest.created_at).total_seconds()<60:
            raise AuthenticationError('Please wait 60 seconds between code requests.')
        OTPChallenge.objects.filter(email=email,consumed=False).update(consumed=True)
        code='123456' if demo_mode() else f'{secrets.randbelow(1000000):06d}'
        challenge=OTPChallenge(email=email,binding=digest(binding),mode=mode,created_at=now,expires_at=now+timedelta(minutes=3))
        # Bind reset to the current password as well as the browser and challenge.
        challenge.code_digest=digest(f'{challenge.id}:{email}:{user.password}:{code}')
        challenge.save()
    if mode=='real':
        try:
            sent=send_mail('Reset your ResearchBridge password',f'Your password-reset code is {code}. It expires in three minutes. If you did not request it, ignore this email.',settings.DEFAULT_FROM_EMAIL,[email],fail_silently=False)
            if sent!=1:
                raise RuntimeError('Delivery not accepted')
        except Exception:
            OTPChallenge.objects.filter(pk=challenge.pk).update(consumed=True)
            raise AuthenticationError('The reset email could not be sent. Please try again later.') from None
    return challenge

@sensitive_variables()
def verify_code(challenge_id,binding,code):
    now=timezone.now(); user=None; error='This code is invalid or expired. Request a new code.'
    with transaction.atomic():
        rows=OTPChallenge.objects.filter(pk=challenge_id,binding=digest(binding),consumed=False,expires_at__gt=now,attempts__lt=5,mode=settings.AUTHENTICATION_MODE)
        if not rows.update(attempts=F('attempts')+1):
            return None,error
        challenge=OTPChallenge.objects.get(pk=challenge_id)
        candidate=registered_user(challenge.email)
        correct=candidate and constant_time_compare(challenge.code_digest,digest(f'{challenge.id}:{challenge.email}:{candidate.password}:{code}'))
        if correct:
            user=candidate; challenge.consumed=True
        else:
            left=5-challenge.attempts
            error=f'Incorrect code. {left} attempts remaining.' if left else 'Too many incorrect attempts. Request a new code.'
            challenge.consumed=not left
        challenge.save(update_fields=['consumed'])
    return user,error
