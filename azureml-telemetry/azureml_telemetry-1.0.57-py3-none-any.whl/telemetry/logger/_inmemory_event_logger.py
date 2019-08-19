# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Mock logger."""
from azureml.telemetry.contracts import TelemetryObjectBase
from ._abstract_event_logger import AbstractEventLogger


class InMemoryEventLogger(AbstractEventLogger):
    """In memory event logger."""

    def __init__(self):
        """Initialize in memory event logger."""
        self.logs = []

    def log_event(self, telemetry_event: TelemetryObjectBase):
        """Store the event into the dictionary."""
        self.logs.append(telemetry_event)
        print(telemetry_event)
        return telemetry_event.required_fields.event_id

    def log_metric(self, telemetry_metric: TelemetryObjectBase) -> str:
        """Store the metric into the dictionary."""
        self.logs.append(telemetry_metric)
        return telemetry_metric.required_fields.event_id

    def flush(self):
        """Flush the events."""
        pass
