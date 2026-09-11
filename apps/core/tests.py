from django.test import TestCase

class FoundationRoutingTests(TestCase):
    def test_entry_routes_to_sign_in(self):
        self.assertRedirects(self.client.get("/"), "/accounts/login/")

    def test_sign_in_does_not_claim_working_otp(self):
        response = self.client.get("/accounts/login/")
        self.assertContains(response, "Sign-in will be available")
        self.assertNotContains(response, '<form')

    def test_private_uploads_are_not_publicly_routed(self):
        self.assertEqual(self.client.get("/media/signed-agreement.pdf").status_code, 404)

    def test_admin_requires_authentication(self):
        self.assertEqual(self.client.get("/admin/").status_code, 302)
