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


Attribute('Output',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "print(smua.source.output)\n?",
           'readFormula': "bool(float(VALUE))",
           'writeCmd': lambda value: "smua.source.output=smua.OUTPUT_%s"
           % ("ON" if value else "OFF"),
           })

# Source ---
Attribute('SourceCurrentAutoRange',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "print(smua.source.autorangei)\n?",
           'readFormula': "bool(float(VALUE))",
           'writeCmd': lambda value: "smua.source.autorangei=smua.AUTORANGE_%s"
           % ("ON" if value else "OFF"),
           })

Attribute('SourceVoltageAutoRange',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "print(smua.source.autorangev)\n?",
           'readFormula': "bool(float(VALUE))",
           'writeCmd': lambda value: "smua.source.autorangev=smua.AUTORANGE_%s"
           % ("ON" if value else "OFF"),
           })

Attribute('SourceFunction',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "print(smua.source.func)\n?",
           'readFormula': "{0: 'AMPS', 1: 'VOLTS'}[int(float(VALUE))]",
           'writeCmd': lambda value: "smua.source.func=smua.OUTPUT_DC%s"
           % value,
           'writeValues': ['AMPS', 'VOLTS']
           })

Attribute('SourceCurrentLevel',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%e',
           'dim': [0],
           'readCmd': "print(smua.source.leveli)\n?",
           'writeCmd': lambda value: "smua.source.leveli=%s" % value,
           })

Attribute('SourceVoltageLevel',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%e',
           'dim': [0],
           'readCmd': "print(smua.source.levelv)\n?",
           'writeCmd': lambda value: "smua.source.levelv=%s" % value,
           })

Attribute('SourceVoltageLimit',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%e',
           'dim': [0],
           'readCmd': "print(smua.source.limitv)\n?",
           'writeCmd': lambda value: "smua.source.limitv=%s" % value,
           })

Attribute('SourceCurrentLimit',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%e',
           'dim': [0],
           'readCmd': "print(smua.source.limiti)\n?",
           'writeCmd': lambda value: "smua.source.limiti=%s" % value,
           })

Attribute('SourceCurrentRange',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%e',
           'dim': [0],
           'readCmd': "print(smua.source.rangei)\n?",
           'writeCmd': lambda value: "smua.source.rangei=%s" % value,
           })

Attribute('SourceVoltageRange',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%e',
           'dim': [0],
           'readCmd': "print(smua.source.rangev)\n?",
           'writeCmd': lambda value: "smua.source.rangev=%s" % value,
           })

Attribute('SourceLimitReached',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "print(smua.source.compliance)\n?",
           'readFormula': '{"false": False, "true": True}[str(VALUE).strip()]'
           })

# Measure ---
Attribute('MeasureCurrentAutoRange',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "print(smua.measure.autorangei)\n?",
           'readFormula': "bool(float(VALUE))",
           'writeCmd': lambda value:
           "smua.measure.autorangei=smua.AUTORANGE_%s"
           % ("ON" if value else "OFF"),
           })

Attribute('MeasureVoltageAutoRange',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "print(smua.measure.autorangev)\n?",
           'readFormula': "bool(float(VALUE))",
           'writeCmd': lambda value:
           "smua.measure.autorangev=smua.AUTORANGE_%s"
           % ("ON" if value else "OFF"),
           })

Attribute('MeasureFunction',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "print(smua.measure.func)\n?",
           'readFormula': "{0: 'AMPS', 1: 'VOLTS', 2: 'OHMS', 3: 'WATTS'}"
           "[int(float(VALUE))]",
           'writeCmd': lambda value: "smua.measure.func=smua.OUTPUT_%s"
           % ("DC%s" % value if value in ['AMPS', 'VOLTS'] else value),
           'writeValues': ['AMPS', 'VOLTS', 'OHMS', 'WATTS']
           })

Attribute('MeasureCurrentRange',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%e',
           'dim': [0],
           'readCmd': "print(smua.measure.rangei)\n?",
           'writeCmd': lambda value: "smua.measure.rangei=%s" % value,
           })

Attribute('MeasureVoltageRange',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%e',
           'dim': [0],
           'readCmd': "print(smua.measure.rangev)\n?",
           'writeCmd': lambda value: "smua.measure.rangev=%s" % value,
           })

Attribute('MeasureCurrent',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "print(smua.measure.i())\n?",
           'readFormula': "float(VALUE)",
           })

Attribute('MeasureVoltage',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "print(smua.measure.v())\n?",
           'readFormula': "float(VALUE)",
           })

Attribute('MeasureResistance',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "print(smua.measure.r())\n?",
           'readFormula': "float(VALUE)",
           })

Attribute('MeasurePower',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "print(smua.measure.p())\n?",
           'readFormula': "float(VALUE)",
           })

Attribute('MeasureCurrentLevel',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%e',
           'dim': [0],
           'readCmd': "print(smua.measure.leveli)\n?",
           'readFormula': 'float(VALUE.replace("nil","nan"))',
           'writeCmd': lambda value: "smua.measure.leveli=%s" % value,
           })

Attribute('MeasureVoltageLevel',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%e',
           'dim': [0],
           'readCmd': "print(smua.measure.levelv)\n?",
           'readFormula': 'float(VALUE.replace("nil","nan"))',
           'writeCmd': lambda value: "smua.measure.levelv=%s" % value,
           })

Attribute('MeasureAutoZero',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "print(smua.measure.autozero)\n?",
           'readFormula': "{0: 'OFF', 1: 'ONCE', 2: 'AUTO'}"
           "[int(float(VALUE))]",
           'writeCmd': lambda value: "smua.measure.autozero=smua.AUTOZERO_%s"
           % value,
           'writeValues': ['OFF', 'ONCE', 'AUTO']
           })

# Others ---
Attribute('LineFrequency',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%e',
           'dim': [0],
           'readCmd': "print(localnode.linefreq)\n?",
           'writeCmd': lambda value: "localnode.linefreq=%s" % value,
           })
