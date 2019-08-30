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

"""module to hold constants for use in the package"""


import logging

log_level_integers = frozenset((logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL))
log_level_strings = frozenset([logging.getLevelName(level) for level in log_level_integers])

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


pid_tid_tag = '[%(process)d %(thread)d]'
time_tag = '%(asctime)s'
level_tag = '%(levelname)s'
thread_name_tag = '%(threadName)-10s'
code_line_tag = '%(filename)s:%(funcName)s:%(lineno)d'
log_message_tag = '%(message)s'

CONSOLE_HANDLER_NAME = 'console_logger_stream'
DEFAULT_CONSOLE_LOG_FORMAT = f'{pid_tid_tag} {time_tag} ({thread_name_tag}) - [{level_tag}] {log_message_tag}'
DEFAULT_LOG_FORMAT = f'{pid_tid_tag} {time_tag} {level_tag} - ({thread_name_tag}) - {code_line_tag} - {log_message_tag}'
