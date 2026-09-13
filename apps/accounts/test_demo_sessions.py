from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.urls import get_script_prefix
from .models import User

@override_settings(DEBUG=True, AUTHENTICATION_MODE='demo')
class DemoSessionTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.password = 'ResearchStart!2026'
        for role in ['student', 'teacher']:
            User.objects.create_user(role+'@rknec.in', self.password, is_demo=True, roster_role=role)

    def open_tab(self):
        response = self.client.get('/accounts/demo-session/')
        self.assertEqual(response.status_code, 302)
        login = response['Location']
        self.client.get(login)
        prefix = login.removesuffix('/accounts/login/')
        cookie = settings.CSRF_COOKIE_NAME+'_'+prefix.split('/')[-1]
        return prefix, cookie

    def sign_in(self, prefix, cookie, role):
        return self.client.post(prefix+'/accounts/login/', {
            'email':role+'@rknec.in', 'password':self.password,
            'csrfmiddlewaretoken':self.client.cookies[cookie].value})

    def test_same_browser_independent_login_logout_and_csrf(self):
        a, ca = self.open_tab()
        b, cb = self.open_tab()
        self.assertNotEqual(a,b)
        self.assertEqual(self.sign_in(a,ca,'student')['Location'],a+'/dashboard/')
        self.assertEqual(self.sign_in(b,cb,'teacher')['Location'],b+'/dashboard/')
        for prefix, email in [(a,'student@rknec.in'),(b,'teacher@rknec.in')]:
            page=self.client.get(prefix+'/profile/')
            self.assertEqual(page.status_code,200)
            self.assertEqual(page.wsgi_request.user.email,email)
            self.assertContains(page,prefix+'/notifications/poll/')
            self.assertEqual(self.client.get(prefix+'/dashboard/')['Location'],prefix+'/profile/')
        # A token from the other account cannot authorise a POST here.
        self.assertEqual(self.client.post(a+'/accounts/logout/',{'csrfmiddlewaretoken':self.client.cookies[cb].value}).status_code,403)
        self.assertEqual(self.client.post(a+'/accounts/logout/',{'csrfmiddlewaretoken':self.client.cookies[ca].value})['Location'],a+'/accounts/login/')
        self.assertFalse(self.client.get(a+'/accounts/login/').wsgi_request.user.is_authenticated)
        self.assertEqual(self.client.get(b+'/profile/').wsgi_request.user.email,'teacher@rknec.in')
        self.assertFalse(self.client.get('/accounts/login/').wsgi_request.user.is_authenticated)
        self.assertEqual(get_script_prefix(),'/')

    def test_root_session_is_not_inherited_by_new_account(self):
        self.client.force_login(User.objects.get(roster_role='student'))
        prefix,_=self.open_tab()
        self.assertFalse(self.client.get(prefix+'/accounts/login/').wsgi_request.user.is_authenticated)
        self.assertEqual(self.client.get('/profile/').wsgi_request.user.email,'student@rknec.in')

    @override_settings(DEBUG=False, AUTHENTICATION_MODE='real')
    def test_feature_unavailable_in_production(self):
        self.assertEqual(self.client.get('/accounts/demo-session/').status_code,404)
        self.assertEqual(self.client.get('/demo/'+'a'*32+'/accounts/login/').status_code,404)
