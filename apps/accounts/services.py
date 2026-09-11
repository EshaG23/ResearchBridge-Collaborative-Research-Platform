"""Small-demo authentication operations; database writes serialize challenge consumption."""
import secrets
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.debug import sensitive_variables
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.utils.crypto import salted_hmac, constant_time_compare
from .models import User, OTPChallenge, AuthThrottle
from .validators import normalise_college_email

class AuthenticationError(Exception):
    pass

def digest(value):
    return salted_hmac('researchbridge.otp', str(value), algorithm='sha256').hexdigest()

def demo_mode():
    return settings.AUTHENTICATION_MODE == 'demo' and settings.DEBUG

@sensitive_variables()
def request_code(email, binding, ip):
    email = normalise_college_email(email)
    mode = settings.AUTHENTICATION_MODE
    if mode == 'demo':
        if not demo_mode() or email not in settings.DEMO_IDENTITIES:
            raise AuthenticationError('Demo access is limited to the listed demonstration identities.')
    elif mode != 'real':
        raise AuthenticationError('Sign-in is not configured yet.')
    if mode == 'real' and settings.EMAIL_BACKEND not in {
        'django.core.mail.backends.smtp.EmailBackend', 'django.core.mail.backends.locmem.EmailBackend'
    }:
        raise AuthenticationError('Email delivery is not configured. Please contact the administrator.')
    existing = User.objects.filter(email=email).first()
    if existing and (not existing.is_active or existing.is_demo != (mode == 'demo')):
        raise AuthenticationError('This account is unavailable in the current authentication mode.')
    now = timezone.now()
    with transaction.atomic():
        # Lock by write (also effective on SQLite); counters do not require Redis.
        for key, limit in [(digest('ip:' + ip), 30), (digest('email:' + email), 5)]:
            throttle, _ = AuthThrottle.objects.get_or_create(key=key, defaults={'started_at': now})
            AuthThrottle.objects.filter(pk=key).update(count=F('count') + 1)
            throttle.refresh_from_db()
            if now - throttle.started_at >= timedelta(minutes=15):
                throttle.count = 1
                throttle.started_at = now
                throttle.save(update_fields=['count', 'started_at'])
            if throttle.count > limit:
                raise AuthenticationError('Too many requests. Please wait 15 minutes before trying again.')
        latest = OTPChallenge.objects.filter(email=email).order_by('-created_at').first()
        if latest and (now - latest.created_at).total_seconds() < 60:
            raise AuthenticationError('Please wait 60 seconds between code requests.')
        OTPChallenge.objects.filter(email=email, consumed=False).update(consumed=True)
        code = '123456' if mode == 'demo' else f'{secrets.randbelow(1000000):06d}'
        challenge = OTPChallenge(email=email, binding=digest(binding), mode=mode,
                                 created_at=now, expires_at=now + timedelta(minutes=3))
        challenge.code_digest = digest(f'{challenge.id}:{email}:{code}')
        challenge.save()
    if mode == 'real':
        try:
            sent = send_mail('Your ResearchBridge sign-in code',
                             f'Your sign-in code is {code}. It expires in three minutes. If you did not request it, ignore this email.',
                             settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
            if sent != 1:
                raise RuntimeError('Delivery not accepted')
        except Exception:
            OTPChallenge.objects.filter(pk=challenge.pk).update(consumed=True)
            # Never expose provider errors, message contents or credentials to logs/UI.
            raise AuthenticationError('The email could not be sent. Please wait a minute and try again.') from None
    return challenge

@sensitive_variables()
def verify_code(challenge_id, binding, code):
    now = timezone.now()
    user = None
    error = 'This code is invalid or expired. Request a new code.'
    with transaction.atomic():
        # First statement is a write, so concurrent verifications serialize on SQLite.
        eligible = OTPChallenge.objects.filter(pk=challenge_id, binding=digest(binding), consumed=False,
                                               expires_at__gt=now, attempts__lt=5,
                                               mode=settings.AUTHENTICATION_MODE)
        if not eligible.update(attempts=F('attempts') + 1):
            return None, error
        challenge = OTPChallenge.objects.get(pk=challenge_id)
        correct = constant_time_compare(challenge.code_digest, digest(f'{challenge.id}:{challenge.email}:{code}'))
        if challenge.mode == 'demo' and (not demo_mode() or challenge.email not in settings.DEMO_IDENTITIES):
            correct = False
        if correct:
            existing = User.objects.filter(email=challenge.email).first()
            if existing and (not existing.is_active or existing.is_demo != (challenge.mode == 'demo')):
                correct = False
        if correct:
            user, _ = User.objects.get_or_create(email=challenge.email, defaults={'is_demo': challenge.mode == 'demo'})
            if not user.password:
                user.set_unusable_password()
            if challenge.mode == 'real':
                user.email_verified_at = now
            user.save()
            challenge.consumed = True
        else:
            remaining = 5 - challenge.attempts
            error = f'Incorrect code. {remaining} attempts remaining.' if remaining else 'Too many incorrect attempts. Request a new code.'
            if not remaining:
                challenge.consumed = True
        challenge.save(update_fields=['consumed'])
    return user, error
