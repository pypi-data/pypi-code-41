# coding=utf-8
from functools import partial
from logging import addLevelName, getLogger as _getLogger, setLoggerClass, \
    FileHandler, Filter, Formatter, Logger, LogRecord, StreamHandler, CRITICAL, DEBUG, ERROR, INFO, NOTSET, WARNING
from string import Template
from typing import cast, Any, Callable, Iterable, Mapping


# Do not import anything from the local package here, otherwise a circular dependency is likely to happen when other
# parts of the package require logging


NOTICE = INFO + 5


_logging_initialized = False

_logger_class_set = False


_color_mapping = {
    DEBUG: 'cyan',
    NOTICE: 'green',
    WARNING: 'yellow',
    ERROR: 'red',
    CRITICAL: 'red'}


_level_log_message = Template('[$level_name] $message')
_no_level_log_message = Template('$message')


# noinspection PyPep8Naming
def getLogger(name=None):
    # type: (str) -> NoticeLogger
    return cast(NoticeLogger, _getLogger(name))


def _format_colored_message(template, color_encoder, log_record):
    # type: (Template, Callable[..., str], LogRecord) -> str
    if log_record.levelno not in _color_mapping:
        return _level_log_message.substitute(
            level_name=log_record.levelname,
            message=log_record.msg)

    color = _color_mapping[log_record.levelno]
    level_name = color_encoder(log_record.levelname, color, attrs=['bold'])
    message = color_encoder(log_record.msg, color)

    formatted_message = template.substitute(
        level_name=level_name,
        message=message)

    return formatted_message


def _create_color_formatters():
    # type: () -> (ModularFormatter, ModularFormatter)
    from colorama import init as install_colorama
    from termcolor import colored

    install_colorama()

    # These partials will function exactly as a LogRecord constructor
    format_log_message_with_level = partial(_format_colored_message, _level_log_message, colored)
    format_log_message_without_level = partial(_format_colored_message, _no_level_log_message, colored)

    # noinspection PyTypeChecker
    default_formatter = ModularFormatter(format_log_message_with_level)
    # noinspection PyTypeChecker
    notice_formatter = ModularFormatter(format_log_message_without_level)

    return default_formatter, notice_formatter


def _create_no_color_formatters():
    # type: () -> (ModularFormatter, ModularFormatter)
    no_level_no_color_formatter = Formatter('%(message)s')
    default_formatter = no_level_no_color_formatter
    notice_formatter = no_level_no_color_formatter

    return default_formatter, notice_formatter


def setup_logging(log_level=INFO, log_file=None, use_colors=None):
    # type: (int, str, bool) -> None
    global _logging_initialized

    if _logging_initialized:
        return

    logger = getLogger()
    if logger.handlers:
        return

    addLevelName(NOTICE, 'NOTICE')

    from .this_package_metadata import package_metadata

    colors_feature = package_metadata.extra_features['color']

    if use_colors and not colors_feature.is_installed:
        colors_feature.raise_not_installed('Unable to use colors with logging')

    if use_colors is None and package_metadata.extra_features.is_installed('color'):
        use_colors = True
    else:
        use_colors = False

    default_formatter, notice_formatter = _create_color_formatters() if use_colors else _create_no_color_formatters()

    level_formatter = LevelFormatter(default_formatter=default_formatter)
    level_formatter.add_formatter_for_level(INFO, Formatter('%(message)s'))
    level_formatter.add_formatter_for_level(NOTICE, notice_formatter)
    console_formatter = level_formatter

    from sys import stdout, stderr
    stdout_handler = StreamHandler(stdout)
    stdout_handler.setLevel(DEBUG)
    stdout_handler.addFilter(LevelFilter(NOTICE))
    stdout_handler.setFormatter(console_formatter)

    stderr_handler = StreamHandler(stderr)
    stderr_handler.setLevel(WARNING)
    stderr_handler.setFormatter(console_formatter)

    logger.setLevel(log_level)
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)

    _logging_initialized = True

    if not log_file:
        return

    file_formatter = Formatter('%(name)-20s - %(levelname)-10s - %(asctime)-30s:  %(message)s')
    log_file_handler = FileHandler(log_file)
    log_file_handler.setLevel(DEBUG)
    log_file_handler.setFormatter(file_formatter)
    logger.addHandler(log_file_handler)


class LevelFilter(Filter):
    def __init__(self, max_level):
        # type: (int) -> None
        super(LevelFilter, self).__init__()
        self._max_level = max_level

    def filter(self, record):
        # type: (LogRecord) -> bool
        return record.levelno <= self._max_level


class LevelFormatter(Formatter):
    def __init__(self, default_formatter=None):
        # type: () -> None
        super(LevelFormatter, self).__init__()

        if not default_formatter:
            default_formatter = Formatter('%(message)s')

        self._default_formatter = default_formatter
        self._formatters = dict()

    def add_formatter_for_level(self, level, formatter):
        # type: (int, Formatter) -> None
        self._formatters[level] = formatter

    def format(self, record):
        # type: (LogRecord) -> str
        if record.levelno in self._formatters:
            formatter = self._formatters[record.levelno]
        else:
            formatter = self._default_formatter

        return formatter.format(record)


class ModularFormatter(Formatter):
    def __init__(self, format_log_record):
        # type: (Callable[[LogRecord], str]) -> None
        super(ModularFormatter, self).__init__()

        self._format_log_record = format_log_record

    def format(self, log_record):
        # type: (LogRecord) -> str
        return self._format_log_record(log_record)


class NoticeLogger(Logger):
    def __init__(self, name, level=NOTSET):
        # type: (str, int) -> None
        super(NoticeLogger, self).__init__(name, level)

    def notice(self, message, *args, **kwargs):
        # type: (str, Iterable[Any], Mapping[str, Any]) -> None
        if not self.isEnabledFor(NOTICE):
            return

        self._log(NOTICE, message, args, **kwargs)


if not _logger_class_set:
    setLoggerClass(NoticeLogger)

    _logger_class_set = True
