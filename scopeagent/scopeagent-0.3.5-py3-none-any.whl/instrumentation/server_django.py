import logging

import wrapt

from .wrappers.wsgi import wrap_wsgi


logger = logging.getLogger(__name__)


def wrapper(wrapped, instance, args, kwargs):
    return wrap_wsgi(wrapped)(*args, **kwargs)


def patch():
    try:
        logger.debug("patching module=django.core.handlers.wsgi name=WSGIHandler.__call__")
        wrapt.wrap_function_wrapper('django.core.handlers.wsgi', 'WSGIHandler.__call__', wrapper)
    except ImportError:
        logger.debug("module not found module=django.core.handlers.wsgi")
