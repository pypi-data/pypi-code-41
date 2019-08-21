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

from numpy import linspace, pi, sin
from numpy.random import random, randint

__author__ = "Sergi Blanch-Torne"
__maintainer__ = "Sergi Blanch-Torne"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2019, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Production"


# First level


class FakeNumber(object):

    _value = None
    _upperLimit = None
    _lowerLimit = None

    def __init__(self, upperLimit=32768, lowerLimit=-32768, *args, **kwargs):
        super(FakeNumber, self).__init__(*args, **kwargs)
        self._upperLimit = upperLimit
        self._lowerLimit = lowerLimit

    def upperLimit(self, value=None):
        if value is None:
            return self._upperLimit
        self._upperLimit = int(value)

    def lowerLimit(self, value=None):
        if value is None:
            return self._lowerLimit
        self._lowerLimit = int(value)


# Second level


class FakeInteger(FakeNumber):
    def __init__(self, *args, **kwargs):
        super(FakeInteger, self).__init__(*args, **kwargs)
        self._value = randint(self._lowerLimit, self._upperLimit)


class FakeFloat(FakeNumber):
    def __init__(self, *args, **kwargs):
        super(FakeFloat, self).__init__(*args, **kwargs)
        self._value = randint(self._lowerLimit, self._upperLimit)+random()


class FakeArray(FakeNumber):
    _samples = None

    def __init__(self, samples=10, *args, **kwargs):
        super(FakeArray, self).__init__(*args, **kwargs)
        self._samples = samples

    def samples(self, value=None):
        if value is None:
            return self._samples
        self._samples = int(value)


# Third level


class ROinteger(FakeInteger):
    """ Read Only Integer """

    def __init__(self, *args, **kwargs):
        super(ROinteger, self).__init__(*args, **kwargs)

    def value(self):
        r = random()
        if r < 0.3:
            self._value += randint(self._lowerLimit / 100,
                                   self._upperLimit / 100)
        elif r < 0.6:
            self._value = randint(self._lowerLimit, self._upperLimit)
        return self._value


class RWinteger(FakeInteger):
    """ Read Write Integer """

    def __init__(self, *args, **kwargs):
        super(RWinteger, self).__init__(*args, **kwargs)

    def value(self, value=None):
        if value is None:
            return self._value
        value = int(value)
        if self._lowerLimit < value < self._upperLimit:
            self._value = value


class ROfloat(FakeFloat):
    """ Read Only floating point number """

    def __init__(self, *args, **kwargs):
        super(ROfloat, self).__init__(*args, **kwargs)

    def value(self):
        r = random()
        if r < 0.3:
            self._value += randint(self._lowerLimit/100,
                                   self._upperLimit/100)+random()
        elif r < 0.6:
            self._value = randint(self._lowerLimit,
                                  self._upperLimit)+random()
        return self._value


class RWfloat(FakeFloat):
    """ Read Write Integer """

    def __init__(self, *args, **kwargs):
        super(RWfloat, self).__init__(*args, **kwargs)

    def value(self, value=None):
        if value is None:
            return self._value
        value = float(value)
        if self._lowerLimit < value < self._upperLimit:
            self._value = value


class ROIntegerFallible(ROinteger):
    """ with a certain probability the value will not be a valid one """
    def __init__(self, *args, **kwargs):
        super(ROIntegerFallible, self).__init__(*args, **kwargs)
        self._threshold = 0.5

    def value(self):
        r = random()
        if r < self._threshold:
            return ROinteger.value(self)


class ROIntegerArray(FakeArray):
    def __init__(self, *args, **kwargs):
        super(ROIntegerArray, self).__init__(*args, **kwargs)
        self.value()

    def value(self):
        self._value = randint(self._lowerLimit, self._upperLimit,
                              size=self._samples)
        return self._value


class ROFloatArray(FakeArray):
    def __init__(self, *args, **kwargs):
        super(ROFloatArray, self).__init__(*args, **kwargs)
        self.value()

    def value(self):
        up = self._upperLimit
        low = self._lowerLimit
        arr = random(self._samples)
        self._value = (up - low) * arr + low
        return self._value

class Waveform(FakeArray):
    def __init__(self, *args, **kwargs):
        super(Waveform, self).__init__(*args, **kwargs)
        self._switch = False
        self._periods = 1
        self.samples()

    def samples(self, value=None):
        # overloaded to recalculate only if nsample changes
        were = self._samples
        ret = super(Waveform, self).samples(value)
        if were != self._samples:
            self._refreshValue()
        return ret

    def switch(self, value=None):
        if value is None:
            return "ON" if self._switch else "OFF"
        if isinstance(value, str):
            value = value.lower()
        if value in [False, 0, '0', 'false', 'off']:
            self._switch = False
        elif value in [True, 1, '1', 'true', 'on']:
            self._switch = True
        if self._switch:
            self._refreshValue()

    def periods(self, value=None):
        if value is None:
            return self._periods
        self._periods = int(value)
        self._refreshValue()

    def value(self):
        if self._switch:
            return self._value
        return ''
        # This else return does something bad on purpose. Empty string to
        # the device means possible communication error. So the device must be
        # robust.

    def _refreshValue(self):
        self._value = sin(linspace(0, self._periods * 2 * pi, self._samples))

class ROFloatChannel(FakeArray):

    _value = None
    _upperLimit = None
    _lowerLimit = None
    _samples = None
    _switches = None

    def __init__(self, channels, *args, **kwargs):
        super(ROFloatChannel, self).__init__(*args, **kwargs)
        self._upperLimit = [self._upperLimit]*channels
        self._lowerLimit = [self._lowerLimit]*channels
        self._samples = [self._samples]*channels
        self._switches = [False]*channels
        self._value = [None]*channels

    def value(self, ch):
        up = self._upperLimit[ch-1]
        low = self._lowerLimit[ch-1]
        arr = random(self._samples[ch-1])
        self._value[ch-1] = (up-low)*arr+low
        return self._value[ch-1]

    def upperLimit(self, ch, value=None):
        if value is None:
            return self._upperLimit[ch-1]
        self._upperLimit[ch-1] = float(value)

    def lowerLimit(self, ch, value=None):
        if value is None:
            return self._lowerLimit[ch-1]
        self._lowerLimit[ch-1] = float(value)

    def samples(self, ch, value=None):
        if value is None:
            return self._samples
        self._samples = int(value)

    def switch(self, ch, value=None):
        if value is None:
            return "ON" if self._switches[ch-1] else "OFF"
        if isinstance(value, str):
            value = value.lower()
        if value in [False, 0, '0', 'false', 'off']:
            self._switches[ch-1] = False
        elif value in [True, 1, '1', 'true', 'on']:
            self._switches[ch-1] = True
