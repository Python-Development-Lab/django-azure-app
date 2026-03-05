import time
import uuid
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from auth_app.msal_service import MSALService


def login_view(request):
    return render(request, 'auth/login.html')


def microsoft_redirect_view(request):
    msal_service = MSALService()
    request.session['state'] = str(uuid.uuid4())
    auth_url = msal_service.get_auth_url(state=request.session['state'])
    return redirect(auth_url)


def callback_view(request):
    if request.GET.get('state') != request.session.get('state'):
        return render(request, 'auth/login.html', {'error': 'State mismatch'})

    if 'error' in request.GET:
        return render(request, 'auth/login.html', {
            'error': request.GET.get('error_description')
        })

    msal_service = MSALService()
    result = msal_service.get_token_by_code(code=request.GET['code'])

    if 'error' in result:
        return render(request, 'auth/login.html', {
            'error': result.get('error_description')
        })

    claims = result.get('id_token_claims', {})

    user = authenticate(request, entra_id_claims=claims)
    if user is None:
        return render(request, 'auth/login.html', {
            'error': 'Authentication failed'
        })

    login(request, user, backend='auth_app.backends.EntraIDBackend')
    request.session['access_token'] = result.get('access_token')
    request.session['id_token'] = result.get('id_token')
    request.session['refresh_token'] = result.get('refresh_token')
    request.session['token_expiry'] = int(time.time()) + result.get('expires_in', 3600)
    request.session['entra_groups'] = claims.get('groups', [])
    request.session['entra_roles'] = claims.get('roles', [])

    return redirect('core:home')


def logout_view(request):
    id_token = request.session.get('id_token', '')
    logout(request)
    request.session.clear()
    msal_service = MSALService()
    logout_url = msal_service.get_logout_url(id_token=id_token)
    return redirect(logout_url)
