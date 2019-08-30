#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .settings import Settings as SETTINGS
from .utils.logger import logger
from .testrunner import TestRunner
from .testresult import TestResult
from importlib import reload


def RELOAD_SETTINGS():
    SETTINGS.__SPECIFIED__ = True

    from . import settings
    settings.Settings = SETTINGS
    from .utils.logger import Logger
    global logger
    logger = Logger(
        logger_dir=SETTINGS.LOG_DIR,
        console_level=SETTINGS.LOG_CONSOLE_LEVEL,
        file_level=SETTINGS.LOG_FILE_LEVEL,
        report_level=SETTINGS.LOG_REPORT_LEVEL
    ).get_new_logger(
        console_switch=SETTINGS.LOG_CONSOLE_SWITCH,
        file_switch=SETTINGS.LOG_FILE_SWITCH,
        report_switch=SETTINGS.LOG_REPORT_SWITCH
    )

    import punittest
    reload(punittest)

__all__ = ['SETTINGS', 'RELOAD_SETTINGS', 'TestRunner', 'TestResult', 'logger']


if SETTINGS.__SPECIFIED__ is True:
    from .punittest import PUnittest
    __all__.append('PUnittest')
