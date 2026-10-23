from unittest.mock import patch
from django.test import TestCase, override_settings
from django.core.management import call_command
from apps.accounts.models import User, OTPChallenge
from apps.accounts.services import request_code, AuthenticationError
from apps.profiles.models import Department, Skill, ResearchInterest, Profile


@override_settings(PASSWORD_RESET_ENABLED=False, AUTHENTICATION_MODE='real',
                   PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class EmailOptionalDeploymentTests(TestCase):
    def test_login_works_without_email_and_hides_reset_link(self):
        user = User.objects.create_user('hosted@rknec.in', 'PrivateTest!8672', roster_role='student', is_demo=False)
        page = self.client.get('/accounts/login/')
        self.assertContains(page, 'Contact the project administrator')
        self.assertNotContains(page, 'href="/accounts/forgot-password/"')
        self.assertNotContains(page, '123456')
        result = self.client.post('/accounts/login/', {'email': user.email, 'password': 'PrivateTest!8672'})
        self.assertEqual(result.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    @patch('apps.accounts.services.send_mail')
    def test_disabled_endpoints_clear_grants_and_never_send(self, send_mail):
        for url in ['/accounts/forgot-password/', '/accounts/verify/', '/accounts/resend/', '/accounts/reset-password/']:
            session = self.client.session
            session['reset_grant'] = 'stale-grant'
            session.save()
            response = self.client.post(url, {'email': 'hosted@rknec.in', 'code': '123456'})
            self.assertEqual(response.status_code, 403)
            self.assertContains(response, 'currently unavailable', status_code=403)
            self.assertNotIn('reset_grant', self.client.session)
        send_mail.assert_not_called()
        self.assertFalse(OTPChallenge.objects.exists())

    def test_direct_service_cannot_issue_code(self):
        with self.assertRaises(AuthenticationError):
            request_code('hosted@rknec.in', 'binding', 'ip')
        self.assertFalse(OTPChallenge.objects.exists())

    def test_production_taxonomy_repeatable_without_profiles(self):
        call_command('seed_taxonomy')
        counts = (Department.objects.count(), Skill.objects.count(), ResearchInterest.objects.count())
        call_command('seed_taxonomy')
        self.assertEqual(counts, (Department.objects.count(), Skill.objects.count(), ResearchInterest.objects.count()))
        self.assertEqual(counts, (10, 8, 7))
        self.assertFalse(User.objects.exists())
        self.assertFalse(Profile.objects.exists())
