# -*- coding: utf-8 -*-
import logging
import weakref

from missinglink.core.bounded_logger import BoundedLogger


class RootLoggerSniffer(BoundedLogger):
    class Handler(logging.Handler):
        def __init__(self, parent):
            super(RootLoggerSniffer.Handler, self).__init__()
            self._parent = parent

        def emit(self, record):
            try:
                self._parent.on_root_log(record)
            except ReferenceError:
                pass

    def __init__(self, log_level):
        super(RootLoggerSniffer, self).__init__()
        self.root_logger = logging.getLogger()
        self.log_level = log_level
        self.handler = None
        self.logs_so_far = []

    def close(self):
        self._deactivate()

    def emit(self, record):
        self.on_root_log(record)

    def on_root_log(self, record):
        pass

    def _activate(self):
        self.handler = self.Handler(weakref.proxy(self))

        self.root_logger.addHandler(self.handler)

    def _deactivate(self):
        self.root_logger.removeHandler(self.handler)
