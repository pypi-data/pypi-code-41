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
#  along with this program; If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import taurus
from time import sleep

__author__ = "Sergi Blanch-Torne"
__maintainer__ = "Sergi Blanch-Torne"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2019, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Production"


factory = taurus.core.TaurusManager().getFactory()
taurus_db = factory().getDatabase()
instances = taurus_db.getServerNameInstances("skippy")

def devices_states_and_versions():
    for instance in instances:
        devices = instance.devices()
        for devName in devices:
            if not devName.startswith('dserver'):
                try:
                    print(
                        "{:40s}\t{}\t{}".format(
                            devName,
                            devices[devName].getDeviceProxy()['state'].value,
                            devices[devName].getDeviceProxy()['version'].value)
                    )
                except Exception as exc:
                    print("{:40s}\texception".format(devName))

def restart_dservers():
    for instance in instances:
        devices = instance.devices()
        for devName in devices:
            if devName.startswith('dserver'):
                try:
                    device = devices[devName].getDeviceProxy()
                    device.RestartServer()
                    print("{}\tok".format(devName))
                except Exception as exc:
                     print("{}\t{}".format(devName, exc[0]))
