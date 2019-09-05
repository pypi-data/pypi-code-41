"""SnapAV(tm) Binary(tm)-brand MoIP(tm) control module for real-time
status and configuration of a Binary-brand (from SnapAV) Media Over IP
controller.

Author: Greg J. Badros

$ cd .../path/to/home-assistant/
$ pip3 install --upgrade .../path/to/pybinarymoip

Then the custom_component/pybinarymoip/ and its require line will work.
(Or just make the custom_component's manifest.json requirements field 
mention this dependency.)

"""

__Author__ = "Greg J. Badros <badros@gmail.com>"
__copyright__ = "Copyright 2019, Greg J. Badros"

import logging
import socket
import select
import threading

# urllib.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
_LOGGER = logging.getLogger(__name__)


class MoIP(object):
    """Main SnapAV Binary Media Over IP (MoIP) class.

    This object owns the connection to the MoIP controller,
    reading status, and issuing state changes.
    """

    # pylint: disable=too-many-instance-attributes, too-many-arguments
    def __init__(self, host, username, password, area='',
                 noop_set_state=False):
        """Initializes the MoIP object. No connection is made to the device."""
        self._host = host
        self._port = 23
        self._username = username
        self._password = password
        self._firmware_version = None
        self._receivers = []
        self._transmitters = []
        self._devices = []
        self._sock = None
        self._timeout = 6
        self._socket_lock = threading.Lock()

    def connect(self):
        """Begin connection to the device and get its status."""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(self._timeout)
        try:
            self._sock.connect(
                (self._host, self._port))
        except socket.error as err:
            _LOGGER.error(
                "Unable to connect to %s on port %s: %s",
                self._host, self._port, err)
            return

        try:
            self._send("?Firmware\n")
            self._firmware_version = self._read_after_equals()
            _LOGGER.info("MoIP firmware version = %s",
                         self._firmware_version)
            self._send("?Devices\n")
            devices = self._read_after_equals()
            (tx, rx) = devices.split(",", 1)
            (num_tx, num_rx) = (int(tx), int(rx))
            _LOGGER.info("# Transmitters = %s, # Receivers = %s",
                         num_tx, num_rx)

            self._send("?Name=0\n")  # receivers
            rx_names = self._read_full()
            rx_lines = rx_names.split("\n")

            num = 1
            for rl in rx_lines[0:len(rx_lines)-1]:
                (_, a) = rl.split("=", 1)
                (_, _, name) = a.split(",", 2)
                self._receivers.append(MoIP_Receiver(self, num, name))
                num += 1

            self._send("?Name=1\n")  # transmitters
            tx_names = self._read_full()
            tx_lines = tx_names.split("\n")

            num = 1
            for tl in tx_lines[0:len(tx_lines)-1]:
                (_, a) = tl.split("=", 1)
                (_, _, name) = a.split(",", 2)
                self._transmitters.append(MoIP_Transmitter(self, num, name))
                num += 1

            self._update_inputs()
            _LOGGER.info("Transmitters = %s", self._transmitters)
            _LOGGER.info("Receivers = %s", self._receivers)
        except Exception as err:
            _LOGGER.error("Failed to initialize connection: %s", err)

    # TODO: skip updating again if last update was < ~2 sec ago
    def _update_inputs(self):
        with self._socket_lock:
            extra_text = self._read_full()
            if extra_text:
                _LOGGER.warning("Ignoring extra text: %r", extra_text)
            _LOGGER.warning
            self._send("?Receivers\n")
            answer = self._read_after_equals()
            if answer is None:
                _LOGGER.error("Got bad response from ?Receivers "
                              "-- cannot _update_inputs")
                return
            inputs = answer.split(",")
            for i in inputs:
                (tx, rx) = i.split(":", 1)
                tx_obj = self._transmitters[int(tx)-1]
                self._receivers[int(rx)-1]._set_input(tx_obj)

    def _send(self, str):
        self._last_send = str
        self._sock.send(str.encode())

    def _send_check(self, str, timeout):
        """Appends newline to str before sending, confirms OK response."""
        if timeout is None:
            timeout = self._timeout
        with self._socket_lock:
            self._send(str + "\n")
            response = self._read(timeout)
            _LOGGER.debug("sent '%s', got response = %s", str, response)
            if response != "OK":
                _LOGGER.error("Sent '%s' and got error response: %s",
                              str, response)

    def _read_raw(self, timeout=None):
        if timeout is None:
            timeout = self._timeout
        readable, _, _ = select.select(
            [self._sock], [], [], timeout)
        if not readable:
            return None
        answer = self._sock.recv(16384).decode()
        return answer

    def _read(self, timeout=None):
        if timeout is None:
            timeout = self._timeout
        answer = self._read_raw(timeout)
        if not answer:
            _LOGGER.warning(
                "Timeout (%s second(s)) waiting for a response after "
                "sending %r to %s on port %s.",
                self._timeout, self._last_send,
                self._host, self._port)
            return None
        if answer.endswith("\n"):
            answer = answer[0:len(answer)-1]
        _LOGGER.debug("read text: %s", answer)
        return answer

    def _read_full(self):
        answer = ""
        while True:
            line = self._read_raw(timeout=0.1)
            if line is None:
                _LOGGER.debug("read: %s", answer)
                return answer
            answer += line

    def _read_after_equals(self):
        answer = self._read()
        split_answer = answer.split("=", 1)
        if len(split_answer) > 1:
            return split_answer[1]
        else:
            return None

    @property
    def receivers(self):
        """Return the full list of receivers."""
        return self._receivers

    @property
    def transmitters(self):
        """Return the full list of transmitters."""
        return self._transmitters

    def _update(self, xml_str=None):
        pass

    def __str__(self):
        return "MoIP Controller @ %s [%s]" % (
            self._host,
            self._firmware_version)

    def __repr__(self):
        return str({'host': self._host,
                    'firmware_version': self._firmware_version})


