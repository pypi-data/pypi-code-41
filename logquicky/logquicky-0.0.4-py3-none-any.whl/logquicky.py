import logging
from logging.handlers import RotatingFileHandler
import sys
import os

# Some colors to make the next part more readable
LEVEL_FORMAT = {
    "TRACE": "\033[0;35m",  # purple
    "DEBUG": "\033[0;34m",  # blue
    "INFO": "\033[0;32m",  # green
    "WARN": "\033[0;33m",  # orange
    "ERROR": "\033[0;31m",  # red
    "CRITICAL": "\033[1;31m",  # Bold red
}

# Reset sequence to remove color
RESET_SEQ = "\033[0m"
TRACE_LVL = 5


def create(*args, **kwargs):

    """ Legacy shorthand for loading a logger."""

    # This method is no longer necessary, as create will return the same logger.
    logging.getLogger("logquicky").warning("Logquicky Warning: Create method is deprecated. Just use 'load'.")
    return load(*args, **kwargs)


def load(logger_name, file: str = None, rewrite: bool = False, level: str = "INFO", propagate=False):

    """ Configures a logger object. If the logger was already configured, it will return the existing logger but not reconfigure it. """

    if logger_name in logging.Logger.manager.loggerDict.keys():
        return logging.getLogger(logger_name)

    log = logging.getLogger(logger_name)
    log.propagate = propagate

    # Nicer to show just 'WARN' instead of WARNING in the output.
    logging.addLevelName(logging.WARNING, "WARN")
    # Add the trace level.
    logging.addLevelName(TRACE_LVL, "TRACE")

    # Configure the logger to screen / STDOUT
    stream_formatter = BetterFormatter(
        "%(asctime)s %(name)s [$COLOR%(levelname)s$RESET] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Fileformatter should not include colors.
    file_formatter = BetterFormatter("%(asctime)s %(name)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(stream_formatter)
    if rewrite:
        stream_handler.terminator = ""
    log.addHandler(stream_handler)

    try:
        if file:
            # If file is "True", check environment var for log location, or fall back to logger_name in current directory."

            if type(file) == bool:
                file = os.environ.get("LOG_FILE_OUTPUT", logger_name)

            file_handler = RotatingFileHandler(file, mode="a", maxBytes=1000000, backupCount=2, encoding="utf-8")
            file_handler.setFormatter(file_formatter)
            log.addHandler(file_handler)
    except PermissionError as e:
        logging.getLogger("logquicky").error(
            f"Logquicky cannot write log to file in '{file}' due to permission issues."
        )

    # Set the final level
    log.setLevel(level)
    return log


class BetterFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        levelname = record.levelname

        message = logging.Formatter.format(self, record)

        message = message.replace("$COLOR", LEVEL_FORMAT.get(levelname, ""))
        message = message.replace("$RESET", "\033[0m")
        return message


def trace(self, message, *args, **kwargs):

    if self.isEnabledFor(TRACE_LVL):
        self._log(TRACE_LVL, message, args, **kwargs)


# Add the trace option to the functions of this logger.
logging.Logger.trace = trace

