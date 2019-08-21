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

import PyTango

__author__ = "Sergi Blanch-Torne"
__maintainer__ = "Sergi Blanch-Torne"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2016, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Development"


Attribute('Function',
          {'description': 'Used to select the measurement function of the '
           'instrument.',
           'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "sense:func?",
           'readFormula': 'VALUE.strip()',
           'writeCmd': lambda value: "sense:func '%s'" % (value),
           'writeValues': ['VOLT:DC', 'VOLTA:DC', 'VOLTAG:DC', 'VOLTAGE:DC',
                           'VOLT:AC', 'VOLTA:AC', 'VOLTAG:AC', 'VOLTAGE:AC',
                           # 'current:dc', 'current:ac',
                           # 'resistence', 'fresistance',
                           # 'period', 'frequency',
                           # 'temperature', 'diode', 'continuity'
                           ],
           })

# DC ---
Attribute('VoltageDCSpeed',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "sense:volt:dc:nplc?",
           'writeCmd': lambda value: "sense:volt:dc:nplc %s" % (value),
           })

Attribute('VoltageDCRange',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "sense:volt:dc:rang?",
           'writeCmd': lambda value: "sense:volt:dc:rang %s" % (value),
           })

Attribute('VoltageDCResolution',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "sense:volt:dc:dig?",
           'writeCmd': lambda value: "sense:volt:dc:dig %s" % (value),
           })

Attribute('VoltageDCAverage',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "sense:volt:dc:aver:stat?",
           'writeCmd': lambda value: "sense:volt:dc:aver:stat %s"
           % ('ON' if value else 'OFF'),
           })

Attribute('VoltageDCMovingAverage',
          {''
           'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "sense:volt:dc:aver:tcon?",
           'readFormula': 'VALUE.strip()',
           'writeCmd': lambda value: "sense:volt:dc:aver:tcon %s" % (value),
           'writeValues': ['MOV', 'MOVI', 'MOVIN', 'MOVING',
                           'REP', 'REPE', 'REPEA', 'REPEAT'],
           })

# AC ---
Attribute('VoltageACBandwidth',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "sense:volt:ac:det:band?",
           'writeCmd': lambda value: "sense:volt:ac:det:band %s" % (value),
           })

Attribute('VoltageACSpeed',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "sense:volt:ac:nplc?",
           'writeCmd': lambda value: "sense:volt:ac:nplc %s" % (value),
           })

Attribute('VoltageACRange',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "sense:volt:ac:rang?",
           'writeCmd': lambda value: "sense:volt:ac:rang %s" % (value),
           })

Attribute('VoltageACResolution',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "sense:volt:ac:dig?",
           'writeCmd': lambda value: "sense:volt:ac:dig %s" % (value),
           })

Attribute('VoltageACAverage',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "sense:volt:ac:aver:stat?",
           'writeCmd': lambda value: "sense:volt:ac:aver:stat %s"
           % ('ON' if value else 'OFF'),
           })

Attribute('VoltageACMovingAverage',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "sense:volt:ac:aver:tcon?",
           'readFormula': 'VALUE.strip()',
           'writeCmd': lambda value: "sense:volt:ac:aver:tcon %s" % (value),
           'writeValues': ['MOV', 'MOVI', 'MOVIN', 'MOVING',
                           'REP', 'REPE', 'REPEA', 'REPEAT'],
           })

# Measurements ---
Attribute('Measure',
          {'description': 'Used to read the latest instrument reading.',
           'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "sense:data?",
           })

Attribute('MeasureStatus',
          {'description': 'Used to read the event registers bit array',
           'type': PyTango.CmdArgType.DevShort,
           'dim': [0],
           'readCmd': "stat:meas:even?",
           })
