from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from .models import User

class AccountFoundationTests(TestCase):
    def test_normalises_college_email_without_claiming_verification(self):
        user = User.objects.create_user("  Student@RBUNAGPUR.IN  ")
        user.refresh_from_db()
        self.assertEqual(user.email, "student@rbunagpur.in")
        self.assertIsNone(user.email_verified_at)
        self.assertFalse(user.has_usable_password())
        self.assertFalse(user.is_staff)

    def test_invalid_or_wrong_domain_is_rejected(self):
        for email in ["a@gmail.com", "a@rbunagpur.in.example.com", "bad", "@rbunagpur.in", "a@@rbunagpur.in"]:
            with self.subTest(email=email), self.assertRaises(ValidationError):
                User.objects.create_user(email)

    def test_case_insensitive_uniqueness_even_when_save_is_bypassed(self):
        User.objects.create_user("student@rbunagpur.in")
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.bulk_create([User(email="STUDENT@RBUNAGPUR.IN")])

    def test_direct_save_checks_eligibility(self):
        with self.assertRaises(ValidationError):
            User(email="outsider@gmail.com").save()

    def test_superuser_requires_admin_permissions(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser("admin@rbunagpur.in", "test-only-password", is_staff=False)

    def test_administrator_can_authenticate(self):
        User.objects.create_superuser("admin@rbunagpur.in", "test-only-password")
        self.assertTrue(self.client.login(email="admin@rbunagpur.in", password="test-only-password"))
        self.assertEqual(self.client.get("/admin/").status_code, 200)
