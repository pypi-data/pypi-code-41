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
__status__ = "Production"


####
# Example of attribute:
#
#   Attribute('name' -> name of the attribute
#             {'type' -> check the PyTango.CmdArgType
#              'dim'  -> can be: 0
#                               [1,X]
#                               [2,X,Y]
#              'channels'    -> boolean to build attrs with a 'ch' suffix
#              'functions'   -> boolean to build attrs with a 'fn' suffix
#              'unit'        -> the unit of the tango attribute
#              'min','max'   -> in writable attributes configure limits
#              'format'      -> in floats and integers the representation
#              'label'       -> attribute property
#              'description' -> attribute property
#              'memorised'   -> attribute property
#              'writeValues' -> list of accepted values to write
#              'manager'     -> to flag if a channel is close to avoid reads
#                               there
#              })
#

Attribute('Attenuation',
          {'type': PyTango.CmdArgType.DevUShort,
           'dim': [0],
           'readCmd': ":input:attenuation?",
           'writeCmd': lambda value: ":input:attenuation %s" % value,
           'unit': 'dB', 'min': 0, 'max': 75
           })

Attribute('ContinuousAcquisition',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': ":INIT:CONT?",
           'writeCmd': lambda value: ":INIT:CONT %s"
                                     % ("1" if bool(value) else "0")
           })

Attribute('FrequencyCenter',
          {'label': 'Frequency Center',
           'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': ":FREQ:CENTER?",
           'writeCmd': lambda value: ":FREQ:CENTER %s" % value,
           'unit': 'Hz'
           })

Attribute('FrequencySpan',
          {'label': 'Frequency Span',
           'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': ":FREQ:SPAN?",
           'writeCmd': lambda value: ":FREQ:SPAN %s" % value,
           'unit': 'Hz'
           })

Attribute('FrequencyStart',
          {'label': 'Frequency Start',
           'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': ":FREQ:START?",
           'writeCmd': lambda value: ":FREQ:START %s" % value,
           'unit': 'Hz'
           })

Attribute('FrequencyStop',
          {'label': 'Frequency Stop',
           'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': ":FREQ:STOP?",
           'writeCmd': lambda value: ":FREQ:STOP %s" % value,
           'unit': 'Hz'
           })

Attribute('Impedance',
          {'type': PyTango.CmdArgType.DevUShort,
           'dim': [0],
           'readCmd': ":input:impedance?",
           'writeCmd': lambda value: ":input:impedance %s" % value
           })  # 50 | 75

Attribute('MarkerState',
          {'type': PyTango.CmdArgType.DevBoolean,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: ":CALC1:MARK%s?"
                                      % (num),
           'functions': True,
           })

Attribute('ResolutionBandWidth',  # RBW
          {'label': 'Resolution Bandwidth (RBW)',
           'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': ":BAND:RES?",
           'writeCmd': lambda value: ":BAND:RES %s" % value,
           'unit': 'Hz', 'min': 10, 'max': 10000000,  # between 10Hz to 10MHz
           })

Attribute('SystemErrors',
          {'label': 'System Errors',
           'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "SYSTEM:ERROR?"})

Attribute('SweepTime',  # SWT
          {'label': 'Sweep time (SWT)',
           'description': 'N_samples/RBW',
           'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': ":SWE:TIME?",
           'writeCmd': lambda value: ":SWE:TIME %s" % value,
           'unit': 's'
           })

Attribute('SweepPoints',
          {'label': 'Sweep Points',
           'description': 'Number of measurement points for one sweep run.\n'
           'valid values: 125, 251, 501, 1001, 2001, 4001, 8001',
           'type': PyTango.CmdArgType.DevUShort,
           'dim': [0],
           'readCmd': "SWE:POINts?",
           'writeCmd': lambda value: ":SWE:POINts %s" % value,
           'writeValues': ['125', '251', '501', '1001', '2001', '4001', '8001']
           })

Attribute('VideoBandWidth',  # VBW
          {'label': 'Video Bandwidth (VBW)',
           'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': ":BAND:VID?",
           'writeCmd': lambda value: ":BAND:VID %s" % value,
           'unit': 'Hz', 'min': 1, 'max': 10000000,  # between 1Hz to 10MHz
           })

Attribute('WaveformState',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': ":TRAC:IQ:STAT?",
           'writeCmd': lambda value: ":TRAC:IQ:STAT %s"
                                     % ("1" if bool(value) else "0")
           })

Attribute('Waveform',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [1, 10000],
           'readCmd': ":TRAC? TRACE1"
           })

Attribute('WaveformDataFormat',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': ":format?",
           'writeCmd': lambda value: ":format %s" % (str(value)),
           'writeValues': ['ASC,0', 'REAL,32'],
           })
