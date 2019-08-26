#! /usr/bin/env python3
# Copyright (c) 2019 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT
"""
This script can be used to flash stm32 devices through the ROM UART bootloader.
"""
import logging
import argparse
import time
import os
from pprint import pformat
import urllib.request

try:
    import wiringpi
except ImportError:
    wiringpi = None
try:
    from serial import Serial, PARITY_EVEN
    from serial.tools import list_ports
except ImportError as exc:
    print("Please install pyserial, \"pip3 install pyserial\"")
    raise exc
try:
    from deepdiff import DeepDiff
except ImportError:
    print("Cannot verify unless deepdiff is installed")
    print("Try \"pip3 install deepdiff\"")
    DeepDiff = None
try:
    from .pin_control import PinControl
except (ImportError, SystemError):
    try:
        from bph_pal.pin_control import PinControl
    except (ImportError, SystemError):
        from pin_control import PinControl


class GPIOPin():
    """GPIO pin control for turning on or off pins

    Args:
        pin(string, int): Designator for gpio pin, either RTS, DTR
                          raspberry pi GPIO number
        dev(Serial): If using RTS or DTR specify the serial port
        invert(bool): Invert io active/inactive levels of a pin
    """

    def __init__(self, pin, dev=None, invert=False, filename=None):
        try:
            pin = int(pin)
            wiringpi.wiringPiSetupGpio()
            wiringpi.pinMode(pin, wiringpi.GPIO.OUTPUT)
            if invert:
                self._active = lambda: wiringpi.digitalWrite(pin, 0)
                self._inactive = lambda: wiringpi.digitalWrite(pin, 1)
            else:
                self._active = lambda: wiringpi.digitalWrite(pin, 1)
                self._inactive = lambda: wiringpi.digitalWrite(pin, 0)
            self._input = lambda: wiringpi.pinMode(
                pin, wiringpi.GPIO.INPUT)

        except ValueError:
            if pin.upper() == "RTS":
                if invert:
                    self._active = lambda: dev.setRTS(0)
                    self._inactive = lambda: dev.setRTS(1)
                else:
                    self._active = lambda: dev.setRTS(1)
                    self._inactive = lambda: dev.setRTS(0)
                self._input = lambda: self._inactive
            elif pin.upper() == "DTR":
                if invert:
                    self._active = lambda: dev.setDTR(0)
                    self._inactive = lambda: dev.setDTR(1)
                else:
                    self._active = lambda: dev.setDTR(1)
                    self._inactive = lambda: dev.setDTR(0)
                    self._input = lambda: self._inactive
            else:

                pins = PinControl(filename=filename)
                wiringpi.wiringPiSetupGpio()
                wiringpi.pinMode(
                    pins.get_pin_num_and_key(pin)[0], wiringpi.GPIO.OUTPUT)
                if invert:
                    self._active = lambda: wiringpi.digitalWrite(
                        pins.get_pin_num_and_key(pin)[0], 0)
                    self._inactive = lambda: wiringpi.digitalWrite(
                        pins.get_pin_num_and_key(pin)[0], 1)
                else:
                    self._active = lambda: wiringpi.digitalWrite(
                        pins.get_pin_num_and_key(pin)[0], 1)
                    self._inactive = lambda: wiringpi.digitalWrite(
                        pins.get_pin_num_and_key(pin)[0], 0)
                self.input = lambda: wiringpi.pinMode(
                    pins.get_pin_num_and_key(pin)[0], wiringpi.GPIO.INPUT)
        self._state = 0
        self.inactive()

    def active(self):
        """Activates GPIO pin"""
        self._state = 1

        self._active()

    def inactive(self):
        """Deactivates GPIO pin"""
        self._state = 0
        self._inactive()

    def toggle(self):
        """Toogle the GPIO pin between active and inactive state"""
        if self._state:
            self.inactive()
        else:
            self.active()

    def toggle_on(self, timeout=0):
        """Toggles pin active for a specified time

        Args:
            timeout(float): time  to stay on in seconds
        """
        self.inactive()
        self.active()
        time.sleep(timeout)
        self.inactive()


