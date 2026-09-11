
import json
import tempfile
from pathlib import Path
from datetime import timedelta
from unittest.mock import patch
from django.core import mail
from django.core.management import call_command
from django.test import TestCase, Client, override_settings
from django.utils import timezone
from .models import User, OTPChallenge
from .services import request_code, verify_code, AuthenticationError
from apps.profiles.models import Profile, Department

@override_settings(DEBUG=True, AUTHENTICATION_MODE='demo')
class AuthenticationWorkflowTests(TestCase):
    email='student@rbunagpur.in'
    password='ResearchStart!2026'
    def setUp(self):
        self.user=User.objects.create_user(self.email,self.password,is_demo=True,roster_role='student')
    def challenge(self):
        return request_code(self.email,'binding','ip')
    def login(self,client=None,password=None):
        return (client or self.client).post('/accounts/login/',{'email':self.email,'password':password or self.password})
    def reset_grant(self):
        self.client.post('/accounts/forgot-password/',{'email':self.email})
        return self.client.post('/accounts/verify/',{'code':'123456'})

    def test_roster_login_and_onboarding(self):
        response=self.login()
        self.assertRedirects(response,'/dashboard/',fetch_redirect_response=False)
        self.assertRedirects(self.client.get('/dashboard/'),'/profile/')
        self.assertFalse(OTPChallenge.objects.exists())
        self.assertEqual(Profile.objects.get().role,'student')

    def test_both_domains_supported(self):
        User.objects.create_user('faculty@rknec.in',self.password,is_demo=True,roster_role='teacher')
        response=self.client.post('/accounts/login/',{'email':' FACULTY@RKNEC.IN ','password':self.password})
        self.assertEqual(response.status_code,302)

    def test_unregistered_email_cannot_create_account(self):
        before=User.objects.count()
        self.client.post('/accounts/login/',{'email':'new@rbunagpur.in','password':self.password})
        self.client.post('/accounts/forgot-password/',{'email':'new@rbunagpur.in'})
        self.client.post('/accounts/verify/',{'code':'123456'})
        self.assertEqual(User.objects.count(),before)
        self.assertNotIn('_auth_user_id',self.client.session)
        self.assertNotIn('reset_grant',self.client.session)

    def test_old_demo_account_not_in_roster_is_rejected(self):
        User.objects.create_user('old@rknec.in',self.password,is_demo=True)
        response=self.client.post('/accounts/login/',{'email':'old@rknec.in','password':self.password})
        self.assertContains(response,'not registered')
        self.assertNotIn('_auth_user_id',self.client.session)

    def test_personal_lookalike_domains_and_wrong_password_fail(self):
        for email in ['a@gmail.com','a@rknec.in.example.com','a@rbunagpur.in.example.com','bad']:
            self.client.post('/accounts/login/',{'email':email,'password':self.password})
        self.login(password='wrong')
        self.assertNotIn('_auth_user_id',self.client.session)

    def test_code_verification_is_not_login_and_password_change_works(self):
        response=self.reset_grant()
        self.assertRedirects(response,'/accounts/reset-password/')
        self.assertNotIn('_auth_user_id',self.client.session)
        response=self.client.post('/accounts/reset-password/',{'new_password1':'FreshResearch!729','new_password2':'FreshResearch!729'})
        self.assertRedirects(response,'/accounts/login/')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('FreshResearch!729'))
        self.assertFalse(self.user.check_password(self.password))
        self.assertIsNone(self.user.email_verified_at)
        self.assertEqual(self.login(password='FreshResearch!729').status_code,302)

    def test_cannot_skip_reset_verification(self):
        response=self.client.post('/accounts/reset-password/',{'new_password1':'FreshResearch!729','new_password2':'FreshResearch!729'})
        self.assertRedirects(response,'/accounts/forgot-password/')
        self.user.refresh_from_db(); self.assertTrue(self.user.check_password(self.password))

    def test_password_confirmation_and_strength(self):
        self.reset_grant()
        for values in [('AStrongPassword!2026','different'),('123','123')]:
            self.assertEqual(self.client.post('/accounts/reset-password/',dict(zip(['new_password1','new_password2'],values))).status_code,200)
        self.user.refresh_from_db();self.assertTrue(self.user.check_password(self.password))

    def test_expiry_replay_and_other_browser(self):
        challenge=self.challenge()
        self.assertIsNone(verify_code(challenge.pk,'other','123456')[0])
        OTPChallenge.objects.filter(pk=challenge.pk).update(expires_at=timezone.now()-timedelta(seconds=1))
        self.assertIsNone(verify_code(challenge.pk,'binding','123456')[0])
        OTPChallenge.objects.filter(pk=challenge.pk).update(expires_at=timezone.now()+timedelta(minutes=1))
        self.assertIsNotNone(verify_code(challenge.pk,'binding','123456')[0])
        self.assertIsNone(verify_code(challenge.pk,'binding','123456')[0])

    def test_five_wrong_codes_lock(self):
        challenge=self.challenge()
        for _ in range(5):self.assertIsNone(verify_code(challenge.pk,'binding','000000')[0])
        self.assertIsNone(verify_code(challenge.pk,'binding','123456')[0])

    def test_resend_invalidates_previous_and_limits_requests(self):
        challenge=self.challenge()
        with self.assertRaises(AuthenticationError):self.challenge()
        OTPChallenge.objects.filter(pk=challenge.pk).update(created_at=timezone.now()-timedelta(seconds=61))
        self.challenge()
        self.assertIsNone(verify_code(challenge.pk,'binding','123456')[0])
        for _ in range(2):
            OTPChallenge.objects.update(created_at=timezone.now()-timedelta(seconds=61))
            self.challenge()
        with self.assertRaises(AuthenticationError):self.challenge()

    def test_password_change_invalidates_old_codes_and_sessions(self):
        other=Client();self.login(client=other)
        challenge=self.challenge()
        self.user.set_password('ChangedSecret!2026');self.user.save()
        self.assertIsNone(verify_code(challenge.pk,'binding','123456')[0])
        self.assertEqual(other.get('/dashboard/').status_code,302)
        self.assertNotIn('_auth_user_id',other.session)

    def test_grant_is_session_bound_and_single_use(self):
        self.reset_grant()
        other=Client()
        self.assertRedirects(other.get('/accounts/reset-password/'),'/accounts/forgot-password/')
        grant=self.client.session['reset_grant']
        self.client.post('/accounts/reset-password/',{'new_password1':'FreshResearch!729','new_password2':'FreshResearch!729'})
        session=self.client.session;session['reset_grant']=grant;session.save()
        self.assertRedirects(self.client.get('/accounts/reset-password/'),'/accounts/forgot-password/')

    def test_login_rate_limit(self):
        for _ in range(10):self.login(password='wrong')
        self.assertContains(self.login(),'Too many attempts')

    @override_settings(DEBUG=False)
    def test_fixed_demo_disabled_in_production(self):
        self.assertIsNone(self.challenge())
        self.assertNotIn('_auth_user_id',self.client.session)

    def test_csrf_and_post_only_logout(self):
        self.assertEqual(Client(enforce_csrf_checks=True).post('/accounts/login/',{}).status_code,403)
        self.assertEqual(self.client.get('/accounts/logout/').status_code,405)

    @override_settings(AUTHENTICATION_MODE='real',EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch('apps.accounts.services.secrets.randbelow',return_value=654321)
    def test_real_reset_uses_random_code(self,random):
        self.user.is_demo=False;self.user.save()
        challenge=self.challenge()
        self.assertIn('654321',mail.outbox[0].body)
        self.assertIsNone(verify_code(challenge.pk,'binding','123456')[0])
        self.assertEqual(verify_code(challenge.pk,'binding','654321')[0].pk,self.user.pk)

    @override_settings(AUTHENTICATION_MODE='real',EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch('apps.accounts.services.send_mail',side_effect=RuntimeError('private provider error'))
    def test_send_failure_invalidates_challenge(self,send):
        self.user.is_demo=False;self.user.save()
        with self.assertRaises(AuthenticationError):self.challenge()
        self.assertTrue(OTPChallenge.objects.get().consumed)

    def test_roster_import_preserves_changed_password_and_assigns_faculty(self):
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/'faculty.json'
            file.write_text(json.dumps({'role':'teacher','accounts':[{'name':'Demo Faculty','email':'faculty@rknec.in','department':'CSE','initial_password':self.password}]}))
            call_command('import_roster',str(file),demo=True,verbosity=0)
            faculty=User.objects.get(email='faculty@rknec.in')
            self.assertTrue(faculty.profile.teacher_approved)
            faculty.set_password('UpdatedFaculty!2026');faculty.save()
            call_command('import_roster',str(file),demo=True,verbosity=0)
            faculty.refresh_from_db();self.assertTrue(faculty.check_password('UpdatedFaculty!2026'))
