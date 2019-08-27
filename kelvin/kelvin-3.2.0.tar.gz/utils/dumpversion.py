
# A troubleshooting command-line utility that prints a file's version resource to the screen.

import sys, struct
from ctypes import *

WORD  = c_short
DWORD = c_long

def dump_file(filename):
    GetFileVersionInfoSize=windll.version.GetFileVersionInfoSizeW
    _GetFileVersionInfo=windll.version.GetFileVersionInfoW
    def GetFileVersionInfo(filename):
        dwUnused = DWORD()
        cb = GetFileVersionInfoSize(filename, byref(dwUnused))
        if cb == 0:
            raise WinError()
        buf = create_string_buffer(cb)
        if not _GetFileVersionInfo(filename, 0, cb, buf):
            raise WinError()
        return buf

    filename = filename.encode('utf_16_le') + '\0\0'
    a = GetFileVersionInfo(filename)
    dump_node(a, 0) 


def wcslen(s, offset):
    index = 0
    while s[index + offset] != '\0' or s[index+1+offset] != '\0':
        index += 2
    return index / 2

def padlen(length):
    # Returns the amount of padding necessary to round this value up.
    r = length % 4
    if r:
        return 4 - r
    return 0

def dump_node(a, offset=0, indent=1, dump_children=True):
    original_offset = offset

    cbNode, cbData, wType = struct.unpack('HHH', a[offset:offset+6])
    offset += 6

    original_len = cbNode

    # For String nodes, the value length is in words, not bytes.
    if wType == 1:
        cbData *= 2

    namelen = wcslen(a, offset)
    ulen = namelen * 2
    name = fromucs2(a[offset:offset+ulen])
    offset += ulen + 2

    if cbData:
        offset += padlen(offset)
        value = a[offset:offset + cbData]
    else:
        value = None

    if indent:
        indentation = '| ' * indent
        header = indentation[:-2] + '+-'
    else:
        indentation = ''
        header = ''

    print '{}0x{:04x} ({}) {}'.format(header, original_offset, original_offset, name)
    print '{}cbNode: 0x{:04x} ({}) cbData: 0x{:04x} ({})'.format(indentation, cbNode, cbNode, cbData, cbData)

    if value is None:
        value = 'no value'
    elif wType == 1:
        value = 'value: 0x{:02x} {}'.format(offset, fromucs2(value[:-2]))
    else:
        value = 'value: 0x{:02x} {}'.format(offset, ' '.join('{:02X}'.format(ord(b)) for b in value))

    print '{}{}'.format(indentation, value)

    offset += cbData

    maximum = original_offset + original_len - 3

    if offset < maximum and dump_children:
        # There are child nodes.
        offset += padlen(offset)

        indent += 1
        while offset < maximum:
            offset += padlen(offset)
            offset = dump_node(a, offset, indent)

    return offset


def toucs2(text):
    # There isn't a UCS2 encoding in Python (surprising considering the 2-byte representation is UCS-2, I believe).
    # UTF-16 will work for most characters that could be represented in UCS-2.  Using "_le" forces little endian and
    # eliminates the need for a byte-order-mark.
    #
    # Note that this also includes two zero-bytes (NULL terminator).

    if type(text) is str:
        text = unicode(text, 'unicode_escape')
    return text.encode('utf_16_le') + '\0\0'

def fromucs2(text):
    # Converts bytes encoded in UTF16 to a string object suitable for printing.
    return text and text.decode('utf_16_le').encode('latin1', errors='replace') or ''


if __name__ == '__main__':
    dump_file(sys.argv[1])
