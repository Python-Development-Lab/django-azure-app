"""
WSGI config for djangoapp project.
"""
import os
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoapp.settings")

try:
    _conn = (
        os.environ.get("APPINSIGHTS_CONNECTION_STRING") or
        os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    )
    if _conn:
        from azure.monitor.opentelemetry import configure_azure_monitor
        configure_azure_monitor(connection_string=_conn)

        import logging as _logging
        from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter
        from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

        _exporter = AzureMonitorLogExporter(connection_string=_conn)
        _provider = LoggerProvider()
        _provider.add_log_record_processor(BatchLogRecordProcessor(_exporter))
        _handler = LoggingHandler(logger_provider=_provider)
        _handler.setLevel(_logging.WARNING)
        _logging.getLogger().addHandler(_handler)

        logger.warning("Azure Monitor: OpenTelemetry configured with logging bridge")
    else:
        logger.warning("Azure Monitor: APPINSIGHTS_CONNECTION_STRING not set")
except Exception as e:
    logger.warning(f"Azure Monitor: configuration failed: {e}")

from django.core.wsgi import get_wsgi_application  # noqa: E402
application = get_wsgi_application()

# Додаємо LoggingHandler ПІСЛЯ Django ініціалізації (dictConfig не перезапише)
if _conn:
    try:
        import logging as _logging2
        from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter
        from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
        _exporter2 = AzureMonitorLogExporter(connection_string=_conn)
        _provider2 = LoggerProvider()
        _provider2.add_log_record_processor(BatchLogRecordProcessor(_exporter2))
        _handler2 = LoggingHandler(logger_provider=_provider2)
        _handler2.setLevel(_logging2.WARNING)
        _logging2.getLogger().addHandler(_handler2)
        _logging2.getLogger().warning("Azure Monitor: logging bridge attached after Django init")
    except Exception as _e2:
        pass
