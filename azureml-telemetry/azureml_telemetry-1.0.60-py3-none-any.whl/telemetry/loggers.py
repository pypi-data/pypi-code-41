# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Factory for creating loggers."""
from typing import Any, Type

from threading import Lock

from .logger import ApplicationInsightsEventLogger as _AppInsightsEventLogger, \
    InMemoryEventLogger as _MemoryEventLogger

mutex = Lock()


class Loggers:
    """Factory of loggers."""

    APPINSIGHT_LOGGERS = {}
    INSTRUMENTATION_KEY_KEY = "instrumentation_key"

    @classmethod
    def default_logger(cls: Type["Loggers"], *args: Any, **kwargs: Any):
        """Return the default logger.

        In most common scenarios, use the :func:`azureml.telemetry.get_event_logger` function to get
        an instance of the default logger.
        """
        return cls.applicationinsights_event_logger(*args, **kwargs)

    @classmethod
    def applicationinsights_event_logger(cls, *args: Any, **kwargs: Any) -> _AppInsightsEventLogger:
        """Return the Application Insights logger.

        In most common scenarios, use the :func:`azureml.telemetry.logging_handler.get_appinsights_log_handler`
        function to get a handle to the Application Insights logger.
        """
        assert kwargs is not None and Loggers.INSTRUMENTATION_KEY_KEY in kwargs, "Instrumentation key is mandatory."
        instrumentation_key = kwargs.pop(Loggers.INSTRUMENTATION_KEY_KEY)

        # Make sure we create only one instance for each instrumentation key.
        with mutex:
            if instrumentation_key not in Loggers.APPINSIGHT_LOGGERS:
                Loggers.APPINSIGHT_LOGGERS[instrumentation_key] = \
                    Loggers.APPINSIGHT_LOGGERS.get(instrumentation_key,
                                                   _AppInsightsEventLogger(instrumentation_key=instrumentation_key,
                                                                           *args, **kwargs))

        return Loggers.APPINSIGHT_LOGGERS[instrumentation_key]

    @classmethod
    def inmemory_event_logger(cls) -> _MemoryEventLogger:
        """Return the mock event logger."""
        return _MemoryEventLogger()
