# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


__author__ = "Sergi Blanch-Torne"
__maintainer__ = "Sergi Blanch-Torne"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2019, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Production"


class FakeString(object):

    _value = None

    def __init__(self, *args, **kwargs):
        super(FakeString, self).__init__(*args, **kwargs)


class Format(FakeString):
    def __init__(self, *args, **kwargs):
        super(Format, self).__init__(*args, **kwargs)
        self._value = 'ASCII'

    def value(self, value=None):
        if value is None:
            return self._value
        if value in ['ASC', 'ASCI', 'ASCII', 'BYT', 'BYTE', 'WOR', 'WORD']:
            self._value = value
