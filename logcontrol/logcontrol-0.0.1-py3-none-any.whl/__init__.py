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

"""Package to simplify and centralize handling of loggers created throughout a program"""


__author__ = "Brandon M. Pace"
__copyright__ = "Copyright 2019, Brandon M. Pace"
__license__ = "GNU LGPL 3+"
__maintainer__ = "Brandon M. Pace"
__status__ = "Development"
__version__ = "0.0.1"


from .loggers import add_handler, disable_propagation, enable_propagation, group_names, log_to_console, register_logger, set_level, set_log_file
