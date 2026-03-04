from unittest.mock import MagicMock, patch
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from auth_app.backends import EntraIDBackend
from auth_app.msal_service import MSALService


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


class MSALServiceTest(TestCase):

    @patch('auth_app.msal_service.msal.ConfidentialClientApplication')
    def test_get_auth_url(self, mock_msal):
        mock_app = MagicMock()
        mock_app.get_authorization_request_url.return_value = 'https://login.microsoft.com/auth'
        mock_msal.return_value = mock_app

        service = MSALService()
        url = service.get_auth_url(state='test-state')

        self.assertEqual(url, 'https://login.microsoft.com/auth')
        mock_app.get_authorization_request_url.assert_called_once()

    @patch('auth_app.msal_service.msal.ConfidentialClientApplication')
    def test_get_token_by_code(self, mock_msal):
        mock_app = MagicMock()
        mock_app.acquire_token_by_authorization_code.return_value = {
            'access_token': 'test-token',
            'id_token_claims': {'oid': 'test-oid'}
        }
        mock_msal.return_value = mock_app

        service = MSALService()
        result = service.get_token_by_code(code='test-code')

        self.assertEqual(result['access_token'], 'test-token')
        mock_app.acquire_token_by_authorization_code.assert_called_once()

    def test_get_logout_url_without_token(self):
        service = MSALService()
        url = service.get_logout_url()
        self.assertIn('logout', url)
        self.assertNotIn('id_token_hint', url)

    def test_get_logout_url_with_token(self):
        service = MSALService()
        url = service.get_logout_url(id_token='test-id-token')
        self.assertIn('id_token_hint=test-id-token', url)
