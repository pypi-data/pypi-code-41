from __future__ import absolute_import, division, print_function, unicode_literals

from ctypes import c_ubyte, c_uint64

BYTE = c_ubyte # wintypes.BYTE is c_byte
ULONGLONG = c_uint64 # wintypes.ULONGLONG doesn't exist
