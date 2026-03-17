"""
WSGI config for djangoapp project.
"""
import os
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoapp.settings")

# Azure Monitor OpenTelemetry — КРИТИЧНО: до get_wsgi_application()
try:
    from azure.monitor.opentelemetry import configure_azure_monitor
    configure_azure_monitor()
    logging.getLogger(__name__).warning(
        "Azure Monitor: OpenTelemetry configured successfully"
    )
except Exception as e:
    logging.getLogger(__name__).warning(
        f"Azure Monitor: configuration failed: {e}"
    )

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