class STM32BootloaderDevice():
    """Connection to a STM32 rom bootloader through UART

    args are a dictionary with various setups

    binfile:        Binary file of path, or name, if empty it will take a
                    *.bin file in the current directory
    dev:            Interface device, usually Serial, if empty it will try to
                    connect
    port:           If no dev specified then connect to port, if no port
                    specified it tries to connect to the first available port
    baudrate:       If not dev specified then the baudrate can be set, if no
                    baudrate then 115200
    reset_pin:      Pin designator for the reset pin, number of GPIO for
                    raspberry pi or RTS/DTR for serial to uart converter
    reset_invert:   Inverts state of the reset pin
    boot_pin:       Pin designator for the boot pin, number of GPIO for
                    raspberry pi or RTS/DTR for serial to uart converter
    boot_invert:    Inverts state of boot pin
    page_size:      Specify page size of device flash, used for quicker erase
    """
    _CMD = {"init": [0x7f], "get": [0x00], "read": [0x11], "write": [0x31],
            "erase": [0x43], "ext_erase": [0x44], "erase_global": [0xFF],
            "ext_erase_global": [0xFF, 0xFF]}
    _RESP = {"ack": [0x79], "nack": [0x1F]}
    _CHUNK_SIZE = 256

    def __init__(self, args):
        self._bytes_to_dev = None
        self._bytes_from_dev = None
        self._page_size = 1024
        logging.debug("args = %r", args)
        if 'page_size' in args:
            if args['page_size']:
                self._page_size = args['page_size']
        if args['erase'] or args['verify'] in args or args['write'] in args:
            if args['philip_ver']:
                self.read_binfile_from_online(args['philip_ver'])
            else:
                self.read_binfile(args['binfile'])
        if 'dev' in args:
            self._dev = args['dev']
        else:
            if 'port' not in args:
                args['port'] = None
            if 'baudrate' not in args:
                args['baudrate'] = 115200
            self._dev = self._connect(args['port'], args['baudrate'])

        if 'reset_invert' not in args:
            args['reset_invert'] = False
        self._reset_pin = GPIOPin(args['reset_pin'], self._dev,
                                  args['reset_invert'])
        if 'boot_invert' not in args:

            args['boot_invert'] = False
        self._boot_pin = GPIOPin(args['boot_pin'], self._dev,
                                 args['boot_invert'])
        self.start_bootloader()
        self.bootloader_version = self._get_bootloader_version()

    def read_binfile(self, binfile=None):
        """Read the bytes to program from file or directory with .bin file

        Args:
            binfile(string): Path to binary file
        """
        if not binfile:
            binfile = [s for s in os.listdir(os.getcwd()) if ".bin" in s][0]
            logging.debug("Found binary to read")
        with open(binfile, 'rb') as bfile:
            logging.info("Reading %s", binfile)
            self._bytes_to_dev = list(bfile.read())
            logging.debug("Binary has 0x%X bytes", len(self._bytes_to_dev))

    def read_binfile_from_online(self, version):
        """Read the bytes to program from file or directory with .bin file

        Args:
            binfile(string): Path to binary file
        """
        url = "https://github.com/riot-appstore/PHiLIP/releases/download/v"
        url += version
        url += "/PHiLIP-BLUEPILL.bin"
        binfile = urllib.request.urlretrieve(url)[0]
        logging.debug("fetching binary from %r", url)
        with open(binfile, 'rb') as bfile:
            logging.info("Reading %s", binfile)
            self._bytes_to_dev = list(bfile.read())
            logging.debug("Binary has 0x%X bytes", len(self._bytes_to_dev))

    @staticmethod
    def _connect(port, baudrate):
        if not port:
            port = list_ports.comports()[0][0]
        logging.info("Open port %r, baud %r", port, baudrate)
        return Serial(port=port, baudrate=baudrate,
                      parity=PARITY_EVEN, timeout=1)

    def _get_bootloader_version(self):
        logging.debug("get_bootloader_version")
        self._send_cmd(self._CMD['get'])
        read_len = self._read_bytes()[0]
        version = self._read_bytes()[0]
        commands = self._read_bytes(read_len=read_len)
        logging.info("Bootloader: 0x%X", version)
        logging.debug("Commands: %r", commands)
        return version

    def read_memory(self, addr=0x08000000, length=None):
        """Reads memory from the device memory

        Args:
            addr (int): Address to start reading
            length (int): Number of bytes to read

        Returns:
            bytes: The bytes read from memory
        """
        if length is None:
            length = len(self._bytes_to_dev)
        assert length > 0
        logging.info("Reading %i bytes from 0x%X", length, addr)
        read_bytes = []
        while length > self._CHUNK_SIZE:
            read_bytes.extend(self._read_memory_chunk(addr, self._CHUNK_SIZE))
            addr += self._CHUNK_SIZE
            length -= self._CHUNK_SIZE
        if length:
            read_bytes.extend(self._read_memory_chunk(addr, length))
        logging.info("Read %i bytes from device", len(read_bytes))
        self._bytes_from_dev = read_bytes
        return read_bytes

    def _read_memory_chunk(self, addr, length):
        logging.debug("_read_memory_chunk %i bytes from 0x%X", length, addr)
        assert length <= self._CHUNK_SIZE
        self._send_cmd(self._CMD['read'])
        self._send_cmd(list(addr.to_bytes(4, byteorder='big')), crc=0)
        self._send_cmd([length - 1])
        return self._read_bytes(length)

    def write_memory(self, bytes_to_write=None, addr=0x08000000):
        """Writes bytes to the device memory

        Args:
            bytes_to_write (bytes, list): Bytes to write
            addr (int): Address to start writing
        """
        if not bytes_to_write:
            bytes_to_write = self._bytes_to_dev
        assert len(bytes_to_write) > 0

        logging.info("Writing %i bytes to 0x%X", len(bytes_to_write), addr)
        bytes_copy = list(bytes_to_write)
        self._bytes_to_dev = list(bytes_to_write)
        while len(bytes_copy) > self._CHUNK_SIZE:
            self._write_memory_chunk(bytes_copy[0:self._CHUNK_SIZE], addr)
            bytes_copy = bytes_copy[self._CHUNK_SIZE:]
            addr += self._CHUNK_SIZE
        if len(bytes_copy):
            self._write_memory_chunk(bytes_copy, addr)
        logging.info("Wrote %i bytes to device", len(bytes_to_write))

    def _write_memory_chunk(self, bytes_to_write, addr):
        length = len(bytes_to_write)
        logging.debug("_write_memory_chunk %i bytes to 0x%X", length, addr)
        assert length <= self._CHUNK_SIZE
        self._send_cmd(self._CMD['write'])
        self._send_cmd(list(addr.to_bytes(4, byteorder='big')), crc=0)
        self._write_bytes([self._CHUNK_SIZE - 1])
        if length < self._CHUNK_SIZE:
            bytes_to_write.extend([0]*(self._CHUNK_SIZE - length))
        self._send_cmd(bytes_to_write)

    def erase_memory(self, global_erase=False):
        """Erases all memory from the device"""
        logging.info("Erasing memory, it may take a while")
        tmp = self._dev.timeout
        self._dev.timeout = 20
        if self.bootloader_version < 0x30:
            self._erase_memory(global_erase)
        else:
            self._ext_erase_memory(global_erase)
        self._dev.timeout = tmp
        self._bytes_from_dev = None
        logging.info("Memory is erased")

    def _erase_memory(self, global_erase):
        logging.debug("_erase_memory, global=%r", global_erase)
        self._send_cmd(self._CMD['erase'])
        if global_erase:
            self._send_cmd(self._CMD['erase_global'])
        else:
            length = len(self._bytes_to_dev)
            assert length > 0
            pages = int((length - 1)/self._page_size)
            erase_cmd = [pages]
            for page in range(0, pages + 1):
                erase_cmd.append(page)
            self._send_cmd(erase_cmd, crc=0x00)

    def _ext_erase_memory(self, global_erase):
        logging.debug("_ext_erase_memory, global=%r", global_erase)
        self._send_cmd(self._CMD['ext_erase'])
        if global_erase:
            self._send_cmd(self._CMD['ext_erase_global'], crc=0x00)
        else:
            length = len(self._bytes_to_dev)
            assert length > 0
            pages = int((length - 1)/self._page_size)
            erase_cmd = list(pages.to_bytes(2, byteorder='big'))
            for page in range(0, pages+1):
                erase_cmd.extend(list(page.to_bytes(2, byteorder='big')))
            self._send_cmd(erase_cmd, crc=0x00)

    def verify_memory(self, addr=0x08000000):
        """Checks memory from the device against expected values

        If device memory has not been read then it will read from the device.

        Args:
            addr (int): Address to start reading

        Returns:
            bool: True if matches memory, false if not
        """
        if not self._bytes_from_dev:
            self.read_memory(addr, len(self._bytes_to_dev))
        if self._bytes_from_dev == self._bytes_to_dev:
            logging.info("Verification successful")
            return True
        else:
            logging.info("Verification failed")
            logging.debug(pformat(DeepDiff(self._bytes_from_dev,
                                           self._bytes_to_dev), indent=2))
            return False

    def start_bootloader(self):
        """Starts the uart bootloader of the device

        This will set the boot pin, provide a reset, provide a sync messeage
        """
        logging.debug("start_bootloader")
        self._boot_pin.active()
        time.sleep(0.1)
        self.reset()
        self._send_cmd(self._CMD['init'], retry=5,
                       accept_nack=True, crc=None)

    def stop_bootloader(self):
        """Stops the bootloader of the device and starts normal operation"""
        logging.debug("stop_bootloader")
        self._boot_pin.inactive()
        self.reset()
        self._reset_pin.input()

    def reset(self):
        """Resets the device

        Takes a total of 600ms, this allows for the startup to occur
        """
        logging.debug("reset")
        self._reset_pin.toggle_on(0.1)
        time.sleep(0.5)

    def _send_cmd(self, write_bytes, retry=1, accept_nack=False, crc=0xFF):
        self._dev.flushInput()
        self._dev.flushOutput()
        if crc is not None:
            for crc_byte in write_bytes:
                crc ^= crc_byte
            write_bytes = write_bytes.copy()
            write_bytes.append(crc)
        while retry:
            self._write_bytes(write_bytes)
            response = self._read_bytes()
            if response == self._RESP['ack']:
                return
            if response == self._RESP['nack']:
                if accept_nack:
                    return
                raise ValueError("{} recieved NACK".format(write_bytes))
            retry -= 1
        raise TimeoutError("Could not read bytes, cmd={}".format(write_bytes))

    def _write_bytes(self, write_bytes):
        logging.debug("Writing bytes: %r", write_bytes)
        self._dev.write(bytes(write_bytes))

    def _read_bytes(self, read_len=1):
        logging.debug("Reading %i bytes", read_len)
        read_bytes = list(self._dev.read(size=read_len))
        logging.debug("read bytes = %r", read_bytes)
        return read_bytes

    def __del__(self):
        self.stop_bootloader()
        self._dev.close()


