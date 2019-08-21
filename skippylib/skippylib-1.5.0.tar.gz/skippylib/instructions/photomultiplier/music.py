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

__author__ = "Sergi Blanch-Torne"
__maintainer__ = "Sergi Blanch-Torne"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2015, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Pre-Alpha"


import PyTango


# from skippylib import skippy
# skippyobj = skippy.Skippy(name='localhost',
#                           port=5025,
#                           nMultiple=['CHANnel:8'])

Attribute('MAC',
          {'description': 'MAC address',
           'type': PyTango.CmdArgType.DevUShort,
           'dim': [0],
           'readCmd': "*MAC?",
           })

Attribute('AcqMode',
          {'description': 'Acquisition Mode:\n'
                          '0: Analog\n'
                          '1: Digital\n',
           'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "CONFigure:ACQUisition:MODE?",
           'writeCmd':
               lambda value: "CONFigure:ACQUisition:MODE {v}".format(v=value),
           # TODO: improve this set of valid values
           })

Attribute('IntTime',
          {'description': 'Number of seconds to integrate counts',
           'type': PyTango.CmdArgType.DevULong,
           'dim': [0],
           'readCmd': "CONFigure:COUNt:INTTime?",
           'writeCmd':
               lambda value: "CONFigure:COUNt:INTTime {v}".format(v=value),
           })

Attribute('CountRate',
          {'description': 'Counts refreshment rate in seconds',
           'type': PyTango.CmdArgType.DevULong,
           'dim': [0],
           'readCmd': "CONFigure:COUNt:RATE?",
           'writeCmd':
               lambda value: "CONFigure:COUNt:RATE {v}".format(v=value),
           })

Attribute('Count',
          {'description': 'Actual count value for SiPM 0-7',
           'type': PyTango.CmdArgType.DevULong,
           'dim': [0],
           'readCmd':
               lambda mult, num: "ACQUire:COUNt:{m}{n:02d}:VALUe?"
                                 "".format(m=mult, n=num),
           'multiple': {'scpiPrefix': 'CHANnel', 'attrSuffix': '',
                        'startAt': 0}
           })

Attribute('CountInt',
          {'description': 'Integrated counts value for SiPM 1-8',
           'type': PyTango.CmdArgType.DevULong,
           'dim': [0],
           'readCmd':
               lambda mult, num: "ACQUire:COUNt:{m}{n:02d}:INTEgrated?"
                                 "".format(m=mult, n=num),
           'multiple': {'scpiPrefix': 'CHANnel', 'attrSuffix': '',
                        'startAt': 0}
           })

Attribute('Enable',
          {'description': 'Enable/Disable channel 0-7',
           'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd':
               lambda mult, num: "CONFigure:{m}{n:02d}:ENABLE?"
                                 "".format(m=mult, n=num),
           'writeCmd': lambda mult, num: (
               lambda value: "CONFigure:{m}{n:02d}:ENABLE {v}"
                             "".format(m=mult, n=num, v=value)),
           'multiple': {'scpiPrefix': 'CHANnel', 'attrSuffix': 'CH',
                        'startAt': 0}
           })

Attribute('Enable',
          {'description': 'Enable/Disable single ended input for channel 0-7',
           'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd':
               lambda mult, num: "CONFigure:{m}{n:02d}:SE?"
                                 "".format(m=mult, n=num),
           'writeCmd': lambda mult, num: (
               lambda value: "CONFigure:{m}{n:02d}:SE {v}"
                             "".format(m=mult, n=num, v=value)),
           'multiple': {'scpiPrefix': 'CHANnel', 'attrSuffix': 'SE',
                        'startAt': 0}
           })

Attribute('Enable',
          {'description': 'Enable/Disable summation channel 0-7',
           'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd':
               lambda mult, num: "CONFigure:{m}{n:02d}:SUMMation?"
                                 "".format(m=mult, n=num),
           'writeCmd': lambda mult, num: (
               lambda value: "CONFigure:{m}{n:02d}:SUMMation {v}"
                             "".format(m=mult, n=num, v=value)),
           'multiple': {'scpiPrefix': 'CHANnel', 'attrSuffix': 'SUM',
                        'startAt': 0}
           })

Attribute('C_VThres',
          {'description': 'Voltage threshold. Possible values are [0-511]',
           'type': PyTango.CmdArgType.DevUShort,
           'dim': [0],
           'readCmd': lambda mult, num: "CONFigure:{m}{n:02d}:VTHReshold?"
                                        "".format(m=mult, n=num),
           'writeCmd': lambda mult, num: (
               lambda value: "CONFigure:{m}{n:02d}:VTHReshold {v}"
                             "".format(m=mult, n=num, v=value)),
           'multiple': {
               'scpiPrefix': 'CHANnel', 'attrSuffix': '',
               'startAt': 0}
           })

Attribute('C_Voff',
          {'description': 'Voltage offset. Possible values are [0-255]',
           'type': PyTango.CmdArgType.DevUShort,
           'dim': [0],
           'readCmd': lambda mult, num: "CONFigure:{m}{n:02d}:VOFFset?"
                                        "".format(m=mult, n=num),
           'writeCmd': lambda mult, num: (
               lambda value: "CONFigure:{m}{n:02d}:VOFFset {v}"
                             "".format(m=mult, n=num, v=value)),
           'multiple': {
               'scpiPrefix': 'CHANnel', 'attrSuffix': '',
               'startAt': 0}
           })

