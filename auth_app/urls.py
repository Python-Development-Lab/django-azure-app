from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='auth_login'),
    path('redirect/', views.microsoft_redirect_view, name='auth_redirect'),
    path('callback/', views.callback_view, name='auth_callback'),
    path('logout/', views.logout_view, name='auth_logout'),
]
