
from datetime import timedelta
from unittest.mock import patch
from django.conf import settings
from django.core import mail
from django.test import TestCase, Client, override_settings
from django.utils import timezone
from .models import User, OTPChallenge
from .services import request_code, verify_code, AuthenticationError

@override_settings(DEBUG=True, AUTHENTICATION_MODE='demo')
class AuthenticationWorkflowTests(TestCase):
    email = 'demo.student@rbunagpur.in'
    def test_account_created_only_after_verification_and_onboarding_gate(self):
        self.client.post('/accounts/login/', {'email': self.email})
        self.assertFalse(User.objects.exists())
        response = self.client.post('/accounts/verify/', {'code':'123456'})
        self.assertRedirects(response, '/dashboard/', fetch_redirect_response=False)
        self.assertRedirects(self.client.get('/dashboard/'), '/profile/')
        user = User.objects.get()
        self.assertTrue(user.is_demo)
        self.assertIsNone(user.email_verified_at)

    def test_personal_and_lookalike_emails_rejected(self):
        for email in ['a@gmail.com','a@rbunagpur.in.example.com','bad']:
            self.client.post('/accounts/login/', {'email': email})
        self.assertFalse(OTPChallenge.objects.exists())

    def test_any_college_email_can_use_local_demo_but_real_records_are_protected(self):
        challenge = request_code('new.researcher@rbunagpur.in','binding','ip')
        user, _ = verify_code(challenge.pk, 'binding', '123456')
        self.assertTrue(user.is_demo)
        self.assertIsNone(user.email_verified_at)
        User.objects.create_user(self.email)
        with self.assertRaises(AuthenticationError):
            request_code(self.email,'binding','ip')

    def test_expired_and_used_codes_fail(self):
        challenge = request_code(self.email,'binding','ip')
        OTPChallenge.objects.filter(pk=challenge.pk).update(expires_at=timezone.now()-timedelta(seconds=1))
        self.assertIsNone(verify_code(challenge.pk,'binding','123456')[0])
        OTPChallenge.objects.filter(pk=challenge.pk).update(expires_at=timezone.now()+timedelta(minutes=1))
        self.assertIsNotNone(verify_code(challenge.pk,'binding','123456')[0])
        self.assertIsNone(verify_code(challenge.pk,'binding','123456')[0])

    def test_five_wrong_attempts_lock_challenge(self):
        challenge = request_code(self.email,'binding','ip')
        for _ in range(5):
            self.assertIsNone(verify_code(challenge.pk,'binding','000000')[0])
        self.assertIsNone(verify_code(challenge.pk,'binding','123456')[0])
        self.assertFalse(User.objects.exists())

    def test_wrong_browser_cannot_consume_challenge(self):
        challenge = request_code(self.email,'binding','ip')
        self.assertIsNone(verify_code(challenge.pk,'other','123456')[0])
        self.assertIsNotNone(verify_code(challenge.pk,'binding','123456')[0])

    def test_cooldown_replacement_and_request_limit(self):
        old = request_code(self.email,'binding','ip')
        with self.assertRaises(AuthenticationError):
            request_code(self.email,'binding','ip')
        for _ in range(4):
            OTPChallenge.objects.filter(email=self.email).update(created_at=timezone.now()-timedelta(seconds=61))
            request_code(self.email,'binding','ip')
        self.assertIsNone(verify_code(old.pk,'binding','123456')[0])
        OTPChallenge.objects.filter(email=self.email).update(created_at=timezone.now()-timedelta(seconds=61))
        with self.assertRaises(AuthenticationError):
            request_code(self.email,'binding','ip')

    @override_settings(DEBUG=False)
    def test_demo_disabled_in_production(self):
        with self.assertRaises(AuthenticationError):
            request_code(self.email,'binding','ip')

    def test_csrf_and_post_only_logout(self):
        csrf_client = Client(enforce_csrf_checks=True)
        self.assertEqual(csrf_client.post('/accounts/login/', {'email': self.email}).status_code,403)
        self.assertEqual(self.client.get('/accounts/logout/').status_code,405)

    @override_settings(AUTHENTICATION_MODE='real', EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch('apps.accounts.services.secrets.randbelow', return_value=654321)
    def test_real_mode_uses_random_code_and_verification_timestamp(self, random_code):
        challenge = request_code('real@rbunagpur.in','binding','ip')
        self.assertEqual(len(mail.outbox),1)
        self.assertIn('654321',mail.outbox[0].body)
        self.assertNotIn('654321',challenge.code_digest)
        self.assertIsNone(verify_code(challenge.pk,'binding','123456')[0])
        user,_ = verify_code(challenge.pk,'binding','654321')
        self.assertIsNotNone(user.email_verified_at)
        self.assertFalse(user.is_demo)

    @override_settings(AUTHENTICATION_MODE='real', EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch('apps.accounts.services.send_mail', side_effect=RuntimeError('private provider error'))
    def test_failed_delivery_cannot_leave_valid_challenge(self, send):
        with self.assertRaises(AuthenticationError):
            request_code('real@rbunagpur.in','binding','ip')
        self.assertTrue(OTPChallenge.objects.get().consumed)
        self.assertFalse(User.objects.exists())
