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
__status__ = "Production"


Attribute('Amplitude',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: ":SOURce%d:VOLTage:AMPLitude?" % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":SOURce%d:VOLTage:AMPLitude %s"
                                        % (ch, value)),
           'channels': True,
           })

Attribute('Frequency',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: ":SOURce%d:FREQuency?" % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":SOURce%d:FREQuency %s"
                                        % (ch, value)),
           'channels': True,
           })

functionShapes = ['SINusoid', 'SQUare', 'PULSe', 'RAMP', 'PRNoise']

Attribute('Function',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: ":SOURce%d:FUNCtion:SHAPe?" % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":SOURce%d:FUNCtion:SHAPe %s"
                                        % (num, value)),
           'writeValues': functionShapes,
           'channels': True
           })

Attribute('FunctionShapes',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [1, 20],
           'readCmd': lambda ch, num: functionShapes,
           })

Attribute('High',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: ":SOURce%d:VOLTage:HIGH?" % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":SOURce%d:VOLTage:HIGH %s"
                                        % (ch, value)),
           'channels': True,
           })

Attribute('Low',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: ":SOURce%d:VOLTage:LOW?" % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":SOURce%d:VOLTage:LOW %s"
                                        % (ch, value)),
           'channels': True,
           })

Attribute('ModulatedDepth',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: ":SOURce%d:am:DEPTh?" % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":SOURce%d:am:DEPTh %s"
                                        % (ch, value)),
           'channels': True,
           })
# FIXME: only valid in ["am"] mode

# Attribute('ModulatedDeviation',
#           {'type': PyTango.CmdArgType.DevDouble,
#            'dim': [0],
#            'readCmd': lambda ch, num: ":SOURce%d:%s:DEViation?" % (num),
#            'writeCmd': lambda ch, num: (lambda value:
#                                         ":SOURce%d:%s:DEViation %s"
#                                         % (ch,value)),
#            'channels': True,
#           })
# FIXME: only valid in ["fm","pm"] modes

# Attribute('ModulatedFrequency',
#           {'type': PyTango.CmdArgType.DevDouble,
#            'dim': [0],
#            'readCmd': lambda ch, num: ":SOURce%d:%s:INTernal:FREQuency?"
#                                       % (num),
#            'writeCmd': lambda ch, num: (lambda value:
#                                         ":SOURce%d:%s:INTernal:FREQuency %s"
#                                         % (ch, value)),
#            'channels': True,
#            })
# FIXME: for ["am","fm","pm"] modes,
#        but for ["fsk"] "INTernal" should have removed

Attribute('ModulatedRate',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: ":SOURce%d:fsk:INTernal:RATE?" % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":SOURce%d:fsk:INTernal:RATE %s"
                                        % (ch, value)),
           'channels': True,
           })
# FIXME: only valid in ["fsk"] mode

# Attribute('ModulatedShape',
#           {'type': PyTango.CmdArgType.DevString,
#            'dim': [0],
#            'readCmd': lambda ch, num: ":SOURce%d:%s:INTernal:FUNCtion?"
#                                       % (num),
#            'writeCmd': lambda ch, num: (lambda value:
#                                         ":SOURce%d:%s:INTernal:FUNCtion %s"
#                                         % (num, value)),
#            'channels': True,
#            'writeValues': functionShapes,
#            })
# FIXME: readCmd depends on the mode ["am", "fm", "pm", "fsk"]

Attribute('Offset',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: ":SOURce%d:VOLTage:OFFSet?" % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":SOURce%d:VOLTage:OFFSet %s"
                                        % (ch, value)),
           'channels': True,
           })

Attribute('Phase',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: ":SOURce%d:PHASe?" % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":SOURce%d:PHASe %s"
                                        % (ch, value)),
           'channels': True,
           })

Attribute('PulseLead',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: ":SOURce%d:PULSe:TRANsition:LEADing?"
                                      % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":SOURce%d:PULSe:TRANsition:LEADing %s"
                                        % (ch, value)),
           'channels': True,
           })

Attribute('PulseWidth',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: ":SOURce%d:PULSe:WIDTh?" % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":SOURce%d:PULSe:WIDTh %s"
                                        % (ch, value)),
           'channels': True,
           })

Attribute('RampSymmetry',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: ":SOURce%d:FUNCtion:RAMP:SYMMetry?"
                                      % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":SOURce%d:FUNCtion:RAMP:SYMMetry %s"
                                        % (ch, value)),
           'channels': True,
           })

