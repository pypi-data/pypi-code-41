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
__copyright__ = "Copyright 2015, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Production"


Attribute('Frequency',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': ":FREQ?",
           'writeCmd': lambda value: ":FREQ %s" % (str(value)),
           'rampeable': True,
           'memorized': True,
           })

Attribute('PowerLevel',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': ":POW?",
           'writeCmd': lambda value: ":POW %s" % (str(value)),
           'memorized': True,
           })

Attribute('RfState',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': ":OUTP:STAT?",
           'writeCmd': lambda value: ":OUTP:STAT %s" % (value),
           })

Attribute('FrequencyRangeLow',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': ":FREQ:PHAS:CONT:LOW?",
           # 'writeCmd': lambda value: ":FREQ:PHAS:CONT:LOW %s" % (str(value)),
           })

Attribute('FrequencyRangeHigh',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': ":FREQ:PHAS:CONT:HIGH?",
           # 'writeCmd': lambda value: ":FREQ:PHAS:CONT:HIGH %s"
           #                           % (str(value)),
           })

Attribute('PowerRangeLow',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': ":OUTP:AFIX:RANG:LOW?",
           # 'writeCmd': lambda value:":OUTP:AFIX:RANG:LOW %s" % (str(value)),
           })

Attribute('PowerRangeHigh',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': ":OUTP:AFIX:RANG:UPP?",
           # 'writeCmd': lambda value: ":OUTP:AFIX:RANG:UPP %s" % (str(value)),
           })

Attribute('Impedancy',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': ":OUTP:IMP?",
           })

Attribute('PhaseContinuousFrequencyActive',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': ":FREQ:PHAS:CONT:STAT?",
           })

Attribute('PhaseContinuousFrequencyNarrow',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': ":FREQ:PHAS:CONT:MODE?",
           })

Attribute('OscillatorSource',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': ":ROSCillator:SOURce?",
           # 'writeCmd': lambda value: ":ROSCillator:SOURce %s" % (str(value)),
           })

Attribute('OscillatorExternalLostRFoff',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': ":ROSCillator:EXTernal:RFOff?",
           # 'writeCmd': ":ROSCillator:EXTernal:RFOff %s" % (str(value))
           })
# FIXME: the reading of this attribute should only be allowed
#        when OscillatorSource is 'EXT' (external).

Attribute('OscillatorExternalFrequency',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': ":ROSCillator:EXTernal:Frequency?"
           })

# Attribute('Errors',
#           {'type': PyTango.CmdArgType.DevString,
#            'dim': [1,100],
#            'readCmd': ":SYST:SERROR?",
#            })
