#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
file name: __init__.py
author: Shlomi Ben-David
file version: 0.0.1
"""
import os
import sys
import time
import logging

COLOR_STREAM = False

try:
    from termcolor import colored
    COLOR_STREAM = True
except ImportError:
    pass


class ColoredStreamHandler(logging.StreamHandler):
    """ Colored Logger Stream Handler class """
    def __init__(self, stream):
        logging.StreamHandler.__init__(self, stream)

    def format(self, record):
        """
        Format the specified record.

        If a formatter is set, use it. Otherwise, use the default formatter
        for the module.

        Available text colors:
        red, green, yellow, blue, magenta, cyan, white.

        Available text highlights:
        on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white.

        Available attributes:
        bold, dark, underline, blink, reverse, concealed.

        Example:
        colored('Hello, World!', 'red', 'on_grey', ['blue', 'blink'])
        colored('Hello, World!', 'green')
        """
        if self.formatter:
            fmt = self.formatter
        else:
            fmt = logging.Formatter()

        level_to_color_mapper = {
            'INFO': 'white',
            'DEBUG': 'blue',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        }

        color = level_to_color_mapper.get(record.levelname) or 'white'
        setattr(record, 'msg', colored(record.msg, color))

        return fmt.format(record)


def get_version(caller, version_file):
    """
    Get the version number from the *_VERSION file

    :param str caller: source file caller (i.e __file__)
    :param str version_file: a version file to get the version number from
    return: (str) version number or '0.0.0' if *_VERSION file doesn't exists
    """
    version_path = ''
    current_dir = os.path.dirname(os.path.abspath(caller))
    for _root, directories, files in os.walk(current_dir):
        for _file in files:
            if _file == version_file:
                version_path = os.path.join(_root, _file)
                break
        else:
            continue
        break

    if not os.path.exists(version_path):
        return '0.0.0'

    with open(version_path, 'r') as ifile:
        return ifile.read().strip()


def init_logging(log_file, verbose=False, console=False):
    """
    Logger initialization

    :param str log_file: log file name
    :param bool console: if set to True will print logs both to a file
        and to stdout
    :param bool verbose: if set to True will print more information

    NOTE: The bellow snippet taken from the logging Formatter class

    %(name)s            Name of the logger (logging channel)
    %(levelno)s         Numeric logging level for the message (DEBUG, INFO,
                        WARNING, ERROR, CRITICAL)
    %(levelname)s       Text logging level for the message ("DEBUG", "INFO",
                        "WARNING", "ERROR", "CRITICAL")
    %(pathname)s        Full pathname of the source file where the logging
                        call was issued (if available)
    %(filename)s        Filename portion of pathname
    %(module)s          Module (name portion of filename)
    %(lineno)d          Source line number where the logging call was issued
                        (if available)
    %(funcName)s        Function name
    %(created)f         Time when the LogRecord was created (time.time()
                        return value)
    %(asctime)s         Textual time when the LogRecord was created
    %(msecs)d           Millisecond portion of the creation time
    %(relativeCreated)d Time in milliseconds when the LogRecord was created,
                        relative to the time the logging module was loaded
                        (typically at application startup time)
    %(thread)d          Thread ID (if available)
    %(threadName)s      Thread name (if available)
    %(process)d         Process ID (if available)
    %(message)s         The result of record.getMessage(), computed just as
                        the record is emitted
    """
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    file_log_formatter = logging.Formatter(
        "%(asctime)s [%(module)s] [%(levelname)s] %(message)s"
    )
    console_log_formatter = logging.Formatter(
        "%(asctime)s [%(process)d] [%(module)s] [%(levelname)s] %(message)s"
    )

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(file_log_formatter)
        logger.addHandler(file_handler)

    if COLOR_STREAM:
        StreamHandler = ColoredStreamHandler
    else:
        StreamHandler = logging.StreamHandler

    if console:
        console_handler = StreamHandler(sys.stdout)
        console_handler.setFormatter(console_log_formatter)
        logger.addHandler(console_handler)


def timer(func):
    """
    This function used as a decorator function to check
    elapsed time of each passed function

    :param func: original function
    :return: wrapper function
    """
    def wrapper_function(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        tword = 'seconds'
        if 60 <= elapsed_time < 3600:
            elapsed_time /= 60
            tword = 'minutes'
        if elapsed_time >= 3600:
            elapsed_time /= 60
            tword = 'hours'
        print(
            "==> {0} run {1:.2f} {2}"
            .format(func.__name__, elapsed_time, tword)
        )
        return result

    return wrapper_function
