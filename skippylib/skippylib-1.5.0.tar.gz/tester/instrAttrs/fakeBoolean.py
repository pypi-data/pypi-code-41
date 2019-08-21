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

from numpy import array
from random import getrandbits

__author__ = "Sergi Blanch-Torne"
__maintainer__ = "Sergi Blanch-Torne"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2019, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Production"


class FakeBoolean(object):
    _value = None

    def __init__(self, *args, **kwargs):
        super(FakeBoolean, self).__init__(*args, **kwargs)


class FakeBooleanArray(FakeBoolean):
    _samples = None

    def __init__(self, samples=8, *args, **kwargs):
        super(FakeBooleanArray, self).__init__(*args, **kwargs)
        self._samples = samples

    def samples(self, value=None):
        if value is None:
            return self._samples
        self._samples = int(value)


class ROboolean(FakeBoolean):
    """ Read Only Boolean """

    def __init__(self, *args, **kwargs):
        super(ROboolean, self).__init__(*args, **kwargs)

    def value(self):
        self._value = bool(getrandbits(1))
        return self._value


class RWboolean(FakeBoolean):
    """ Read Write Boolean """

    def __init__(self, *args, **kwargs):
        super(RWboolean, self).__init__(*args, **kwargs)
        self._value = False

    def value(self, value=None):
        if value is None:
            return self._value
        if isinstance(value, str):
            if value.lower() in ['false', 'true']:
                self._value = True if value.lower() == 'true' else False
            else:
                try:
                    self._value = bool(int(value))
                except:
                    pass


class ROBooleanArray(FakeBooleanArray):
    def __init__(self, *args, **kwargs):
        super(ROBooleanArray, self).__init__(*args, **kwargs)
        self.value()

    def value(self):
        self._value = getrandbits(self._samples)
        lst = []
        for i in range(self._samples):
            lst.insert(0, bool(self._value >> i & 1))
        return array(lst)