class MoIP_Receiver(object):
    def __init__(self, mc, num, name, input=None):
        self._mc = mc
        self._num = num
        self._name = name
        self._input = input

    @property
    def num(self):
        return self._num

    @property
    def name(self):
        return self._name

    @property
    def input(self):
        return self._input

    # input is a Tx object (which has a .num property)
    def _set_input(self, input):
        self._input = input

    def _send_check(self, str, timeout):
        return self._mc._send_check(str, timeout)

    def switch_to_tx(self, tx):
        if not isinstance(tx, int):
            tx = tx.num
        self._send_check("!Switch=%s,%s" %
                         (tx, self._num), 12) # long timeout
        self._mc._update_inputs()

    def set_resolution(self, resolution):
        """Use resolution int in [0,4]::
        0 == Pass thru
        1 == 1080p 60Hz
        2 == 1080p 50Hz
        3 == 2160p 30Hz
        4 == 2160p 25Hz
        """
        self._send_check("!Resolution=%s,%d" % (self._num, resolution))

    def show_osd_message(self, msg):
        self._send_check("!OSD=%s,%s" % (self._num, msg))

    def reboot_device(self):
        self._send_check("!Reboot")

    def set_cec(self, cec_on):
        self._send_check("!CEC=%s,%d" % (self._num, 1 if cec_on else 0))

    def __str__(self):
        return "{MoIP Rx#%d \"%s\" from %s}" % (self._num,
                                                self._name,
                                                self._input)

    def __repr__(self):
        return str({'name': self._name,
                    'num': self._num,
                    'input': self._input,
                    'input_num': self._input and self._input.num,
                    'mc': self._mc})


class MoIP_Transmitter(object):
    def __init__(self, mc, num, name):
        self._mc = mc
        self._num = num
        self._name = name

    @property
    def num(self):
        return self._num

    @property
    def name(self):
        return self._name

    def __str__(self):
        return "{MoIP Tx#%d \"%s\"}" % (self._num,
                                        self._name)

    def __repr__(self):
        return str({'name': self._name,
                    'num': self._num,
                    'mc': self._mc})
