# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Factory of loggers."""
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
        """Logger."""
        return cls.applicationinsights_event_logger(*args, **kwargs)

    @classmethod
    def applicationinsights_event_logger(cls, *args: Any, **kwargs: Any) -> _AppInsightsEventLogger:
        """Application insights logger."""
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
        """Mock event logger."""
        return _MemoryEventLogger()
