import logging


class LoggingFilter(logging.Filter):
    """Filters logging messages by logger name prefix.

    For example::

      >>> fltr = LoggingFilter('-boto,requests')
      >>> handler.addFilter(fltr)

    filters out logging messages to handler from boto, while filter in
    those from requests. The loggers not explicitly specified will be
    filtered in by default.

    TODO: This filter may not be as useful without allowing wild card,
    or more aggressive white-listing as opposed to black-listing.

    """

    def __init__(self, logger_prefixes):
        self.whitelist = []
        self.blacklist = []
        for name in logger_prefixes.split(","):
            name = name.strip()
            if name.startswith("-"):
                self.blacklist.append(logging.Filter(name[1:]))
            else:
                self.whitelist.append(logging.Filter(name))

    def filter(self, record):
        if any(f.filter(record) for f in self.blacklist):
            return False
        if any(f.filter(record) for f in self.whitelist):
            return True
        return True
