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


class TokenRefreshMiddlewareTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test-oid', password='pass')
        self.factory = RequestFactory()

    def test_skips_anonymous_user(self):
        from auth_app.middleware import TokenRefreshMiddleware
        get_response = MagicMock(return_value=MagicMock())
        middleware = TokenRefreshMiddleware(get_response)
        request = self.factory.get('/')
        request.user = MagicMock(is_authenticated=False)
        request.session = {}
        middleware(request)
        get_response.assert_called_once()

    def test_skips_if_no_expiry(self):
        from auth_app.middleware import TokenRefreshMiddleware
        get_response = MagicMock(return_value=MagicMock())
        middleware = TokenRefreshMiddleware(get_response)
        request = self.factory.get('/')
        request.user = MagicMock(is_authenticated=True)
        request.session = {}
        middleware(request)
        get_response.assert_called_once()

    @patch('auth_app.middleware.MSALService')
    def test_refreshes_token_when_expiring(self, mock_msal_class):
        import time
        from auth_app.middleware import TokenRefreshMiddleware
        mock_service = MagicMock()
        mock_service.refresh_token.return_value = {
            'access_token': 'new-token',
            'expires_in': 3600,
        }
        mock_msal_class.return_value = mock_service

        get_response = MagicMock(return_value=MagicMock())
        middleware = TokenRefreshMiddleware(get_response)
        request = self.factory.get('/')
        request.user = MagicMock(is_authenticated=True)
        request.session = {
            'token_expiry': int(time.time()) + 60,
            'refresh_token': 'old-refresh-token',
        }
        middleware(request)
        mock_service.refresh_token.assert_called_once_with('old-refresh-token')
        self.assertEqual(request.session['access_token'], 'new-token')


class RBACDecoratorsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test-oid', password='pass')
        self.factory = RequestFactory()

    def _make_request(self, session_data=None):
        request = self.factory.get('/')
        request.user = self.user
        request.session = session_data or {}
        return request

    def test_require_group_allows_access(self):
        from auth_app.decorators import require_group
        view = require_group('Admin')(lambda r: 'ok')
        request = self._make_request({'entra_groups': ['Admin', 'Users']})
        result = view(request)
        self.assertEqual(result, 'ok')

    def test_require_group_denies_access(self):
        from auth_app.decorators import require_group
        from django.http import HttpResponseForbidden
        view = require_group('Admin')(lambda r: 'ok')
        request = self._make_request({'entra_groups': ['Users']})
        result = view(request)
        self.assertIsInstance(result, HttpResponseForbidden)

    def test_require_role_allows_access(self):
        from auth_app.decorators import require_role
        view = require_role('manager')(lambda r: 'ok')
        request = self._make_request({'entra_roles': ['manager']})
        result = view(request)
        self.assertEqual(result, 'ok')

    def test_require_role_denies_access(self):
        from auth_app.decorators import require_role
        from django.http import HttpResponseForbidden
        view = require_role('manager')(lambda r: 'ok')
        request = self._make_request({'entra_roles': []})
        result = view(request)
        self.assertIsInstance(result, HttpResponseForbidden)


class KeyVaultServiceTest(TestCase):
    @patch('djangoapp.key_vault.ManagedIdentityCredential')
    @patch('djangoapp.key_vault.SecretClient')
    def test_load_secrets_to_env(self, mock_client_cls, mock_cred_cls):
        mock_client = MagicMock()
        mock_client.get_secret.return_value = MagicMock(value='test-value')
        mock_client_cls.return_value = mock_client

        import os
        os.environ.pop('SECRET_KEY', None)

        from djangoapp.key_vault import load_secrets_to_env
        load_secrets_to_env()

        mock_client.get_secret.assert_called()

    @patch('djangoapp.key_vault.ManagedIdentityCredential')
    @patch('djangoapp.key_vault.SecretClient')
    def test_load_secrets_skips_existing_env(self, mock_client_cls, mock_cred_cls):
        mock_client = MagicMock()
        mock_client.get_secret.return_value = MagicMock(value='test-value')
        mock_client_cls.return_value = mock_client

        import os
        for key in ['SECRET_KEY', 'AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET', 'AZURE_TENANT_ID']:
            os.environ[key] = 'already-set'

        from djangoapp.key_vault import load_secrets_to_env
        load_secrets_to_env()

        # get_secret called once for credential check only, not for each secret
        secret_names = [c.args[0] for c in mock_client.get_secret.call_args_list]
        assert secret_names.count('DJANGO-SECRET-KEY') <= 1
