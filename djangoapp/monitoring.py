import os
import logging


def setup_azure_monitor():
    connection_string = os.environ.get('APPINSIGHTS_CONNECTION_STRING')
    if not connection_string:
        logging.getLogger(__name__).warning(
            "Azure Monitor: APPINSIGHTS_CONNECTION_STRING not set"
        )
        return
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
        configure_azure_monitor(
            connection_string=connection_string,
            logger_name="djangoapp",
        )
        logging.getLogger(__name__).info(
            "Azure Monitor: OpenTelemetry configured"
        )
    except Exception as e:
        logging.getLogger(__name__).warning(
            f"Azure Monitor: configuration failed: {e}"
        )
