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

from fakeInstrument import FakeInstrument, TestManager

# From a python console, in the package directory one can call:
# >>> from tester.fakeInstrument import TestManager
# >>> manager = TestManager()
# and have in a python console the two objects of the Testbench.
# Then it can be manually tested what happens when an instrument goes down,
# simulated by a call:
# >>> instrument.close()
# Having a device proxy, an interaction with the instrument will produce a
# decay to fault. Calling instrument.open() and Init() the proxy should
# recover the communication.
# TODO: the device proxy will have the functionality (back, temporally removed)
# to auto-recover by checking from time to time if the instrument is back.