Attribute('C_VBG',
          {'description': 'Coarse voltage reference. Possible values are [0-7]',
           'type': PyTango.CmdArgType.DevUShort,
           'dim': [0],
           'readCmd': "CONFigure:VBG?",
           'writeCmd': lambda value: "CONFigure:VBG {v}".format(v=value)
           })

Attribute('PoleZeroEnable',
          {'description': 'Enable Pole Zero cancellation',
           'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "CONFigure:POLEzero:ENABle?",
           'writeCmd': lambda value: "CONFigure:POLEzero:ENABle {v:d}"
                                     "".format(v=value)
           })

Attribute('PoleZeroR',
          {'description': 'Enable Pole Zero Resistance Ladder. '
                          'Possible values are [0-7]',
           'type': PyTango.CmdArgType.DevUShort,
           'dim': [0],
           'readCmd': "CONFigure:POLEzero:RESIstance?",
           'writeCmd': lambda value: "CONFigure:POLEzero:RESIstance {v}"
                                     "".format(v=value)
           })

Attribute('PoleZeroC',
          {'description': 'Enable Pole Zero Capacitance Ladder. '
                          'Possible values are [0-31]',
           'type': PyTango.CmdArgType.DevUShort,
           'dim': [0],
           'readCmd': "CONFigure:POLEzero:CAPAcitance?",
           'writeCmd': lambda value: "CONFigure:POLEzero:CAPAcitance {v}"
                                     "".format(v=value)
           })

Attribute('PoleZeroAtt',
          {'description': 'Enable Pole Zero Low Atten Ladder',
           'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "CONFigure:POLEzero:ATTEn?",
           'writeCmd': lambda value: "CONFigure:POLEzero:ATTEn {v:d}"
                                     "".format(v=value)
           })

Attribute('C_HighGain',
          {'description': 'Enable high gain transimpedance mode',
           'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "CONFigure:HIGHgain:ENABle?",
           'writeCmd': lambda value: "CONFigure:HIGHgain:ENABle {v:d}"
                                     "".format(v=value)
           })

# Attribute('TS_ThresholdsBest',
#           {'description': 'File tune of threshold per channel',
#            'type': PyTango.CmdArgType.DevLong,
#            'dim': [1, 8],
#            'readCmd': "ACQUire:THREshold:BEST?"
#            })
# FIXME: music returns a string evaluable as an array, but incorrectly
# it doesn't sends a #NMMMMxxx.. array as scpi expect

Attribute('TS_VBGBest',
          {'description': 'Global coarse tune of threshold',
           'type': PyTango.CmdArgType.DevLong,
           'dim': [0],
           'readCmd': "ACQUire:THREshold:VBG?"
           })

Attribute('TS_DutyWindow',
          {'description': 'Threshold Scan DutyWindow for actual count',
           'type': PyTango.CmdArgType.DevLong,
           'dim': [0],
           'readCmd': "CONFigure:THREshold:WINDow?",
           'writeCmd': lambda value: "CONFigure:THREshold:WINDow {v}"
                                     "".format(v=value)
           })

Attribute('TOFtime',
          {'description': 'Acquisition time in miliseconds',
           'type': PyTango.CmdArgType.DevULong,
           'dim': [0],
           'readCmd': "CONFigure:TOF:TIME?",
           'writeCmd': lambda value: "CONFigure:TOF:TIME {v}".format(v=value)
           })

Attribute('TOFinjection',
          {'description': 'Useinjection pulse in U16 SMA',
           'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "CONFigure:TOF:INJEction?",
           'writeCmd': lambda value: "CONFigure:TOF:INJEction {v}"
                                     "".format(v=value)
           })

# Attribute('TOFudpHost',
#           {'description': 'IP to which send udp packets',
#            'type': PyTango.CmdArgType.DevString,
#            'dim': [0],
#            'readCmd': "CONFigure:TOF:UDP:HOST?",
#            'writeCmd': lambda value: "CONFigure:TOF:UDP:HOST {v}"
#                                      "".format(v=value)
#            })
#
# Attribute('TOFudpPort',
#           {'description': 'Port to which send udp packets',
#            'type': PyTango.CmdArgType.DevUShort,
#            'dim': [0],
#            'readCmd': "CONFigure:TOF:UDP:PORT?",
#            'writeCmd': lambda value: "CONFigure:TOF:UDP:PORT {v}"
#                                      "".format(v=value)
#            })

Attribute('HVenable',
          {'description': 'High voltage font enabled',
           'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "CONFigure:HV:ENABle?",
           'writeCmd': lambda value: "CONFigure:HV:ENABle {v}".format(v=value),
           'delayAfterWrite': 0.2,
           })

Attribute('HVvoltage',
          {'description': 'Voltage level [40-90]V',
           'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "CONFigure:HV:VOLTage?",
           'writeCmd': lambda value: "CONFigure:HV:VOLTage {v}".format(v=value)
           })

Attribute('HVvoltageOutput',
          {'description': 'Output voltage',
           'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "DIAGnostic:HV:VOLTage?"
           })

Attribute('HVcurrentOutput',
          {'description': 'Output current in mA',
           'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "DIAGnostic:HV:CURRent?"
           })

Attribute('HVoverCurrent',
          {'description': 'Current output beyond safe levels',
           'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "DIAGnostic:HV:OVERcurrent?"
           })

# Attribute('temperature',
#           {'description': 'Rpi temperature',
#            'type': PyTango.CmdArgType.DevDouble,
#            'dim': [0],
#            'readCmd': "DIAGnostic:TEMPerature?"
#            })