def main():
    """Main program"""
    parser = argparse.ArgumentParser()
    log_levels = ('debug', 'info', 'warning', 'error', 'fatal', 'critical')

    parser.add_argument('--port', '-p', help="""
Specifies the serial port, for example /dev/ttyUSB0, if none then the first
available port is taken""",
                        default=None)
    parser.add_argument('--baudrate', '-b', help='Serial port baudrate',
                        default=115200)
    parser.add_argument('--read', '-r', help='Flag to read memory',
                        action="store_true", default=False)
    parser.add_argument('--write', '-w', help='Flag to write memory',
                        action="store_true", default=False)
    parser.add_argument('--verify', '-v', help='Verifies memory',
                        action="store_true", default=False)
    parser.add_argument('--erase', '-e', help='Erases memory',
                        action="store_true", default=False)
    parser.add_argument('--binfile', '-bf', help="""
Binary file to program, if not provided it takes the first *.bin file in the
current directory""",
                        default=None)
    parser.add_argument('--reset_pin', '-rp',
                        help='Reset pin designator, int/RTS/DTR/gpio_map pin',
                        default="BP_RST")
    parser.add_argument('--boot_pin', '-bp',
                        help='Boot pin designator, int/RTS/DTR/gpio_map pin',
                        default="BOOT0")
    parser.add_argument('--reset_invert', '-ri', help='Reset pin invert',
                        action="store_false", default=True)
    parser.add_argument('--boot_invert', '-bi', help='Boot pin invert',
                        action="store_true", default=False)
    parser.add_argument('--page_size', '-psz',
                        help='Flash page size of the device only for erase',
                        default=None)
    parser.add_argument('--pin_config_filename', '-pf',
                        help="Filename of config",
                        default='bph_pinout_v2c.json')
    parser.add_argument('--philip_ver', '-pv',
                        help='Version of PHiLIP to fetch from online')
    parser.add_argument('--loglevel', '-l', choices=log_levels, default='info',
                        help='Python logger log level')

    start = time.time()
    pargs = parser.parse_args()
    if pargs.loglevel:
        loglevel = logging.getLevelName(pargs.loglevel.upper())
        logging.basicConfig(level=loglevel)
    stmboot = STM32BootloaderDevice(vars(pargs))
    if pargs.erase:
        stmboot.erase_memory()
    if pargs.write:
        stmboot.write_memory()
    if pargs.read:
        stmboot.read_memory()
    if pargs.verify:
        stmboot.verify_memory()
    logging.info("total time: %r", time.time() - start)


if __name__ == '__main__':
    main()
