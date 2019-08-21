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
__copyright__ = "Copyright 2015, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Production"

# import scpi
__version__ = '1.5.0'


class InstrumentIdentification(object):
    def __init__(self, manufacturer, instrument, serialNumber,
                 firmwareVersion):
        object.__init__(self)
        self.manufacturer = manufacturer
        self.instrument = instrument
        self.serialNumber = serialNumber
        self.firmwareVersion = firmwareVersion

    @property
    def manufacturer(self):
        return self._manufacturerName

    @manufacturer.setter
    def manufacturer(self, value):
        self._manufacturerName = str(value)

    @property
    def instrument(self):
        return self._instrumentName

    @instrument.setter
    def instrument(self, value):
        self._instrumentName = str(value)

    @property
    def serialNumber(self):
        return self._serialNumber

    @serialNumber.setter
    def serialNumber(self, value):
        self._serialNumber = str(value)

    @property
    def firmwareVersion(self):
        return self._firmwareVersion

    @firmwareVersion.setter
    def firmwareVersion(self, value):
        self._firmwareVersion = str(value)

    def idn(self):
        return "%s,%s,%s,%s" % (self.manufacturer, self.instrument,
                                self.serialNumber, self.firmwareVersion)


def main():
    instrument = InstrumentIdentification('ALBA', 'test', 0, __version__)
    print(instrument.idn())

if __name__ == '__main__':
    main()
