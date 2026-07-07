from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('health/', views.health_check, name='health_check'),

    # Security Dashboard
    path('security/', views.security_dashboard, name='security_dashboard'),
    path('security/coverage/', views.security_coverage, name='security_coverage'),
    path('security/alerts/', views.security_alerts, name='security_alerts'),

    # FinOps Dashboard
    path('finops/', views.finops_dashboard, name='finops_dashboard'),
    path('finops/summary/', views.finops_summary, name='finops_summary'),
    path('finops/daily/', views.finops_daily, name='finops_daily'),
    path('finops/breakdown/', views.finops_breakdown, name='finops_breakdown'),
    path('finops/rg-summary/', views.finops_rg_summary, name='finops_rg_summary'),
]
