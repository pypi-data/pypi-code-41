import logging
import logging.handlers
import threading
from logging import _STYLES
from logging import Formatter
from itertools import zip_longest

try:
    from raven.handlers.logging import SentryHandler
except ImportError:
    SentryHandler = None

from .filters import LoggingFilter


_lock = threading.RLock()


def _acquire_lock():
    if _lock:
        _lock.acquire()


def _release_lock():
    if _lock:
        _lock.release()


root = logging.root


def config(**kwargs):
    """Do basic configuration of the logging system.

    This function extends built-in :func:`logging.basicConfig` to add features mainly
    for convenience. See the documentation of :func:`logging.basicConfig` for available
    function arguments. For this function, the following additional options can be
    supplied.

    Args:
        file_handler: One of the logging.handlers class to use with the supplied
            `filename`.
        filter (str): Comma-delimited logger name prefixes to filter in and out, e.g.,
            "-boto,requests". Using "-" means filtering out.
        sentry_client (:class:`raven.Client`): Sentry client.
        sentry_logging_level (str): Name of logging level used for Sentry
            logginghandler. Defaults to 'WARNING'.
        sentry_logging_filter (str): Name prefixes (see `filter` above) used for Sentry
            handlers.
        socket (str): If set in the form `host:port`, add a SocketHandler to send
            logging messages over the network. If only the host is given and port is
            missing, `logging.handlers.DEFAULT_TCP_LOGGING_PORT` is assumed.

    Unlike :func:`logging.basicConfig`, `filename` and `stream` is not mutually
    exclusive, i.e., if both are specified, the stream handler for each will be created.

    For `sentry_logging_level` and `sentry_logging_filter`, more than one item can be
    added delimiting with semicolon(s), in case more complicated filtering behavior is
    desired for tuning Sentry usage.
    """
    _acquire_lock()
    try:
        force = kwargs.pop("force", False)
        if force:
            for h in root.handlers[:]:
                root.removeHandler(h)
                h.close()

        if len(root.handlers) == 0:
            handlers = kwargs.pop("handlers", None)
            if handlers is None:
                if "stream" in kwargs and "filename" in kwargs:
                    raise ValueError(
                        "'stream' and 'filename' should not be specified together"
                    )
            else:
                if "stream" in kwargs or "filename" in kwargs:
                    raise ValueError(
                        "'stream' or 'filename' should not be "
                        "specified together with 'handlers'"
                    )

            if handlers is None:
                handlers = []

                filename = kwargs.pop("filename", None)
                mode = kwargs.pop("filemode", "a")
                handler_cls = kwargs.pop("file_handler", logging.FileHandler)
                if filename:
                    handlers.append(handler_cls(filename, mode=mode))

                stream = kwargs.pop("stream", None)
                if stream:
                    handlers.append(logging.StreamHandler(stream))

                socket = kwargs.pop("socket", None)
                if socket:
                    if ":" in socket:
                        host, port = socket.split(":", 1)
                        port = int(port)
                    else:
                        host = socket
                        port = logging.handlers.DEFAULT_TCP_LOGGING_PORT
                    handlers.append(logging.handlers.SocketHandler(host, port))

                # Add one stream handler at least.
                if not handlers:
                    handlers.append(logging.StreamHandler())

            dfs = kwargs.pop("datefmt", None)
            style = kwargs.pop("style", "%")
            if style not in _STYLES:
                raise ValueError("Style must be one of: %s" % ",".join(_STYLES.keys()))
            filter_arg = kwargs.pop("filter", None)
            fs = kwargs.pop("format", _STYLES[style][1])
            fmt = Formatter(fs, dfs, style)
            for h in handlers:
                if h.formatter is None:
                    h.setFormatter(fmt)
                _add_handler_to_root(h, filter_arg)

            level = kwargs.pop("level", None)
            _set_level(root, level)

            sentry_client = kwargs.pop("sentry_client", None)
            levels = kwargs.pop("sentry_logging_level", "WARNING")
            sentry_filter_args = kwargs.pop("sentry_logging_filter", "")
            if SentryHandler and sentry_client:
                delim = ";"
                levels = levels.split(delim)
                sentry_filter_args = sentry_filter_args.split(delim)
                for level, sentry_filter_arg in zip_longest(levels, sentry_filter_args):
                    h = SentryHandler(sentry_client)
                    _set_level(h, level)
                    _add_handler_to_root(h, sentry_filter_arg or filter_arg)

            if kwargs:
                keys = ", ".join(kwargs.keys())
                raise ValueError("Unrecognized argument(s): %s" % keys)

    finally:
        _release_lock()


def _set_level(handler, level):
    if level is not None:
        if isinstance(level, str):
            level = level.upper()
        elif not isinstance(level, int):
            raise ValueError("Logging level must be an int or str")
        handler.setLevel(level)


def _add_handler_to_root(handler, args):
    if args and isinstance(args, str):
        handler.addFilter(LoggingFilter(args))
    root.addHandler(handler)
