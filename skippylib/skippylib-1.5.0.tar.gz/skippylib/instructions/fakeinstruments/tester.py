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
__copyright__ = "Copyright 2017, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Development"


Attribute("boolean_scalar_ro",
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': 'source:readable:boolean:value?'
           })

Attribute("boolean_scalar_rw",
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "source:writable:boolean:value?",
           'writeCmd': lambda value: "source:writable:boolean:"
                                     "value {0}".format(value)
           })

Attribute("short_scalar_ro",
          {'type': PyTango.CmdArgType.DevShort,
           'dim': [0],
           'readCmd': "source:readable:short:value?"
           })

Attribute("short_scalar_rw",
          {'type': PyTango.CmdArgType.DevShort,
           'dim': [0],
           'readCmd': "source:writable:short:value?",
           'writeCmd': lambda value: "source:writable:short:"
                                     "value {0}".format(value)
           })

Attribute("float_scalar_ro",
          {'type': PyTango.CmdArgType.DevFloat,
           'dim': [0],
           'readCmd': "source:readable:float:value?"
           })

Attribute("float_scalar_rw",
          {'type': PyTango.CmdArgType.DevFloat,
           'dim': [0],
           'readCmd': "source:writable:float:value?",
           'writeCmd': lambda value: "source:writable:float:"
                                     "value {0}".format(value)
           })

# Test rampeable attributes ---
Attribute('Rampeable',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "rampeable?",
           'writeCmd': lambda value: "rampeable {0}".format(str(value)),
           'rampeable': True,
           'memorized': True,
           })

Attribute("Fallible",
          {'type': PyTango.CmdArgType.DevShort,
           'dim': [0],
           'readCmd': "fallible?"})

# FIXME: generalise this attrName and specify in the spectrum attr
Attribute('WaveformDataFormat',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "dataformat?",
           'writeCmd': lambda value: "dataformat {0}".format(str(value)),
           'writeValues': ['HALF', 'SINGLE', 'DOUBLE', 'QUADRUPLE'],
           })

Attribute('WaveformOrigin',
          {'type': PyTango.CmdArgType.DevFloat,
           'dim': [0],
           'readCmd': "dataorigin?",
           'writeCmd': lambda value: "dataorigin {0}".format(str(value)),
           })

Attribute('WaveformIncrement',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "dataincrement?",
           'writeCmd': lambda value: "dataincrement {0}".format(str(value)),
           })

Attribute('boolean_spectrum_ro',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [1, 40000000],
           'readCmd': "source:readable:array:boolean:value?",
           })

Attribute('short_spectrum_ro',
          {'type': PyTango.CmdArgType.DevShort,
           'format': '%9.6f',
           'dim': [1, 40000000],
           'readCmd': "source:readable:array:short:value?",
           })

Attribute('float_spectrum_ro',
          {'type': PyTango.CmdArgType.DevFloat,
           'format': '%9.6f',
           'dim': [1, 40000000],
           'readCmd': "source:readable:array:float:value?",
           })

Attribute('Waveform',
          {'type': PyTango.CmdArgType.DevFloat,
           'format': '%9.6f',
           'dim': [1, 40000000],
           'readCmd': "source:switchable:array:float:value?",
           'switch': 'Waveform_switch',
           'dataFormat': 'WaveformDataFormat',
           'dataOrigin': 'WaveformOrigin',
           'dataIncrement': 'WaveformIncrement'
           })

Attribute('Waveform_switch',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "source:switchable:array:float:switch?",
           'writeCmd': lambda value: "source:switchable:array:float:"
                                     "switch {0}".format(
               "ON" if value else "OFF")
           })

Attribute('Waveform_samples',
          {'type': PyTango.CmdArgType.DevUShort,
           'dim': [0],
           'readCmd': "source:switchable:array:float:samples?",
           'writeCmd': lambda value: "source:switchable:array:"
                                     "float:samples {0}".format(value),
           })

Attribute('Waveform_periods',
          {'type': PyTango.CmdArgType.DevUShort,
           'dim': [0],
           'readCmd': "source:switchable:array:float:periods?",
           'writeCmd': lambda value: "source:switchable:array:"
                                     "float:periods {0}".format(value),
           })

Attribute('wfState',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': lambda ch, num: "source:readable:{0}{1:02d}:float:"
                                      "switch?".format(ch, num),
           'writeCmd': lambda ch, num: (
               lambda value: "source:readable:{0}{1:02d}:float:"
                             "switch {2}".format(ch, num,
                                                  'ON' if value else 'OFF')),
           'channels': True,
           'functions': True,
           })

Attribute('wfChannels',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [1, 40000000],
           'readCmd': lambda ch, num: "source:readable:{0}{1:02d}:float:"
                                      "value?".format(ch, num),
           'channels': True,
           'functions': True,
           'switch': 'wfState'
           })

# Attribute('wfMultiple',
#           {'type': PyTango.CmdArgType.DevDouble,
#            'dim': [1, 40000000],
#            'readCmd': lambda ch, num: "source:{0}{1:02d}:array:"
#                                       "float?".format(ch, num),
#            'multiple': {'scpiPrefix': 'multiple', 'attrSuffix': 'Multi'}
#            })
