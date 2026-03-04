from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from auth_app.backends import EntraIDBackend


class EntraIDBackendTest(TestCase):

    def setUp(self):
        self.backend = EntraIDBackend()
        self.factory = RequestFactory()
        self.claims = {
            'oid': 'test-oid-123',
            'preferred_username': 'test@epam.com',
            'name': 'Test User',
        }

    def test_authenticate_creates_user(self):
        request = self.factory.get('/')
        user = self.backend.authenticate(request, entra_id_claims=self.claims)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'test-oid-123')
        self.assertEqual(user.email, 'test@epam.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')

    def test_authenticate_updates_existing_user(self):
        User.objects.create(username='test-oid-123', email='old@epam.com')
        request = self.factory.get('/')
        user = self.backend.authenticate(request, entra_id_claims=self.claims)
        self.assertEqual(user.email, 'test@epam.com')
        self.assertEqual(user.first_name, 'Test')

    def test_authenticate_no_claims_returns_none(self):
        request = self.factory.get('/')
        user = self.backend.authenticate(request, entra_id_claims=None)
        self.assertIsNone(user)

    def test_authenticate_no_oid_returns_none(self):
        request = self.factory.get('/')
        user = self.backend.authenticate(request, entra_id_claims={'email': 'test@epam.com'})
        self.assertIsNone(user)

    def test_get_user_returns_user(self):
        existing = User.objects.create(username='test-oid-123')
        user = self.backend.get_user(existing.pk)
        self.assertEqual(user.pk, existing.pk)

    def test_get_user_not_found_returns_none(self):
        user = self.backend.get_user(99999)
        self.assertIsNone(user)
