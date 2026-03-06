import os
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler


def setup_azure_monitor():
    connection_string = os.environ.get('APPINSIGHTS_CONNECTION_STRING')
    if not connection_string:
        logging.getLogger(__name__).warning(
            "Azure Monitor: APPINSIGHTS_CONNECTION_STRING not set"
        )
        return

    # Structured logging to Application Insights
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = AzureLogHandler(connection_string=connection_string)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    ))
    logger.addHandler(handler)

    logging.getLogger(__name__).info(
        "Azure Monitor: logging configured"
    )


def get_trace_exporter():
    connection_string = os.environ.get('APPINSIGHTS_CONNECTION_STRING')
    if not connection_string:
        return None, None
    exporter = AzureExporter(connection_string=connection_string)
    sampler = ProbabilitySampler(1.0)
    return exporter, sampler
