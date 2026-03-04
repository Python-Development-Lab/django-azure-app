import logging
import uuid
import msal
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render


def get_msal_app():
    return msal.ConfidentialClientApplication(
        client_id=settings.AZURE_CLIENT_ID,
        authority=settings.AZURE_AUTHORITY,
        client_credential=settings.AZURE_CLIENT_SECRET,
    )


def login_view(request):
    request.session['state'] = str(uuid.uuid4())
    auth_url = get_msal_app().get_authorization_request_url(
        scopes=settings.AZURE_SCOPE,
        state=request.session['state'],
        redirect_uri=settings.AZURE_REDIRECT_URI,
    )
    return redirect(auth_url)


def callback_view(request):
    if request.GET.get('state') != request.session.get('state'):
        return render(request, 'auth/login.html', {'error': 'State mismatch'})

    if 'error' in request.GET:
        return render(request, 'auth/login.html', {
            'error': request.GET.get('error_description')
        })

    result = get_msal_app().acquire_token_by_authorization_code(
        code=request.GET['code'],
        scopes=settings.AZURE_SCOPE,
        redirect_uri=settings.AZURE_REDIRECT_URI,
    )

    if 'error' in result:
        return render(request, 'auth/login.html', {
            'error': result.get('error_description')
        })

    claims = result.get('id_token_claims', {})
    logging.warning('ENTRA_CLAIMS: %s', claims)

    user = authenticate(request, entra_id_claims=claims)
    if user is None:
        return render(request, 'auth/login.html', {
            'error': 'Authentication failed'
        })

    login(request, user, backend='auth_app.backends.EntraIDBackend')
    request.session['access_token'] = result.get('access_token')
    request.session['id_token'] = result.get('id_token')

    return redirect('core:home')


def logout_view(request):
    id_token = request.session.get('id_token', '')
    logout(request)
    request.session.clear()
    logout_url = (
        f"{settings.AZURE_AUTHORITY}/oauth2/v2.0/logout"
        f"?post_logout_redirect_uri="
        f"{settings.AZURE_REDIRECT_URI.replace('/auth/callback/', '/')}"
    )
    if id_token:
        logout_url += f"&id_token_hint={id_token}"
    return redirect(logout_url)
