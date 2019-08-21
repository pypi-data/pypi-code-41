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


####
# Example of attribute:
#
#   Attribute('name' -> name of the attribute
#             {'type' -> check the PyTango.CmdArgType
#              'dim'  -> can be: 0
#                               [1,X]
#                               [2,X,Y]
#              'channels' -> boolean to build attrs with a 'ch' suffix
#              'funtions' -> boolean to build attrs with a 'fn' suffix
#              'unit'     -> the unit of the tango attribute
#              'min','max'-> in writable attributes configure limits
#              'format'   -> in floats and integers the representation
#              'label'    -> attribute property
#              'description' -> attribute property
#              'memorized' -> attribute property
#              'writeValues' -> list of accepted values to write
#              'manager'  -> to flag if a channel is close to avoid reads there
#             }
#            )
#

Attribute('State',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': lambda ch, num: "{0}{1}:DISPlay?".format(ch, num),
           'writeCmd': lambda ch, num: (lambda value:
                                        "{0}{1}:DISPlay {2}".format(
                                         ch, num, 'ON' if value else 'OFF')),
           'channels': True,
           'functions': True,
           })

Attribute('Impedance',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: "{0}{1}:INPut?".format(ch, num),
           'channels': True,
           })

Attribute('Area',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: "MEAS:AREA? "
                                      "Display,{0}{1}".format(ch, num),
           'channels': True,
           'functions': True,
           'switch': 'State',
           })

Attribute('Amplitude',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: "MEAS:VAMP? {0}{1}".format(ch, num),
           'channels': True,
           'functions': True,
           'switch': 'State',
           })

Attribute('Scale',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: "{0}{1}:SCALe?".format(ch, num),
           'writeCmd': lambda ch, num: (lambda value:
                                        "{0}{1}:SCALe {2}".format(
                                         ch, num, value)),
           'channels': True,
           'switch': 'State',
           })

Attribute('Offset',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: "{0}{1}:OFFS?".format(ch, num),
           'writeCmd': lambda ch, num: (lambda value:
                                        "{0}{1}:OFFS {2}".format(
                                         ch, num, value)),
           'channels': True,
           'switch': 'State',
           })

Attribute('VPeakToPeak',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: "MEAS:VPP? {0}{1}".format(ch, num),
           'channels': True,
           'functions': True,
           'switch': 'State',
           })

Attribute('VoltageMin',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: "MEAS:VMIN? {0}{1}".format(ch, num),
           'channels': True,
           'functions': True,
           'switch': 'State',
           })

Attribute('VoltageMax',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: "MEAS:VMAX? {0}{1}".format(ch, num),
           'channels': True,
           'functions': True,
           'switch': 'State',
           })

Attribute('VoltageUpper',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: "MEAS:VUPPER? {0}{1}".format(ch, num),
           'channels': True,
           'switch': 'State',
           })

Attribute('VoltageLower',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: "MEAS:VLOWER? {0}{1}".format(ch, num),
           'channels': True,
           'switch': 'State',
           })

Attribute('Frequency',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: "MEAS:FREQ? {0}{1}".format(ch, num),
           'channels': True,
           'switch': 'State',
           })

Attribute('Period',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: "MEAS:PERIOD? {0}{1}".format(ch, num),
           'channels': True,
           'switch': 'State',
           })

Attribute('RiseTime',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: "MEAS:RISETIME? {0}{1}".format(ch, num),
           'channels': True,
           'switch': 'State',
           })

Attribute('FallTime',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: "MEAS:FALLTIME? {0}{1}".format(ch, num),
           'channels': True,
           'switch': 'State',
           })

Attribute('OverShoot',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: "MEAS:OVERSHOOT? {0}{1}".format(ch, num),
           'channels': True,
           'switch': 'State',
           })

Attribute('PreShoot',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: "MEAS:PRESHOOT? {0}{1}".format(ch, num),
           'channels': True,
           'switch': 'State',
           })

Attribute('Waveform',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [1, 40000000],
           'readCmd': lambda ch, num: "WAVeform:SOURce {0}{1};"
                                      ":WAVeform:DATA?".format(ch, num),
           'channels': True,
           'functions': True,
           'switch': 'State',
           })

Attribute('CurrentSampleRate',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [0],
           'readCmd': "ACQuire:SRATe?",
           })

Attribute('ScaleH',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [0],
           'readCmd': "TIMebase:SCALe?",
           'writeCmd': lambda value: "TIMebase:SCALe {0!s}".format(value),
           })

Attribute('OffsetH',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [0],
           'readCmd': "TIMebase:POS?",
           'writeCmd': lambda value: "TIMebase:POS {0!s}".format(value),
           })

Attribute('TriggerType',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "TRIGger:MODE?",
           'writeCmd': lambda value: "TRIGger:MODE {0!s}".format(value),
           })

Attribute('AcquisitionMode',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQuire:MODE?",
           'writeCmd': lambda value: "ACQuire:MODE {0!s}".format(value),
           })

Attribute('AcquisitonPoints',
          {'type': PyTango.CmdArgType.DevLong,
           'dim': [0],
           'readCmd': "ACQuire:POINts?",
           'writeCmd': lambda value: "ACQuire:POINts {0!s}".format(value),
           })

Attribute('WaveformDataFormat',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': ":waveform:format?",
           'writeCmd': lambda value: "waveform:format {0!s}".format(value),
           'writeValues': ['BYTE', 'BYT',
                           'WORD', 'WOR',
                           'ASCII', 'ASCI', 'ASC'],
           })

Attribute('WaveformOrigin',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [0],
           'readCmd': "WAVeform:YORigin?",
           })

Attribute('WaveformIncrement',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%%9.6f',
           'dim': [0],
           'readCmd': "WAVeform:YINCrement?",
           })

Attribute('ByteOrder',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "WAVeform:BYTeorder?",
           'writeCmd': lambda value: "WAVeform:BYTeorder {0!s}".format(value),
           'writeValues': ['LSBF', 'MSBF'],
           'memorized': True,
           })

Attribute('Error',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "SYSTem:ERRor?",
           })

Attribute('Lock',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "SYSTem:LOCK?",
           'writeCmd': lambda value: "SYSTem:LOCK {0!s}".format(value),
           'memorized': True,
           })
