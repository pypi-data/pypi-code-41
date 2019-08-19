# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Application insights logger."""
from typing import Any

from applicationinsights import TelemetryClient

from azureml.telemetry.contracts import Event, Metric
from ._abstract_event_logger import AbstractEventLogger


class ApplicationInsightsEventLogger(AbstractEventLogger):
    """Application insights logger."""

    def __init__(self, instrumentation_key: str, *args: Any, **kwargs: Any) -> None:
        """
        Initialize a new instance of the ApplicationInsightsLogger.

        :param instrumentation_key: instrumentation key to use while sending telemetry to the service.
        :param args: arguments
        :param kwargs: key word arguments
        """
        self.telemetry_client = TelemetryClient(instrumentation_key=instrumentation_key)
        # flush telemetry every 30 seconds (assuming we don't hit max_queue_item_count first)
        self.telemetry_client.channel.sender.send_interval_in_milliseconds = 30 * 1000
        # flush telemetry if we have 10 or more telemetry items in our queue
        self.telemetry_client.channel.queue.max_queue_length = 10
        super(ApplicationInsightsEventLogger, self).__init__(*args, **kwargs)

    def log_event(self, telemetry_event: Event) -> str:
        """
        Log event.

        :param telemetry_event: Telemetry event to log.
        :return: Event GUID.
        """
        self.telemetry_client.track_event(telemetry_event.name, telemetry_event.get_all_properties())
        return telemetry_event.required_fields.event_id

    def log_metric(self, telemetry_metric: Metric) -> str:
        """Log metric.

        :param telemetry_metric: Telemetry metric to log.
        :return: Metric GUID.
        """
        properties = telemetry_metric.get_all_properties()
        self.telemetry_client.track_metric(
            name=telemetry_metric.name,
            value=telemetry_metric.value,
            count=telemetry_metric.count,
            type=telemetry_metric.metric_type,
            max=telemetry_metric.metric_max,
            min=telemetry_metric.metric_min,
            std_dev=telemetry_metric.std_dev,
            properties=properties
        )
        return telemetry_metric.required_fields.event_id

    def flush(self) -> None:
        """Flush the telemetry client."""
        self.telemetry_client.flush()
