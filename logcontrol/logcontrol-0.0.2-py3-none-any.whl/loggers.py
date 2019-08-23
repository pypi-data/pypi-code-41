#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright (C) 2019 Brandon M. Pace
#
# This file is part of logcontrol
#
# logcontrol is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# logcontrol is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with logcontrol.
# If not, see <https://www.gnu.org/licenses/>.

"""module for creating and storing loggers"""


import logging
import threading

from logging.handlers import RotatingFileHandler
from typing import Dict, List, Set
from .constants import CONSOLE_HANDLER_NAME, DEFAULT_CONSOLE_LOG_FORMAT, DEFAULT_LOG_FORMAT


group_handlers: Dict[str, Set[logging.Handler]] = {}
group_log_levels: Dict[str, int] = {}
group_propagation: Dict[str, bool] = {}
logger_groups: Dict[str, Set[logging.Logger]] = {}
logger_lock = threading.RLock()
loggers: Set[logging.Logger] = set()
root_logger = logging.getLogger()


def add_handler(handler: logging.Handler, group: str = ''):
    """Add a log handler to a group of loggers (or the root logger if no group provided)"""
    if group:
        validate_group_exists(group)

        with logger_lock:
            for logger in logger_groups[group]:
                if handler in logger.handlers:
                    root_logger.warning(f'handler "{handler.name}" already enabled for the logger "{logger.name}"')
                    continue
                else:
                    logger.addHandler(handler)

            if group in group_handlers:
                group_handlers[group].add(handler)
            else:
                group_handlers[group] = {handler}

            root_logger.debug(f'handler "{handler.name}" added to logger group {group}')
    else:
        if handler in root_logger.handlers:
            root_logger.warning(f'handler "{handler.name}" already enabled for the root logger')
        else:
            root_logger.addHandler(handler)
            root_logger.debug(f'handler "{handler.name}" added to the root logger')


def disable_propagation(group: str):
    """
    Disable propagation for a specific group of loggers.
    This means no logger lower in the hierarchy will process messages from it and its children.
    """
    validate_group_exists(group)

    with logger_lock:
        for logger in logger_groups[group]:
            logger.propagate = False
        group_propagation[group] = False
        root_logger.debug(f'propagation disabled for logger group "{group}"')


def enable_propagation(group: str):
    """
    Enable propagation for a specific group of loggers.
    This means any logger lower in the hierarchy will process messages from it and its children.
    """
    validate_group_exists(group)

    with logger_lock:
        for logger in logger_groups[group]:
            logger.propagate = True
        group_propagation[group] = True
        root_logger.debug(f'propagation enabled for logger group "{group}"')


def group_level(group: str) -> int:
    """
    Get the integer log level for a group
    """
    with logger_lock:
        validate_group_exists(group)
        return group_log_levels[group]


def group_level_name(group: str) -> int:
    """
    Get the string log level name for a group
    """
    with logger_lock:
        validate_group_exists(group)
        return logging.getLevelName(group_log_levels[group])


def group_levels() -> Dict[str, int]:
    """
    Get a dictionary with group names as keys and the integer levels as values
    """
    with logger_lock:
        return group_log_levels.copy()


def group_level_names() -> Dict[str, str]:
    """
    Get a dictionary with group names as keys and string level name as values
    This can be useful for populating a debug options window that allows configuring the different groups.
    """
    with logger_lock:
        return {group: logging.getLevelName(level) for group, level in group_log_levels.items()}


def group_names() -> List[str]:
    """
    Get a sorted list of group names that have been added
    """
    with logger_lock:
        return sorted([group for group in logger_groups])


def log_to_console(group: str = '', fmt: str = None, datefmt: str = None):
    """
    Enable printing log items to the console
    If a group name is passed, then loggers in that group will log to console.
    If a group name is not passed or empty, the root logger will log to console.
    If a format string is passed to via fmt or datefmt, it will be used.
    If a format is not passed, a default is used.
    (see logging.Formatter and LogRecord attributes documentation for more information about format strings)
    NOTE: If you do not have a handler for the root logger, you may see all loggers output on the console.
    """
    log_format = (DEFAULT_CONSOLE_LOG_FORMAT if fmt is None else fmt)
    formatter = logging.Formatter(fmt=log_format, datefmt=datefmt)
    console_handler = logging.StreamHandler()
    console_handler.name = CONSOLE_HANDLER_NAME
    console_handler.setFormatter(formatter)

    add_handler(console_handler, group=group)


def register_logger(logger: logging.Logger, group: str):
    """
    Add a logger to be controlled. The group name can be a user-friendly one if you wish.
    """
    if not (logger and isinstance(logger, logging.Logger)):
        raise ValueError(f'unable to register invalid object: {logger}')
    elif not (group and isinstance(group, str)):
        raise ValueError('a valid group name string is required')

    with logger_lock:
        if logger in loggers:
            raise ValueError(f'logger already registered: {logger}')

        loggers.add(logger)

        if group in logger_groups:
            logger_groups[group].add(logger)
        else:
            logger_groups[group] = {logger}

        if group in group_log_levels:
            logger.setLevel(group_log_levels[group])
        else:
            effective_level = logger.getEffectiveLevel()
            group_log_levels[group] = effective_level
            logger.setLevel(effective_level)

        if group in group_handlers:
            for handler in group_handlers[group]:
                logger.addHandler(handler)

        if group in group_propagation:
            logger.propagate = group_propagation[group]


def set_level(level: int, group: str = ''):
    """
    Set log level for root logger or a specific group of loggers.
    level is as seen in Python's logging module documentation (e.g. logging.DEBUG, logging.WARNING, logging.INFO)
    group name is optional. If no group is passed, the level is configured for the root logger.
    """
    level_name = logging.getLevelName(level)

    if group:
        validate_group_exists(group)

        with logger_lock:
            for logger in logger_groups[group]:
                logger.setLevel(level)
            root_logger.debug(f'log level set to "{level_name}" for logger group "{group}"')
    else:
        root_logger.setLevel(level)
        root_logger.debug(f'log level set to "{level_name}"')


def set_log_file(file_path: str, group: str = '', fmt: str = None, datefmt: str = None, max_size: int = 5242880, roll_count: int = 9):
    """
    Set the log file for the root logger (or group, if given)

    The file path is the destination log file
    If a group name is provided, it will only apply to the specific group.
    If a format string is passed to via fmt or datefmt, it will be used.
    If a format is not passed, a default is used.
    (see logging.Formatter and LogRecord attributes documentation for more information about format strings)
    The max size is in bytes
    The roll count determines how many files beyond the current log are kept (e.g. log_file.1, log_file.2, etc.)
    """
    format_string = (fmt if fmt else DEFAULT_LOG_FORMAT)
    formatter = logging.Formatter(fmt=format_string, datefmt=datefmt)
    rotation_handler = RotatingFileHandler(file_path, maxBytes=max_size, backupCount=roll_count)
    rotation_handler.setFormatter(formatter)
    add_handler(rotation_handler, group=group)


def validate_group_exists(group: str):
    """Internal function to validate that a group has been added"""
    if group not in logger_groups:
        raise ValueError(f'no logger group with name: {group}')
