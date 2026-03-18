"""
WSGI config for djangoapp project.
"""
import os
import logging

# Налаштовуємо logging ДО configure_azure_monitor
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoapp.settings")

# Azure Monitor OpenTelemetry — КРИТИЧНО: до get_wsgi_application()
try:
    from azure.monitor.opentelemetry import configure_azure_monitor
    configure_azure_monitor()

    # Явний тестовий trace
    from opentelemetry import trace
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("wsgi-startup"):
        logger.warning("Azure Monitor: OpenTelemetry configured successfully")

except Exception as e:
    logger.warning(f"Azure Monitor: configuration failed: {e}")

from django.core.wsgi import get_wsgi_application  # noqa: E402
application = get_wsgi_application()
