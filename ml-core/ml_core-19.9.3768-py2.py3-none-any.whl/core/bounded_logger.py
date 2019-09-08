import logging


class BoundedLogger(object):
    DEFAULT_MAX_BACKLOGS = 10000
    SIZE_LIMIT_MSG = 'Logging truncated due to size limit'

    def __init__(self, max_backlogs=None):
        self.logs_so_far = []
        self.max_backlogs = max_backlogs or self.DEFAULT_MAX_BACKLOGS

    def _is_backlog_full(self):
        return len(self.logs_so_far) > self.max_backlogs

    def _add_record(self, record):
        self.logs_so_far.append(record)

        if not self._is_backlog_full():
            return

        while self._is_backlog_full():
            self.logs_so_far.pop(0)

        self.logs_so_far[0] = logging.makeLogRecord(dict(name='root', msg=self.SIZE_LIMIT_MSG, levelno=logging.WARNING))
