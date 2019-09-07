# This program is free software: you can redistribute it and/or modify it under the
# terms of the Apache License (v2.0) as published by the Apache Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the Apache License for more details.
#
# You should have received a copy of the Apache License along with this program.
# If not, see <https://www.apache.org/licenses/LICENSE-2.0>.

"""Logging for dist_exe."""

# standard libs
import sys
import logging
import socket


class HostnameFilter(logging.Filter):
    """Custom filter to inject the hostname into the logging record."""

    hostname: str = socket.gethostname()

    def filter(self, record):
        """Adds hostname to record."""
        record.hostname = self.hostname
        return True


# default values
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s %(hostname)s %(levelname)s %(name)s %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def get_logger(name: str, level: str = LOG_LEVEL, msgfmt: str = LOG_FORMAT,
               datefmt: str = DATE_FORMAT, filename: str = None):
    """Configure and initialize logger."""

    if not filename:
        handler = logging.StreamHandler(stream=sys.stderr)
    else:
        handler = logging.FileHandler(filename)

    handler.addFilter(HostnameFilter())
    handler.setFormatter(logging.Formatter(msgfmt, datefmt=datefmt))

    log = logging.getLogger(name)
    log.addHandler(handler)
    log.setLevel(getattr(logging, level.upper()))
    return log
