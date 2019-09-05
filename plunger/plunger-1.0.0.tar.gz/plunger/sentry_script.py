import os
import functools
import logging

import sentry_sdk
from sentry_sdk import configure_scope
from sentry_sdk.integrations.logging import LoggingIntegration

from .version import get_version


def with_sentry(func):
    """A decorator to send exception to sentry"""
    dsn = os.getenv('SENTRY_DSN', '')
    if dsn:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR,
        )
        sentry_sdk.init(dsn, integrations=[sentry_logging])
        with configure_scope() as scope:
            # set some sentry meta
            package = __package__.replace('_', '-')
            version = get_version()
            scope.set_tag('%s_version' % package, version)
            scope.set_extra('%s.version' % package, version)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:  # pragma: no cover
            logging.exception('An error occured')
            # re-raise to get the error on stdout
            raise

    return wrapper
