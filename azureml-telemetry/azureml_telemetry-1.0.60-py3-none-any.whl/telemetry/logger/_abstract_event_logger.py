# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base class for all loggers."""
from abc import ABC, abstractmethod

from azureml.telemetry.contracts import TelemetryObjectBase
from azureml.telemetry.log_scope import LogScope as _LogScope


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

    def _fill_props_with_context(self, telemetry_entry: TelemetryObjectBase) -> dict:
        props = telemetry_entry.get_all_properties()
        ctx = _LogScope.get_current()
        return props if ctx is None else ctx.get_merged_props(props)
