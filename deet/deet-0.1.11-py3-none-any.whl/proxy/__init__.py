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
"""Database and Data Warehouse."""

__copyright__ = '2019 Frootlab'
__license__ = 'GPLv3'
__docformat__ = 'google'
__author__ = 'Frootlab Developers'
__email__ = 'contact@frootlab.org'
__authors__ = ['Patrick Michl <patrick.michl@frootlab.org>']

from typing import Any
from hup.base import pkg
from deet.core import table
from hup.errors import ConnectError
from hup.typing import Module

#
# Constructors
#

def connect(name: str, *args: Any, **kwds: Any) -> table.Proxy:
    """Connect Table Proxy

    Args:
        name: Name of module, which is used to connect a Table Proxy.
        *args: Arguments, that are passed to the class 'Table' of the given
            module.
        **kwds: Keyword arguments, that are passed to the class 'Table' of the
            given module.

    """
    module = pkg.get_submodule(name=name)
    if not isinstance(module, Module):
        raise ConnectError(f"module '{name}' does not exist")
    if not hasattr(module, 'Table'):
        raise ConnectError(f"module '{name}' does not contain a 'Table' class")
    return module.Table(*args, **kwds) # type: ignore
