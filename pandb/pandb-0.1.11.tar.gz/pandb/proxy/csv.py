# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Frootlab
#
# This file is part of Pandora, https://www.frootlab.org/pandora
#
#  Pandora is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Pandora is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  Pandora. If not, see <http://www.gnu.org/licenses/>.
#
"""Table Proxy for textfiles containing delimiter-separated values."""

__copyright__ = '2019 Frootlab'
__license__ = 'GPLv3'
__docformat__ = 'google'
__author__ = 'Frootlab Developers'
__email__ = 'contact@frootlab.org'
__authors__ = ['Patrick Michl <patrick.michl@frootlab.org>']

from typing import Any
from hup.base import attrib
from hup.errors import ConnectError, DisconnectError
from hup.io import csv, ini
from hup.io import FileRef, FileRefClassInfo
from pandb.core import table

#
# CSV Table Proxy Class
#

class Table(table.Proxy):
    """CSV-Table Proxy."""

    #
    # Public Attributes
    #

    # Remove setter from name, since the name is determined by the file name
    name: property = attrib.Virtual('_get_name')
    name.__doc__ = "Name of the table."

    #
    # Protected Attributes
    #

    _fileref: property = attrib.Temporary(dtype=FileRefClassInfo)
    _file: property = attrib.Temporary(dtype=csv.File)

    #
    # Special Methods
    #

    def __init__(self, file: FileRef, *args: Any, **kwds: Any) -> None:
        """Initialize CSV-Table Proxy.

        Args:
            file:
            *args: Additional arguments, that are passed to
                :class:`csv.File <hup.base.io.csv.File>`.
            **kwds: Additional keyword arguments, that are passed to csv.File.

        """
        super().__init__() # Initialize table proxy
        self.connect(file, *args, **kwds) # Connect CSV File
        self._post_init() # Run post init hook

    #
    # Public Methods
    #

    def connect( # type: ignore
            self, file: FileRef, *args: Any, **kwds: Any) -> None:
        """Connect to given file reference."""
        if self._connected:
            raise ConnectError("the connection already has been established")

        # Create and reference CSV file
        fh = csv.File(file, *args, **kwds)
        self._file = fh

        # Get table name, structure and and metadata from CSV file
        name = fh.name.split('.', 1)[0]
        fields = fh.fields
        metadata = ini.decode(fh.comment, flat=True, autocast=True)

        # Create table
        self.create(name, fields, metadata=metadata)
        self._connected = True

    def disconnect(self) -> None:
        """Close connection to referenced file."""
        if not self._connected:
            raise DisconnectError("the proxy has not yet been connected")
        self._file.close()
        self._connected = False

    def pull(self) -> None:
        """Pull all rows from CSV-File."""
        comment = self._file.comment
        mapping = ini.decode(comment, flat=True, autocast=True)
        self._metadata.update(mapping)
        name = self._file.name.split('.', 1)[0] # Get name from filename
        self._set_name(name)
        rows = self._file.read()
        self.insert(rows)

    def push(self) -> None:
        """Push all rows to CSV-File."""
        comment = ini.encode(self.metadata, flat=True)
        self._file.comment = comment
        rows = self.select()
        self._file.write(rows)
