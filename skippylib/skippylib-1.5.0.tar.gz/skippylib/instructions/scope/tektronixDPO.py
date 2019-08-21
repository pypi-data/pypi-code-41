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


Attribute('State',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': lambda ch, num: ":SELect:%s%d?" % (ch, num),
           'writeCmd': lambda ch, num: (lambda value: ":SELect:%s%d %s"
                                        % (ch, num, value)),
           'channels': True,
           })

Attribute('Impedance',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: ":%s%d:TERmination" % (ch, num),
           'channels': True,
           })

Attribute('Amplitude',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: ":MEASUrement:IMMed:TYPe AMPlitude;"
                                      ":MEASUrement:IMMed:SOURCE %s%d;"
                                      ":MEASUrement:IMMed:VALue?" % (ch, num),
           'channels': True,
           })

# Attribute('Scale',
#           {'type': PyTango.CmdArgType.DevDouble,
#            'dim': [0],
#            'channels': True,
#            })

Attribute('Offset',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: ":%s%d:OFFSet?" % (ch, num),
           'writeCmd': lambda ch, num: (lambda value: ":%s%d:OFFSet %s"
                                        % (ch, num, value)),
           'channels': True,
           })

Attribute('CurrentSampleRate',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': ":HORizontal:MAIn:SAMPLERate?",
           })

Attribute('ScaleH',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': ":HORizontal:SCAle?",
           'writeCmd': lambda value: ":HORizontal:SCAle %s" % (str(value)),
           })

# Attribute('OffsetH',
#           {'type': PyTango.CmdArgType.DevDouble,
#            'dim': [0],
#            })
