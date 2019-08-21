import logging

from msglite import constants
from msglite.utils import properHex

logger = logging.getLogger(__name__)


def create_prop(string):
    temp = constants.ST2.unpack(string)[0]
    if temp in constants.FIXED_LENGTH_PROPS:
        return FixedLengthProp(string)
    else:
        if temp not in constants.VARIABLE_LENGTH_PROPS:
            # DEBUG
            logger.warning('Unknown property type: {}'.format(properHex(temp)))
        return VariableLengthProp(string)


class PropBase(object):
    """
    Base class for Prop instances.
    """

    def __init__(self, string):
        super(PropBase, self).__init__()
        self.raw = string
        self.name = properHex(string[3::-1]).upper()
        self.type, self.flags = constants.ST2.unpack(string)
        self.flag_mandatory = self.flags & 1 == 1
        self.flag_readable = self.flags & 2 == 2
        self.flag_writable = self.flags & 4 == 4


class FixedLengthProp(PropBase):
    """
    Class to contain the data for a single fixed length property.

    Currently a work in progress.
    """

    def __init__(self, string):
        super(FixedLengthProp, self).__init__(string)
        self.value = self.parse_type(self.type, constants.STFIX.unpack(string)[0])

    def parse_type(self, _type, stream):
        """
        Converts the data in :param stream: to a
        much more accurate type, specified by
        :param _type:, if possible.
        :param stream: #TODO what is stream for?

        WARNING: Not done.
        """
        # WARNING Not done.
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
            value = (constants.STI64.unpack(value))[0] / 10000.0
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
        elif _type == 0x0014:  # PtypInteger64
            value = constants.STI64.unpack(value)[0]
        elif _type == 0x0040:  # PtypTime
            value = constants.ST3.unpack(value)[0]
        elif _type == 0x0048:  # PtypGuid
            # TODO parsing for this
            pass
        return value

    def __repr__(self):
        return '<FLProp(%r)>' % self.value


class VariableLengthProp(PropBase):
    """
    Class to contain the data for a single variable length property.
    """

    def __init__(self, string):
        super(VariableLengthProp, self).__init__(string)
        self.length, self.reserved_flags = constants.STVAR.unpack(string)
        if self.type == 0x001E:
            self.real_length = self.length - 1
        elif self.type == 0x001F:
            self.real_length = self.length - 2
        elif self.type == 0x000D:
            self.real_length = None
        else:
            self.real_length = self.length

    def __repr__(self):
        return '<VLProp(%r)>' % self.real_length