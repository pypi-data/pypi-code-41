#! /usr/bin/env python3
# Copyright (c) 2018 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT
"""
Simple python driver for the INA226.
"""
import logging
from time import sleep
try:
    import smbus
except ImportError:
    print("Cannot import smbus, resorting to printing")
    smbus = None


class INA226():
    """Driver for the INA226 current sensor

    Args:
        [address] - The I2C address of the INA device
        [operation_mode] - The starting mode of the INA, default continuous
        [shunt_val] - Value of the shunt resistor being used
        [bus_num] - Number of the I2C bus
    """
    # Regiter map
    REG_CONFIGURATION = 0x00
    REG_SHUNT_VOLTAGE = 0x01
    REG_BUS_VOLTAGE = 0x02
    REG_POWER = 0x03
    REG_CURRENT = 0x04
    REG_CALIBRATION = 0x05
    REG_MASK = 0x06
    REG_ALERT_LIMIT = 0x07
    REG_MANUFACTURER_ID = 0xFE
    REG_DIE_ID = 0xFF

    # Configuration register masks
    CONF_MASK_MODE = 0x0007
    CONF_MASK_SHUNT_CONV_TIME = 0x0038
    CONF_MASK_BUS_CONV_TIME = 0x01C0
    CONF_MASK_AVG = 0X0E00
    CONF_MASK_RST = 0X8000

    # Configuration register offsets
    CONF_OFFSET_MODE = 0
    CONF_OFFSET_SHUNT_CONV_TIME = 3
    CONF_OFFSET_BUS_CONV_TIME = 6
    CONF_OFFSET_AVG = 9
    CONF_OFFSET_RST = 15

    # Operation modes
    MODE_POWER_DOWN = 0
    MODE_SHUNT_TRIGGERED = 1
    MODE_BUS_TRIGGERED = 2
    MODE_SHUNT_BUS_TRIGGERED = 3
    # MODE_POWER_DOWN = 4
    MODE_SHUNT_CONTINUOUS = 5
    MODE_BUS_CONTINUOUS = 6
    MODE_SHUNT_BUS_CONTINUOUS = 7

    # Valid average values
    AVG_1 = 0
    AVG_4 = 1
    AVG_16 = 2
    AVG_64 = 3
    AVG_128 = 4
    AVG_256 = 5
    AVG_512 = 6
    AVG_1024 = 7

    SCALE_SHUNT_V = 0.0000025
    SCALE_BUS_V = 0.00125

    def __init__(self, address=0x44, operation_mode=MODE_SHUNT_BUS_CONTINUOUS,
                 shunt_val=1, bus_num=1):
        if smbus is None:
            self.bus = None
        else:
            self.bus = smbus.SMBus(bus_num)
        self.address = address
        self.shunt = shunt_val
        self.set_operation_mode(operation_mode)

    @staticmethod
    def _swap_16(word):
        return ((word >> 8) & 0x00FF) | ((word << 8) & 0xFF00)

    @staticmethod
    def _convert_to_v(value, scale):
        # get sign
        sign = (value & 0x8000) >> 15

        # two's complement
        binary = value - 1
        binary = (~binary) & 0xFFFF

        # scale the value
        result = value * scale

        # apply sign
        if sign:
            result = 0

        return result

    def _write_register(self, reg, value):
        value = self._swap_16(value)
        if self.bus is None:
            logging.info("i2c addr %r write word %r to reg %r", self.address,
                         reg, value)
        else:
            self.bus.write_word_data(self.address, reg, value)

    def _read_register(self, reg):
        if self.bus is None:
            logging.info("i2c addr %r read reg %r", self.address,
                         reg)
            data = 0
        else:
            data = self.bus.read_word_data(self.address, reg)
        return self._swap_16(data)

    def _set_configuration(self, value, mask, offset):
        conf = self._read_register(self.REG_CONFIGURATION)
        reg = (conf & ~(mask))
        reg |= (value << offset) & mask
        self._write_register(self.REG_CONFIGURATION, reg)

    def set_operation_mode(self, mode):
        """Set operation mode such as continuous or power down"""
        if mode not in range(self.MODE_POWER_DOWN,
                             self.MODE_SHUNT_BUS_CONTINUOUS + 1):
            raise AssertionError('Invalid mode {}'.format(mode))
        self._set_configuration(mode, self.CONF_MASK_MODE,
                                self.CONF_OFFSET_MODE)

    def set_avg(self, average):
        """Sets amount of samples to average"""
        if average not in range(self.AVG_1, self.AVG_1024):
            raise AssertionError('Invalid average {}'.format(average))
        self._set_configuration(average, self.CONF_MASK_AVG,
                                self.CONF_OFFSET_AVG)

    def set_shunt(self, shunt):
        """Sets shunt resistor value"""
        self.shunt = shunt

    def get_die_id(self):
        """Gets ina226 chip id"""
        return self._read_register(self.REG_DIE_ID)

    def get_shunt_voltage(self):
        """Gets shunt voltage drop in volts"""
        data = self._read_register(self.REG_SHUNT_VOLTAGE)
        return self._convert_to_v(data, self.SCALE_SHUNT_V)

    def get_bus_voltage(self):
        """Gets bus voltage in volts"""
        data = self._read_register(self.REG_BUS_VOLTAGE)
        return self._convert_to_v(data, self.SCALE_BUS_V)

    def get_current(self):
        """Gets current in amps"""
        shunt_v = self.get_shunt_voltage()
        return shunt_v / self.shunt

    def get_power(self):
        """Gets power in watts"""
        current = self.get_current()
        return current * self.get_bus_voltage()


if __name__ == '__main__':
    print('Testing INA226 connection')
    SHUNT = 3.9e3
    CM_DEV = INA226(0x44, shunt_val=SHUNT)

    while True:
        print('ID: {:02x}'.format(CM_DEV.get_die_id()))
        print('BUS: {} V'.format(CM_DEV.get_bus_voltage()))
        print('SHUNT: {} V'.format(CM_DEV.get_shunt_voltage()))
        print('CURRENT: {} A'.format(CM_DEV.get_current()))
        sleep(2)
