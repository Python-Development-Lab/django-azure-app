import time
from auth_app.msal_service import MSALService


class TokenRefreshMiddleware:
    """Automatically refresh expired Microsoft Entra ID access tokens."""

    REFRESH_THRESHOLD = 300  # refresh if token expires in less than 5 minutes

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            self._maybe_refresh_token(request)
        return self.get_response(request)

    def _maybe_refresh_token(self, request):
        expiry = request.session.get('token_expiry')
        refresh_tok = request.session.get('refresh_token')

        if not expiry or not refresh_tok:
            return

        if time.time() < expiry - self.REFRESH_THRESHOLD:
            return

        msal_service = MSALService()
        result = msal_service.refresh_token(refresh_tok)

        if 'access_token' in result:
            request.session['access_token'] = result['access_token']
            request.session['token_expiry'] = int(time.time()) + result.get('expires_in', 3600)
            if 'refresh_token' in result:
                request.session['refresh_token'] = result['refresh_token']
