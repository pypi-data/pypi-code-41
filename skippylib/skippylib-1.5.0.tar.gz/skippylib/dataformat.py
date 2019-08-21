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
__copyright__ = "Copyright 2019, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Production"

def interpret_binary_format(data_format):
    data_format = data_format.lower()

    # 'BYTE':              1 byte,    8 bits
    # 'HALF'|'WORD':       2 byte,   16 bits
    # 'SINGLE'|'real,32':  4 bytes,  32 bits
    # 'DOUBLE':            8 bytes,  64 bits
    # 'QUADRUPLE':        16 bytes, 128 bits
    # 'ASCII':               coma separated strings
    if data_format in ['byt', 'byte']:
        format, divisor = 'b', 1
    elif data_format in ['hal', 'half', 'wor', 'word']:
        format, divisor = 'h', 2
    elif data_format in ['sin', 'sing', 'singl', 'single', 'real,32']:
        format, divisor = 'I', 4
    elif data_format in ['dou', 'doub', 'doubl', 'double']:
        format, divisor = 'q', 8
    elif data_format in ['qua', 'quad', 'quadr', 'quadru', 'quadrup',
                         'quadrupl', 'quadruple']:
        format, divisor = None, 16
    else:
        raise AssertionError(
            "Cannot decodify data received with format {0!r}".format(
                data_format))
    return format, divisor