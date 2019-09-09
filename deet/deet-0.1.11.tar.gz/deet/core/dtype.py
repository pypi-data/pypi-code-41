# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Frootlab
#
# This file is part of Deet, https://www.frootlab.org/deet
#
#  Deet is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Deet is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  Deet. If not, see <http://www.gnu.org/licenses/>.
#
"""Data Types.

This module comprises a collection of data types, as specified in the SQL
standard. Thereby in most cases the types are directly taken from Python3
builtin or standard library types. For fixed length arrays the corresponding
ctypes type is used.

"""
__copyright__ = '2019 Frootlab'
__license__ = 'GPLv3'
__docformat__ = 'google'
__author__ = 'Frootlab Developers'
__email__ = 'contact@frootlab.org'
__authors__ = ['Patrick Michl <patrick.michl@frootlab.org>']

#import ctypes
import decimal
import datetime
import uuid

#
# Numeric Types
#

# Problem: Operators do not work!
# SmallInt = ctypes.c_short
# Integer = ctypes.c_int
# BigInt = ctypes.c_longlong
# Real = ctypes.c_float
Decimal = decimal.Decimal
Integer = int
Float = float

#
# Character Types
#

Varchar = str
Char = str # ctypes.create_string_buffer

#
# Binary Types
#

#
# Large object types
#


#
# Misc Types
#

Boolean = bool
UUID = uuid.UUID

#
# Date and time Types
#

Date = datetime.date
Time = datetime.time
TimeStamp = datetime.datetime
