import msal
from django.conf import settings


class MSALService:
    """Service class for Microsoft Authentication Library operations."""

    def __init__(self):
        self.client_id = settings.AZURE_CLIENT_ID
        self.client_secret = settings.AZURE_CLIENT_SECRET
        self.authority = settings.AZURE_AUTHORITY
        self.scope = settings.AZURE_SCOPE
        self.redirect_uri = settings.AZURE_REDIRECT_URI

    def _get_app(self):
        return msal.ConfidentialClientApplication(
            client_id=self.client_id,
            authority=self.authority,
            client_credential=self.client_secret,
        )

    def get_auth_url(self, state):
        """Generate Microsoft login URL with CSRF state."""
        return self._get_app().get_authorization_request_url(
            scopes=self.scope,
            state=state,
            redirect_uri=self.redirect_uri,
        )

    def get_token_by_code(self, code):
        """Exchange authorization code for access and ID tokens."""
        return self._get_app().acquire_token_by_authorization_code(
            code=code,
            scopes=self.scope,
            redirect_uri=self.redirect_uri,
        )

    def refresh_token(self, refresh_token):
        """Refresh access token using refresh token."""
        return self._get_app().acquire_token_by_refresh_token(
            refresh_token=refresh_token,
            scopes=self.scope,
        )

    def get_logout_url(self, id_token=None):
        """Generate Microsoft SSO logout URL."""
        base_url = (
            f"{self.authority}/oauth2/v2.0/logout"
            f"?post_logout_redirect_uri="
            f"{self.redirect_uri.replace('/auth/callback/', '/')}"
        )
        if id_token:
            base_url += f"&id_token_hint={id_token}"
        return base_url
