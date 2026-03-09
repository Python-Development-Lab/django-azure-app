"""
WSGI config for djangoapp project.
It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoapp.settings")

# Azure Monitor OpenTelemetry — ініціалізація до першого запиту
if os.environ.get('WEBSITE_SITE_NAME'):
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
        configure_azure_monitor()
        import logging
        logging.getLogger(__name__).info(
            "Azure Monitor: OpenTelemetry configured via wsgi.py"
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(
            f"Azure Monitor: configuration failed: {e}"
        )

application = get_wsgi_application()
