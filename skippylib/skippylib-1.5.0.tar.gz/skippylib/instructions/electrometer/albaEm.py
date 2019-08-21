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

__author__ = "Manuel Broseta Sebastia"
__maintainer__ = "Antonio Milan Otero"
__email__ = "mbroseta@cells.es"
__copyright__ = "Copyright 2017, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Production"


Attribute('Mac',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "*MAC?",
           })

# IO Port functions ---
Attribute('IOCONFIG',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd':
               lambda mult, num: "{0}{1:02d}:CONFI?".format(mult, num),
           'writeCmd':
               lambda mult, num: (
                   lambda value: "{0}{1:02d}:CONFI {2}".format(mult, num, value)),
           'multiple': {'scpiPrefix': 'IOPOrt', 'attrSuffix': 'Port'}
           })

Attribute('IO',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd':
               lambda mult, num: "{0}{1:02d}:VALU?".format(mult, num),
           'writeCmd':
               lambda mult, num: (
                   lambda value: "{0}{1:02d}:VALU {2}".format(mult, num, value)),
           'multiple': {'scpiPrefix': 'IOPOrt', 'attrSuffix': 'Port'}
           })

# Trigger Commands ---
Attribute('TriggerDelay',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "TRIG:DELA?",
           'writeCmd': lambda value: "TRIG:DELA {0}".format(value),
           })

Attribute('TriggerInput',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "TRIG:INPU?",
           'writeCmd': lambda value: "TRIG:INPU {0}".format(value),
           })

Attribute('TriggerMode',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "TRIG:MODE?",
           'writeCmd': lambda value: "TRIG:MODE {0}".format(value),
           })

Attribute('TriggerPolarity',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "TRIG:POLA?",
           'writeCmd': lambda value: "TRIG:POLA {0}".format(value),
           })

Attribute('SWTrigger',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "TRIG:SWSET?",
           'writeCmd': lambda value: "TRIG:SWSET {0}".format(value),
           })

# Acquisition Commands ---
Attribute('AcqFilter',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:FILTER?",
           'writeCmd': lambda value: "ACQU:FILTER {0}".format(value),
           })

Attribute('Meas',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:MEAS?",
           })

Attribute('NData',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:NData?",
           })

Attribute('AcqRange',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:RANGE?",
           'writeCmd': lambda value: "ACQU:RANGE {0}".format(value),
           })

Attribute('AcqAutoRange',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:ARNG?",
           'writeCmd': lambda value: "ACQU:ARNG {0}".format(value),
           })

Attribute('AcqStart',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:START?",
           'writeCmd': lambda value: "ACQU:START {0}".format(value),
           })

Attribute('AcqState',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:STATE?",
           })

Attribute('AcqStop',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:STOP?",
           'writeCmd': lambda value: "ACQU:STOP {0}".format(value),
           })

Attribute('AcqTime',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:TIME?",
           'writeCmd': lambda value: "ACQU:TIME {0}".format(value),
           })

Attribute('NTrig',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:NTRIggers?",
           'writeCmd': lambda value: "ACQU:NTRIggers {0}".format(value),
           })

Attribute('EmStatus',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:STUS?",
           })

Attribute('AcqMode',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:MODE?",
           'writeCmd': lambda value: "ACQU:MODE {0}".format(value),
           })

# Channels ---
Attribute('I',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: "{0}{1:02d}:INSCurrent?".format(ch, num),
           'channels': True,
           'multiple': {'scpiPrefix': 'CHAN', 'attrSuffix': ''}
           })

Attribute('Current',
          {'type': PyTango.CmdArgType.DevString,
           # FIXME: DevString? should it be an array of doubles?
           'dim': [0],
           'readCmd': lambda ch, num: "{0}{1:02d}:CURRent?".format(ch, num),
           'channels': True
           })

Attribute('AverageCurrent',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: "{0}{1:02d}:AVGCurrent?".format(ch, num),
           'channels': True
           })

Attribute('Range_',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: "{0}{1:02d}:CABO:RANGE?".format(ch, num),
           'writeCmd': lambda ch, num: (
               lambda value: "{0}{1:02d}:CABO:RANGE {2}".format(ch, num, value)),
           'channels': True
           })

Attribute('Filter_',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: "{0}{1:02d}:CABO:FILT?".format(ch, num),
           'writeCmd': lambda ch, num: (
               lambda value: "{0}{1:02d}:CABO:FILT {2}".format(ch, num, value)),
           'channels': True
           })

Attribute('AutoRangeMin_',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: "{0}{1:02d}:CABO:SMIN?".format(ch, num),
           'writeCmd': lambda ch, num: (
               lambda value: "{0}{1:02d}:CABO:SMIN {2}".format(ch, num, value)),
           'channels': True
           })

Attribute('AutoRangeMax_',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: "{0}{1:02d}:CABO:SMAX?".format(ch, num),
           'writeCmd': lambda ch, num: (
               lambda value: "{0}{1:02d}:CABO:SMAX {2}".format(ch, num, value)),
           'channels': True
           })

Attribute('AutoRange_',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: "{0}{1:02d}:CABO:ARNG?".format(ch, num),
           'writeCmd': lambda ch, num: (
               lambda value: "{0}{1:02d}:CABO:ARNG {2}".format(ch, num, value)),
           'channels': True
           })

Attribute('Saturation_',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: "{0}{1:02d}:CABO:SATU?".format(ch, num),
           'channels': True
           })

Attribute('TiGain_',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: "{0}{1:02d}:CABO:TIGA?".format(ch, num),
           'writeCmd': lambda ch, num: (
               lambda value: "{0}{1:02d}:CABO:TIGA {2}".format(ch, num, value)),
           'channels': True
           })

Attribute('VGgain_',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: "{0}{1:02d}:CABO:VGAIn?".format(ch, num),
           'writeCmd': lambda ch, num: (
               lambda value: "{0}{1:02d}:CABO:VGAIn {2}".format(ch, num, value)),
           'channels': True
           })

Attribute('Offset_Percentage_',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: "{0}{1:02d}:CABO:OFFS?".format(ch, num),
           'writeCmd': lambda ch, num: (
               lambda value: "{0}{1:02d}:CABO:OFFS {2}".format(ch, num, value)),
           'channels': True
           })

Attribute('Offset_',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: "{0}{1:02d}:CABO:OFFS?".format(ch, num),
           'writeCmd': lambda ch, num: (
               lambda value: "{0}{1:02d}:CABO:OFFS {2}".format(ch, num, value)),
           'channels': True
           })

Attribute('Inversion_',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: "{0}{1:02d}:CABO:INVE?".format(ch, num),
           'writeCmd': lambda ch, num: (
               lambda value: "{0}{1:02d}:CABO:INVE {2}".format(ch, num, value)),
           'channels': True
           })