# Attribute('RunMode',
#           {'type': PyTango.CmdArgType.DeString,
#            'dim': [0],
#            #'readCmd': lambda ch, num: "" % (num),
#            #'writeCmd': lambda ch, num: (lambda value:
#            #                             ""
#            #                             % (ch, value)),
#            'channels': True,
#            })
# TODO: PyVisaInstrWrapper asks 5 questions and combines them to get one answer
#     def runMode_read(self,ch):
#         """ This block is really different than the rest. The continuous
#            runMode is when all the other possibles are not activated.
#         """
#         query = StringIO()
#         #The order has to be this, the same from the ds dict
#         query.write(self.runMode_modulation_am_get(ch))
#         query.write(";"+self.runMode_modulation_fm_get(ch))
#         query.write(";"+self.runMode_modulation_fsk_get(ch))
#         query.write(";"+self.runMode_modulation_pm_get(ch))
#         query.write(";"+self.runMode_sweep_get(ch))
#         return query.getvalue()
#
#     def runMode_write(self,ch,value):
#         bar = ""
#         print "runMode_write(%d,%d)"%(ch,value)
#         if value in [0,1,2,4,8]:
#             bar = ":source%d:frequency:mode CW;"%(ch)
#             bar += {
#                0:self.runMode_continuous_set,
#                1:self.runMode_modulation_am_set,
#                2:self.runMode_modulation_fm_set,
#                4:self.runMode_modulation_fsk_set,
#                8:self.runMode_modulation_pm_set,
#                #16:self.runMode_sweep_set,
#               }[value](ch,"1")
#         elif value in [16]:
#             bar = self.runMode_sweep_set(ch,"1")
#         return bar

# Attribute('RunModes',
#           {'type': PyTango.CmdArgType.DevString,
#            'dim': [1, 20],
#            #'readCmd': lambda ch, num: "" % (num),
#            #'writeCmd': lambda ch, num: (lambda value:
#            #                             ""
#            #                             % (ch,value)),
#           })


Attribute('State',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': lambda ch, num: ":OUTPut%d:STATE?" % (num),
           'writeCmd': lambda ch, num: (lambda value: ":OUTPut%d:STATE %s"
                                        % (num, value)),
           'channels': True
           })

Attribute('SweepFreqCenter',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: ":source%d:frequency:center?" % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":source%d:frequency:center %s"
                                        % (ch, value)),
           'channels': True,
           })

Attribute('SweepFreqSpan',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: ":source%d:frequency:span?" % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":source%d:frequency:span %s"
                                        % (ch, value)),
           'channels': True,
           })

Attribute('SweepFreqStart',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: ":source%d:frequency:start?" % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":source%d:frequency:start %s"
                                        % (ch, value)),
           'channels': True,
           })

Attribute('SweepFreqStop',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: ":source%d:frequency:stop?" % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":source%d:frequency:stop %s"
                                        % (ch, value)),
           'channels': True,
           })

Attribute('SweepHoldTime',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: ":source%d:sweep:htime?" % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":source%d:sweep:htime %s"
                                        % (ch, value)),
           'channels': True,
           })

Attribute('SweepMode',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: ":source%d:sweep:mode?" % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":source%d:sweep:mode %s"
                                        % (ch, value)),
           'channels': True,
           'writeValues': ['auto', 'man']
           })

Attribute('SweepReturnTime',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: ":source%d:sweep:rtime?" % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":source%d:sweep:rtime %s"
                                        % (ch, value)),
           'channels': True,
           })

Attribute('SweepSpacing',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: ":source%d:sweep:spacing?" % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":source%d:sweep:spacing %s"
                                        % (ch, value)),
           'channels': True,
           })

Attribute('SweepTime',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: ":source%d:sweep:time?" % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":source%d:sweep:time %s"
                                        % (ch, value)),
           'channels': True,
           })

Attribute('lock',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': ":SYSTem:KLOCk:STATe?",
           'writeCmd': lambda value: ":SYSTem:KLOCk:STATe %s" % (value)
           })

Attribute('click',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': ":SYSTem:KCLick:STATe?",
           'writeCmd': lambda value: ":SYSTem:KCLick:STATe %s" % (value)
           })

Attribute('beep',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': ":SYSTem:BEEPer:STATe?",
           'writeCmd': lambda value: ":SYSTem:BEEPer:STATe %s" % (value)
           })
