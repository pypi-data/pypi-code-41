# -*- coding: iso-8859-15 -*-
#
# From the PDF

# ---------------------------------------------------------------------------#
# Logging
# ---------------------------------------------------------------------------#
import logging

_logger = logging.getLogger(__name__)


def V():
    return ['Voltage', 'V']


def A():
    return ['Ampere', 'A']


def AH():
    return ['Ampere hours', 'Ah']


def W():
    return ['Watt', 'W']


def C():
    return ['degree Celsius', '°C']  # \0xb0


def PC():
    return ['%, percentage', '%']


def KWH():
    return ['kWh, kiloWatt/hour', 'kWh']


def Ton():
    return ['1000kg', 't']


def MO():
    return ['milliohm', 'mOhm']


def I():
    return ['integer', '']


def SEC():
    return ['seconds', 's']


def MIN():
    return ['minutes', 'min']


def HOUR():
    return ['hours', 'h']


class Value:
    '''Value with unit'''

    def __init__(self, register, value):
        self.register = register
        if self.register.times != 1 and value is not None:
            self.value = 1.0 * value / self.register.times
        else:
            self.value = value

    def __str__(self):
        if self.value is None:
            return self.register.name + " = " + str(self.value)
        return self.register.name + " = " + str(self.value) + self.register.unit()[1]

    def __float__(self):
        return float(self.value)

    def __int__(self):
        return int(self.value)


class Register:
    def __init__(self, name, address, description, unit, times, size=1,code=""):
        self.name = name
        self.address = address
        self.description = description
        self.unit = unit
        self.times = times
        self.size = size
        self.code = code
    def is_coil(self):
        return self.address < 0x1000

    def is_discrete_input(self):
        return self.address >= 0x1000 and self.address < 0x3000

    def is_input_register(self):
        return self.address >= 0x3000 and self.address < 0x9000

    def is_holding_register(self):
        return self.address >= 0x9000

    def decode(self, response):
        if hasattr(response, "getRegister"):
            mask = rawvalue = lastvalue = 0
            for i in range(self.size):
                lastvalue = response.getRegister(i)
                rawvalue = rawvalue | (lastvalue << (i * 16))
                mask = (mask << 16) | 0xffff
            if (lastvalue & 0x8000) == 0x8000:
                # print rawvalue
                rawvalue = -(rawvalue ^ mask) - 1
            return Value(self, rawvalue)
        _logger.info("No value for register " + repr(self.name))
        return Value(self, None)

    def encode(self, value):
        # FIXME handle 2 word registers
        rawvalue = int(value * self.times)
        if rawvalue < 0:
            rawvalue = (-rawvalue - 1) ^ 0xffff
            # print rawvalue
        return rawvalue


class Coil(Register):
    def decode(self, response):
        if hasattr(response, "bits"):
            return Value(self, response.bits[0])
        _logger.info("No value for coil " + repr(self.name))
        return Value(self, None)
