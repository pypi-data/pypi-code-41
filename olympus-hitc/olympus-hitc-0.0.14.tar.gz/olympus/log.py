#!/usr/local/python/bin
# coding=utf-8


__author__ = "tuantuan.lv <dangoakachan@foxmail.com>"
__status__ = "Development"

__all__ = ['set_logger', 'debug', 'info', 'warning', 'error',
           'critical', 'exception']

import os
import sys
import logging
import logging.handlers

# Color escape string
COLOR_RED = '\033[1;31m'
COLOR_GREEN = '\033[1;32m'
COLOR_YELLOW = '\033[1;33m'
COLOR_BLUE = '\033[1;34m'
COLOR_PURPLE = '\033[1;35m'
COLOR_CYAN = '\033[1;36m'
COLOR_GRAY = '\033[1;37m'
COLOR_WHITE = '\033[1;38m'
COLOR_RESET = '\033[1;0m'

# Define log color
LOG_COLORS = {
    #'DEBUG': '%s',
    'DEBUG': COLOR_BLUE + '%s' + COLOR_RESET,
    'INFO': COLOR_GREEN + '%s' + COLOR_RESET,
    'WARNING': COLOR_YELLOW + '%s' + COLOR_RESET,
    'ERROR': COLOR_RED + '%s' + COLOR_RESET,
    'CRITICAL': COLOR_RED + '%s' + COLOR_RESET,
    'EXCEPTION': COLOR_RED + '%s' + COLOR_RESET,
}

# Global logger
g_logger = None


class ColoredFormatter(logging.Formatter):
    '''A colorful formatter.'''

    def __init__(self, fmt=None, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)

    def format(self, record):
        level_name = record.levelname
        msg = logging.Formatter.format(self, record)

        return LOG_COLORS.get(level_name, '%s') % msg


def add_handler(cls, level, fmt, colorful, **kwargs):
    '''Add a configured handler to the global logger.'''
    global g_logger

    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.DEBUG)

    handler = cls(**kwargs)
    handler.setLevel(level)

    if colorful:
        formatter = ColoredFormatter(fmt)
    else:
        formatter = logging.Formatter(fmt)

    handler.setFormatter(formatter)
    g_logger.addHandler(handler)

    return handler


def add_streamhandler(level, fmt):
    '''Add a stream handler to the global logger.'''
    return add_handler(logging.StreamHandler, level, fmt, True)


def add_filehandler(level, fmt, filename, mode, backup_count, limit, when):
    '''Add a file handler to the global logger.'''
    kwargs = {}

    # If the filename is not set, use the default filename
    if filename is None:
        filename = getattr(sys.modules['__main__'], '__file__', 'log.py')
        filename = os.path.basename(filename.replace('.py', '.log'))
        filename = os.path.join('/tmp', filename)

        print ("?????????????",filename)
    kwargs['filename'] = filename

    # Choose the filehandler based on the passed arguments
    if backup_count == 0:  # Use FileHandler
        cls = logging.FileHandler
        kwargs['mode'] = mode
    elif when is None:  # Use RotatingFileHandler
        cls = logging.handlers.RotatingFileHandler
        kwargs['maxBytes'] = limit
        kwargs['backupCount'] = backup_count
        kwargs['mode'] = mode
    else:  # Use TimedRotatingFileHandler
        cls = logging.handlers.TimedRotatingFileHandler
        kwargs['when'] = when
        kwargs['interval'] = limit
        kwargs['backupCount'] = backup_count

    return add_handler(cls, level, fmt, False, **kwargs)


def init_logger():
    '''Reload the global logger.'''
    global g_logger

    if g_logger is None:
        g_logger = logging.getLogger()
    else:
        logging.shutdown()
        g_logger.handlers = []

    g_logger.setLevel(logging.DEBUG)


def set_logger(filename=None, mode='a', level='ERROR:DEBUG',
               fmt='[%(levelname)s] %(asctime)s - %(filename)s:%(lineno)d--- %(message)s',
               backup_count=5, limit=20480, when=None):
    '''Configure the global logger.'''
    level = level.split(':')

    if len(level) == 1:  # Both set to the same level
        s_level = f_level = level[0]
    else:
        s_level = level[0]  # StreamHandler log level
        f_level = level[1]  # FileHandler log level

    init_logger()
    add_streamhandler(s_level, fmt)
    add_filehandler(f_level, fmt, filename, mode, backup_count, limit, when)

    # Import the common log functions for convenient
    import_log_funcs()


def import_log_funcs():
    '''Import the common log functions from the global logger to the module.'''
    global g_logger

    curr_mod = sys.modules[__name__]
    log_funcs = ['debug', 'info', 'warning', 'error', 'critical',
                 'exception']

    for func_name in log_funcs:
        func = getattr(g_logger, func_name)
        setattr(curr_mod, func_name, func)


# Set a default logger
set_logger(filename = './olympus-hitc.log')
