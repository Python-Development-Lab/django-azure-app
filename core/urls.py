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
    path('security/geo/', views.security_geo, name='security_geo'),
    path('security/geo-data/', views.security_geo_data, name='security_geo_data'),
    path('security/threat-intel/', views.security_threat_intel, name='security_threat_intel'),

    # FinOps Dashboard
    path('finops/', views.finops_dashboard, name='finops_dashboard'),
    path('finops/summary/', views.finops_summary, name='finops_summary'),
    path('finops/daily/', views.finops_daily, name='finops_daily'),
    path('finops/breakdown/', views.finops_breakdown, name='finops_breakdown'),
    path('finops/rg-summary/', views.finops_rg_summary, name='finops_rg_summary'),

    # Analytics Dashboard
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/pageviews/', views.analytics_pageviews, name='analytics_pageviews'),
    path('analytics/browsers/', views.analytics_browsers, name='analytics_browsers'),
    path('analytics/performance/', views.analytics_performance, name='analytics_performance'),
    path('analytics/rum/', views.analytics_rum, name='analytics_rum'),
]
