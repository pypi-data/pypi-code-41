# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base class for all loggers."""
from abc import ABC, abstractmethod
from azureml.telemetry.contracts import TelemetryObjectBase


class AbstractEventLogger(ABC):
    """Abstract event logger class."""

    @abstractmethod
    def log_event(self, telemetry_event: TelemetryObjectBase) -> str:
        """
        Log event.

        :return: Event GUID.
        """
        raise NotImplementedError()

    @abstractmethod
    def log_metric(self, telemetry_metric: TelemetryObjectBase) -> str:
        """
        Log metric.

        :return: Metric GUID.
        """
        raise NotImplementedError()

    @abstractmethod
    def flush(self):
        """Flush the telemetry client."""
        raise NotImplementedError()
