import msal
from django.conf import settings


class ExternalIDService:
    def __init__(self):
        self.client_id = settings.EXTERNAL_ID_CLIENT_ID
        self.client_secret = settings.EXTERNAL_ID_CLIENT_SECRET
        self.tenant_id = settings.EXTERNAL_ID_TENANT_ID
        self.user_flow = settings.EXTERNAL_ID_USER_FLOW
        self.redirect_uri = settings.EXTERNAL_ID_REDIRECT_URI
        self.authority = f"https://seclabsecurityengineering.ciamlogin.com"

    def _get_app(self):
        return msal.ConfidentialClientApplication(
            client_id=self.client_id,
            authority=self.authority,
            client_credential=self.client_secret,
        )

    def get_auth_url(self, state):
        return self._get_app().get_authorization_request_url(
            scopes=["User.Read"],
            state=state,
            redirect_uri=self.redirect_uri,
            extra_query_parameters={"p": self.user_flow},
        )

    def get_token_by_code(self, code):
        return self._get_app().acquire_token_by_authorization_code(
            code=code,
            scopes=["User.Read"],
            redirect_uri=self.redirect_uri,
        )

    def get_logout_url(self, id_token=None):
        base_url = f"{self.authority}/oauth2/v2.0/logout?post_logout_redirect_uri=https://mydjango1772289446.azurewebsites.net/"
        if id_token:
            base_url += f"&id_token_hint={id_token}"
        return base_url
