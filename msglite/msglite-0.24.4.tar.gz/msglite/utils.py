"""
Utility functions of extract_msg.
"""
import os
import sys
import json
import pytz
import chardet
import logging
import argparse
import datetime

from msglite import constants

logger = logging.getLogger(__name__)


def properHex(inp):
    """
    Taken (with permission) from https://github.com/TheElementalOfCreation/creatorUtils
    """
    a = ''
    if isinstance(inp, str):
        a = ''.join([hex(ord(inp[x]))[2:].rjust(2, '0') for x in range(len(inp))])
    elif isinstance(inp, bytes):
        a = inp.hex()
    elif isinstance(inp, int):
        a = hex(inp)[2:]
    if len(a) % 2 != 0:
        a = '0' + a
    return a


def xstr(s):
    return '' if s is None else str(s)


def guess_encoding(raw):
    if raw is None:
        return
    result = chardet.detect(raw)
    if result.get('confidence') > 0.5:
        encoding = result.get('encoding')
        if encoding == 'ascii':
            return 'utf-8'
        return encoding


def divide(string, length):
    """
    Taken (with permission) from https://github.com/TheElementalOfCreation/creatorUtils

    Divides a string into multiple substrings of equal length
    :param string: string to be divided.
    :param length: length of each division.
    :returns: list containing the divided strings.

    Example:
    >>>> a = divide('Hello World!', 2)
    >>>> print(a)
    ['He', 'll', 'o ', 'Wo', 'rl', 'd!']
    """
    return [string[length * x:length * (x + 1)] for x in range(int(len(string) / length))]


def fromTimeStamp(stamp):
    return datetime.datetime.fromtimestamp(stamp, pytz.UTC)


def has_len(obj):
    """
    Checks if :param obj: has a __len__ attribute.
    """
    try:
        obj.__len__
        return True
    except AttributeError:
        return False


def format_party(email, label):
    result = None
    if label is None or label == email:
        result = email
    else:
        result = label
        if email is not None:
            result += ' <' + email + '>'
    return result


def msgEpoch(inp):
    """
    Taken (with permission) from https://github.com/TheElementalOfCreation/creatorUtils
    """
    return (inp - 116444736000000000) / 10000000.0


def parse_type(_type, stream):
    """
    Converts the data in :param stream: to a
    much more accurate type, specified by
    :param _type:, if possible.
    :param stream # TODO what is stream?

    Some types require that :param prop_value: be specified. This can be retrieved from the Properties instance.

    WARNING: Not done. Do not try to implement anywhere where it is not already implemented
    """
    # WARNING Not done. Do not try to implement anywhere where it is not already implemented
    value = stream
    if _type == 0x0000:  # PtypUnspecified
        pass
    elif _type == 0x0001:  # PtypNull
        if value != b'\x00\x00\x00\x00\x00\x00\x00\x00':
            # DEBUG
            logger.warning('Property type is PtypNull, but is not equal to 0.')
        value = None
    elif _type == 0x0002:  # PtypInteger16
        value = constants.STI16.unpack(value)[0]
    elif _type == 0x0003:  # PtypInteger32
        value = constants.STI32.unpack(value)[0]
    elif _type == 0x0004:  # PtypFloating32
        value = constants.STF32.unpack(value)[0]
    elif _type == 0x0005:  # PtypFloating64
        value = constants.STF64.unpack(value)[0]
    elif _type == 0x0006:  # PtypCurrency
        value = (constants.STI64.unpack(value)[0]) / 10000.0
    elif _type == 0x0007:  # PtypFloatingTime
        value = constants.STF64.unpack(value)[0]
        # TODO parsing for this
        pass
    elif _type == 0x000A:  # PtypErrorCode
        value = constants.STI32.unpack(value)[0]
        # TODO parsing for this
        pass
    elif _type == 0x000B:  # PtypBoolean
        value = bool(constants.ST3.unpack(value)[0])
    elif _type == 0x000D:  # PtypObject/PtypEmbeddedTable
        # TODO parsing for this
        pass
    elif _type == 0x0014:  # PtypInteger64
        value = constants.STI64.unpack(value)[0]
    elif _type == 0x001E:  # PtypString8
        # TODO parsing for this
        pass
    elif _type == 0x001F:  # PtypString
        value = value.decode('utf_16_le')
    elif _type == 0x0040:  # PtypTime
        value = constants.ST3.unpack(value)[0]
    elif _type == 0x0048:  # PtypGuid
        # TODO parsing for this
        pass
    elif _type == 0x00FB:  # PtypServerId
        # TODO parsing for this
        pass
    elif _type == 0x00FD:  # PtypRestriction
        # TODO parsing for this
        pass
    elif _type == 0x00FE:  # PtypRuleAction
        # TODO parsing for this
        pass
    elif _type == 0x0102:  # PtypBinary
        # TODO parsing for this
        # Smh, how on earth am I going to code this???
        pass
    elif _type & 0x1000 == 0x1000:  # PtypMultiple
        # TODO parsing for `multiple` types
        pass
    return value
