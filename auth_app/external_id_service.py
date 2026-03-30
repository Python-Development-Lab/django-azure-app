import msal
from django.conf import settings


class ExternalIDService:
    def __init__(self):
        self.client_id = settings.EXTERNAL_ID_CLIENT_ID
        self.client_secret = settings.EXTERNAL_ID_CLIENT_SECRET
        self.tenant_id = settings.EXTERNAL_ID_TENANT_ID
        self.user_flow = settings.EXTERNAL_ID_USER_FLOW
        self.redirect_uri = settings.EXTERNAL_ID_REDIRECT_URI
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"

    def _get_app(self):
        return msal.ConfidentialClientApplication(
            client_id=self.client_id,
            authority=self.authority,
            client_credential=self.client_secret,
        )

    def get_auth_url(self, state):
        return self._get_app().get_authorization_request_url(
            scopes=["openid", "profile", "email"],
            state=state,
            redirect_uri=self.redirect_uri,
        )

    def get_token_by_code(self, code):
        return self._get_app().acquire_token_by_authorization_code(
            code=code,
            scopes=["openid", "profile", "email"],
            redirect_uri=self.redirect_uri,
        )

    def get_logout_url(self, id_token=None):
        base_url = f"{self.authority}/oauth2/v2.0/logout?post_logout_redirect_uri=http://localhost:8000/"
        if id_token:
            base_url += f"&id_token_hint={id_token}"
        return base_url
