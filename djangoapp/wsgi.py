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
    import os as _os
    _conn = (
        _os.environ.get("APPINSIGHTS_CONNECTION_STRING") or
        _os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    )
    if _conn:
        from azure.monitor.opentelemetry import configure_azure_monitor
        configure_azure_monitor(connection_string=_conn)
        # Підключити auth_app logger до OpenTelemetry
        import logging
        from opentelemetry.sdk._logs import LoggerProvider
        from opentelemetry._logs import get_logger_provider
        for log_name in ["auth_app", "auth_app.device_middleware", "djangoapp"]:
            logging.getLogger(log_name).setLevel(logging.INFO)
        logger.warning("Azure Monitor: OpenTelemetry configured")
    else:
        logger.warning("Azure Monitor: APPINSIGHTS_CONNECTION_STRING not set")
    # Явний тестовий trace
    from opentelemetry import trace
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("wsgi-startup"):
        logger.warning("Azure Monitor: OpenTelemetry configured successfully")

except Exception as e:
    logger.warning(f"Azure Monitor: configuration failed: {e}")

from django.core.wsgi import get_wsgi_application  # noqa: E402
application = get_wsgi_application()
