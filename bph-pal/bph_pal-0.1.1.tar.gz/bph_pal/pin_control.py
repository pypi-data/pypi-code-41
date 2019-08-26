# Copyright (c) 2019 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT
"""wiringpi pin control wrapper
This module handles wapping the wiringpi pinout to one designated from the
pin config file.
"""
import logging
import os
from pathlib import Path
from json import load
try:
    import wiringpi
except ImportError:
    print("Cannot import wiring pi, resorting to printing")
    wiringpi = None


class PinControl:
    """Controls wiring pi pins with wrapper for bph"""

    def __init__(self, path=None, filename=None,
                 init_state=False):
        if path is None:
            path = str(Path(__file__).parents[0]) + '/config/'
        if filename is None:
            filename = [f for f in os.listdir(path) if f.endswith('.json')][0]
        full_path = os.path.join(path, filename)
        self.load_pinmap(full_path, init_state)

    def load_pinmap(self, bph_pinout_file, init_state):
        """Loads specific pinout map"""
        logging.debug("Loading pinout from %r", bph_pinout_file)
        with open(bph_pinout_file) as bpf:
            self.pinout = load(bpf)
        logging.debug("pinout = %r", self.pinout)
        self.gpio_map = self.pinout['gpio']
        self.set_gpio_map(self.gpio_map, init_state)

    @staticmethod
    def set_gpio_map(gpio_map, initialize):
        """Sets the GPIO map and can initialize to default values"""
        logging.debug('Setting defaults')
        if wiringpi is None:
            logging.info("Setting up gpio")
        else:
            wiringpi.wiringPiSetupGpio()
        for gpio_value in gpio_map.values():
            logging.debug("Setting GPIO %r: on pin %r to %r",
                          gpio_value['name'],
                          gpio_value['pin'],
                          gpio_value['mode'])
            if initialize:
                if wiringpi is None:
                    logging.info("Pin %r mode is %r", gpio_value['pin'],
                                 gpio_value['mode'])
                else:
                    wiringpi.pinMode(gpio_value['pin'], gpio_value['mode'])
            if 'state' in gpio_value and initialize:
                if wiringpi is None:
                    logging.info("Pin %r state is %r", gpio_value['pin'],
                                 gpio_value['state'])
                else:
                    wiringpi.digitalWrite(gpio_value['pin'],
                                          gpio_value['state'])
                logging.debug("State is %r", gpio_value['state'])

    def pin_to_input(self, arg):
        """Sets the pin to an input"""
        pin_num, pin_key = self.get_pin_num_and_key(arg)
        if wiringpi is None:
            logging.info("Pin %r mode is %r", pin_num, 0)
            self.gpio_map[pin_key]['mode'] = 0
        else:
            wiringpi.pinMode(pin_num, wiringpi.GPIO.INPUT)
            self.gpio_map[pin_key]['mode'] = wiringpi.GPIO.INPUT
        self.gpio_map[pin_key].pop("state", None)

    def write_pin_state(self, arg, state):
        """Writes the pin state..."""
        pin_num, pin_key = self.get_pin_num_and_key(arg)
        logging.debug("Writing pin %r for %r to %r", pin_num, pin_key, state)
        if wiringpi is None:
            logging.info("Pin %r mode is %r", pin_num, 1)
            logging.info("Pin %r state is %r", pin_num, state)
            self.gpio_map[pin_key]['mode'] = 1
        else:
            wiringpi.pinMode(pin_num, wiringpi.GPIO.OUTPUT)
            wiringpi.digitalWrite(pin_num, state)
            self.gpio_map[pin_key]['mode'] = wiringpi.GPIO.OUTPUT
        self.gpio_map[pin_key]['state'] = state

    def get_pin_num_and_key(self, arg):
        """Gets the pin number and key from a number or key from the map"""
        pin_num = None
        pin_key = None
        if arg in self.gpio_map:
            pin_num = self.gpio_map[arg]['pin']
        else:
            for val in self.gpio_map.values():
                if val['name'] == arg:
                    pin_num = val['pin']
                    break
            if pin_num is None:
                pin_num = int(arg)
        for key, val in self.gpio_map.items():
            if val['pin'] == pin_num:
                pin_key = key
                break
        return pin_num, pin_key
