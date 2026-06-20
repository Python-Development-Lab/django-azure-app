from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="auth_login"),
    path("redirect/", views.microsoft_redirect_view, name="auth_redirect"),
    path("callback/", views.callback_view, name="auth_callback"),
    path("logout/", views.logout_view, name="auth_logout"),
    path("external/redirect/", views.external_redirect_view, name="auth_external_redirect"),
    path("external/callback/", views.external_callback_view, name="auth_external_callback"),
    path("external/logout/", views.external_logout_view, name="auth_external_logout"),
]
