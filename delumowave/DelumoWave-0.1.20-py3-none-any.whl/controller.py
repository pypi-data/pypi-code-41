#!/usr/bin/env python3

import errno
import logging
from time import time, sleep
from typing import Union, Optional

import serial
from serial import SerialException

from delumowave.config.delumo import (DEVICE, COMMAND, EEPROM_SIZE)

# import threading
from threading import Lock as threading_lock
from multiprocessing import Lock as multiprocessing_lock

_LOGGER = logging.getLogger(__name__)

# Required delay between recording to UART
UART_INTERVAL = 0.1


class NodeAddrError(ValueError):
    def __init__(self, node_addr, msg=None):
        if msg is None:
            msg = f'Node address: {node_addr} -  must be {bytes}, {list} or ' \
                  f'{tuple}, must have size 3, and each item must be {int} ' \
                  f'in range [0x00, 0xFF]'
        super().__init__(msg)


class NodeVersionError(ValueError):
    def __init__(self, node_version, msg=None):
        if msg is None:
            msg = f'Node version: {node_version} - must be {int} in range ' \
                  f'[0x00, 0xFF]'
        super().__init__(msg)


class ProcedureError(ValueError):
    def __init__(self, procedure, msg=None):
        if msg is None:
            msg = f'Procedure: {procedure} - must be {int} in range [0x00, 0xFF]'
        super().__init__(msg)


class DataLengthError(ValueError):
    def __init__(self, data_length, msg=None):
        if msg is None:
            msg = f'Data length: {data_length} -  must be {int} in range ' \
                  f'[0x00, 0xFF]'
        super().__init__(msg)


class EEPROMAddrError(ValueError):
    def __init__(self, eeprom_addr, msg=None):
        if msg is None:
            msg = f'EEPROM address: {eeprom_addr} - must be {int} in range ' \
                  f'[0x00, 0xFF]'
        super().__init__(msg)


class EEPROMDataError(ValueError):
    def __init__(self, eeprom_data, msg=None):
        if msg is None:
            msg = f'EEPROM data: {eeprom_data} - must be {bytes}, {list}, ' \
                  f'{tuple} and each item must be {int} in range [0x00, 0xFF]' \
                  f' or single {int} in range [0x00, 0xFF]. And EEPROM data ' \
                  f'must not be out of EEPROM.'
        super().__init__(msg)


class RequestError(ValueError):
    def __init__(self, request, msg=None):
        if msg is None:
            msg = f'Request: {request} - must be {bytes}, {list} or {tuple} ' \
                  f'and each item must be {int} in range [0x00, 0xFF]'
        super().__init__(msg)


class RequestLengthError(ValueError):
    def __init__(self,
                 request_length: int,
                 expected_request_length: int,
                 msg=None):
        if msg is None:
            msg = f'Request length {request_length} is not equal expected ' \
                  f'request length {expected_request_length}'
        super().__init__(msg)


class ResponseError(ValueError):
    def __init__(self, response, msg=None):
        if msg is None:
            msg = f'Response: {response} - must be {bytes}, {list} or {tuple}' \
                  f' and each item must be {int} in range [0x00, 0xFF]'
        super().__init__(f'Response: {response} - ' + msg)


class RadioControllerBlocked(SerialException):
    def __init__(self, msg=None):
        if msg is None:
            msg = 'Radio controller is blocked by other process.'
        super().__init__(errno.EAGAIN, msg)


class NotSupportedError(KeyError):
    def __init__(self, msg=None):
        if msg is None:
            msg = 'Operation is not supported for this node firmware version.'
        super().__init__(msg)


def hex_repr(data: Union[int, bytes, list, tuple, set]) -> Optional[str]:
    """
    Get hexadecimal representation of data (single int digit or
    bytes, list of int, tuple of int, set of int). This function is used for
    pretty logging.

    Parameters
    ----------
    data : Union[int, bytes, list, tuple, set]
        Data that should be represented in hex.

    Returns
    -------
    str
        Depending on the input data type function returns value could be
        represented in string of single hex int or string of list of int.

    Examples
    --------
    If input data has ``int`` type

    >>> hex_repr(18)
    '0x12'

    If input data has ``bytes`` type

    >>> hex_repr(b'\\x12\\x23\\x34')
    '[0x12, 0x23, 0x34]'

    If input data has ``list`` type

    >>> hex_repr([18, 35, 52])
    '[0x12, 0x23, 0x34]'

    """

    if isinstance(data, (bytes, list, tuple, set)) and \
            all(isinstance(x, int) for x in data):
        return f'[{", ".join([f"{b:#04x}" for b in data])}]'
    elif isinstance(data, int):
        return f'{data:#04x}'
    else:
        return None


def valid_node_addr(node_addr: Union[bytes, list, tuple]) -> bool:
    if not isinstance(node_addr, (bytes, list, tuple)):
        return False
    if not len(node_addr) == 3:
        return False
    if not all((isinstance(x, int) and 0x00 <= x <= 0xFF) for x in node_addr):
        return False
    return True


class DelumoWaveController:
    def __init__(self,
                 port_path: str = '/dev/ttyUSB0',
                 baudrate: int = 115200,
                 bytesize: int = serial.EIGHTBITS,
                 parity: int = serial.PARITY_NONE,
                 stopbits: int = serial.STOPBITS_ONE,
                 timeout: float = 3.0,
                 # write_timeout: float = 3.0,
                 unlock_timeout: float = 5.0,
                 sleep_time: float = 0.1,
                 block: bool = False):
        """
        Base class for low-level communication with nodes. This class provide
        base methods to send command to nodes, read nodes' EEPROM and write to
        nodes' EEPROM via radio controller, connected by UART or USB.

        Parameters
        ----------
        port_path : str, optional
            Device name via which radio controller is connected: depending on
            operating system. e.g. ``/dev/ttyUSB0``, ``/dev/ttyAMA0``
            on GNU/Linux or ``COM3`` on Windows.
            By default, ``/dev/ttyAMA0`` is used.
        baudrate : int, optional
            Baud rate such as 9600 or 115200 etc. By default, 115200 is used.
        bytesize : int, optional
            Number of data bits. Possible values: ``FIVEBITS``, ``SIXBITS``,
            ``SEVENBITS``, ``EIGHTBITS``. By default, ``EIGHTBITS`` is used.
        parity : int, optional
            Enable parity checking. Possible values: ``PARITY_NONE``,
            ``PARITY_EVEN``, ``PARITY_ODD``, ``PARITY_MARK``, ``PARITY_SPACE``.
            By default, ``PARITY_NONE`` is used.
        stopbits : int, optional
            Number of stop bits. Possible values: ``STOPBITS_ONE``,
            ``STOPBITS_ONE_POINT_FIVE``, ``STOPBITS_TWO``.
            By default, ``STOPBITS_ONE`` is used.
        timeout : float, optional
            Set a read timeout value. By default, ``3.0`` is used.
        write_timeout : float, optional
            Set a write timeout value. By default, ``3.0`` is used.
        unlock_timeout : float, optional
            How long (in seconds) try to to open radio controller in case if it
            is blocked by other process. By default, 5 seconds.
        sleep_time : float, optional
            How often (in seconds) try to open radio controller in case if it is
            blocked by other process. By default, each 0.1 second.
        block : bool, optional
            Block radio controller and wait until a radio transmission and node
            processing are complete. By default, block is False.
        logging_level : Union[str, int, None], optional
            Available logging levels: ``DEBUG``, ``INFO``, ``WARNING``,
            ``ERROR``, ``CRITICAL``, ``NOTSET``. Also it could be written by
            numeric values.
            By default, logging is disabled.

        Raises
        ------
        ValueError
            Will be raised when parameter are out of range, e.g. baud rate,
            data bits.
        SerialException
            In case the device can not be found or can not be configured.

        See Also
        --------
        serial.serial_for_url : function to open serial port
        logging.setLevel : function to set logging level (see available
            constants).
        """

        _LOGGER.debug(f'DelumoWaveController __init__() with Args: {locals()}')

        self._port_path = port_path
        self.__unlock_timeout = unlock_timeout
        self.__sleep_time = sleep_time
        self.__block = block
        self.__node_version = None
        self.__last_uart = 0.0
        self.__is_busy = False
        # self.__lock = threading.Lock()
        self.__threading_lock = threading_lock()
        self.__multiprocessing_lock = multiprocessing_lock()

        self._controller = serial.serial_for_url(url=port_path,
                                                 baudrate=baudrate,
                                                 bytesize=bytesize,
                                                 parity=parity,
                                                 stopbits=stopbits,
                                                 timeout=timeout,
                                                 # write_timeout=write_timeout,
                                                 # do_not_open=True,
                                                 exclusive=True)

        _LOGGER.info(f'Radio controller is ready: {self._controller}')

    def __del__(self):
        self._controller.close()
        _LOGGER.info(f'Radio controller is closed: {self._controller}')

    def _pretty_eeprom(self, eeprom: bytes) -> str:
        """
        Compose pretty string from array of hex data (EEPROM) for logging
        """

        pretty_eeprom = ''
        lines, columns = divmod(len(eeprom), 16)
        for line in range(lines):
            pretty_eeprom += '\n\t ' + \
                             ' '.join([hex_repr(b) for b in
                                       eeprom[line * 16: (line + 1) * 16]])
        if columns:
            pretty_eeprom += '\n\t ' + \
                             ' '.join([hex_repr(b) for b in
                                       eeprom[lines * 16: len(eeprom)]])

        return pretty_eeprom

    def _checksum(self, data: Union[bytes, list, tuple, set]) -> int:
        """Calculate checksum for data.

        Summarize all bytes (int) in data and return least significant byte.

        Parameters
        ----------
        data : Union[bytes, list, tuple, set]
            Data, for which checksum is calculated. It could be bytes or list,
            tuple, set of int values.

        Returns
        -------
        checksum : int
            Calculated checksum for input data.

        Examples
        --------
        >>> self._checksum(b'\x00\x12\x23\x34\x02\x80\x00')
        235
        >>> self._checksum([0x00, 0x12, 0x23, 0x34, 0x02, 0x80, 0x00])
        235
        """
        if not isinstance(data, (bytes, list, tuple, set)):
            raise TypeError(f'Data must be {bytes}, {list} or {tuple}, '
                            f'not {type(data)}')
        if not all((isinstance(x, int) and 0x00 <= x <= 0xFF) for x in data):
            raise TypeError(f'{type(data)} items\' data must be {int} and be '
                            f'in range [0x00, 0xFF]')

        return sum(data) & 0xFF

    def _check_node_addr(self, node_addr: Union[bytes, list, tuple]):
        """
        Check node address
        """
        if not isinstance(node_addr, (bytes, list, tuple)):
            raise NodeAddrError(node_addr)
        if not len(node_addr) == 3:
            raise NodeAddrError(node_addr)
        if not all((isinstance(x, int) and 0x00 <= x <= 0xFF) for x in node_addr):
            raise NodeAddrError(node_addr)

    def _request_cmd(self,
                    node_addr: Union[bytes, list, tuple],
                    procedure: int,
                    device: int = DEVICE['COMPUTER']) -> bytes:
        # Check node address
        self._check_node_addr(node_addr)

        # Check procedure
        if not (isinstance(procedure, int) and 0x00 <= procedure <= 0xFF):
            raise ProcedureError(procedure)

        request = [device,  # Device ID
                   node_addr[0],  # Address
                   node_addr[1],  # Address
                   node_addr[2],  # Address
                   COMMAND['EXECUTE_PROCEDURE'],  # Command
                   procedure,  # Procedure number
                   0x00]  # Reserve
        request.append(self._checksum(request[1:]))  # Checksum

        return bytes(request)

    def _request_read(self,
                     node_addr: Union[bytes, list, tuple],
                     data_length: int,
                     eeprom_addr: int,
                     device: int = DEVICE['COMPUTER']) -> (bytes, int):
        # Check node address
        self._check_node_addr(node_addr)

        # Check EEPROM address
        if not (isinstance(eeprom_addr, int) and 0x00 <= eeprom_addr <= 0xFF):
            raise EEPROMAddrError(eeprom_addr)

        # Check data length
        if not (isinstance(data_length, int) and 0x00 <= data_length <= 0xFF):
            raise DataLengthError(data_length)

        request = [device,  # Device ID
                   node_addr[0],  # Address
                   node_addr[1],  # Address
                   node_addr[2],  # Address
                   COMMAND['READ_EEPROM'],  # Command
                   data_length,  # Size of data to read
                   eeprom_addr]  # Start address EEPROM, where read
        request.append(self._checksum(request[1:]))  # Checksum

        # If requested data length is 0x00, then it expected whole EEPROM
        # data from eeprom_addr to the end of EEPROM. Otherwise it expect
        # data_length bytes from addr_eeprom
        if data_length == 0x00:
            requested_data_length = EEPROM_SIZE - eeprom_addr
        else:
            requested_data_length = data_length

        # Request length + requested data length + 1 byte of check sum
        expected_response_length = len(request) + requested_data_length + 1

        return bytes(request), expected_response_length

    def _request_write(self,
                       node_addr: Union[bytes, list, tuple],
                       eeprom_data,
                       eeprom_addr: int,
                       device: int = DEVICE['COMPUTER']):
        # Check node address
        self._check_node_addr(node_addr)

        # Check EEPROM address
        if not (isinstance(eeprom_addr, int) and 0x00 <= eeprom_addr <= 0xFF):
            raise EEPROMAddrError(eeprom_addr)

        # Check that data is not out of EEPROM scope
        if not isinstance(eeprom_data, (bytes, list, tuple, int)):
            raise EEPROMDataError(eeprom_data)
        if isinstance(eeprom_data, int):
            eeprom_data = [eeprom_data]
        elif len(eeprom_data) >= EEPROM_SIZE - eeprom_addr:
            raise EEPROMDataError(eeprom_data)
        if not all((isinstance(x, int) and 0x00 <= x <= 0xFF) for x in eeprom_data):
            raise EEPROMDataError(eeprom_data)

        request = [device,  # Device ID
                   node_addr[0],  # Address
                   node_addr[1],  # Address
                   node_addr[2],  # Address
                   COMMAND['WRITE_EEPROM'],  # Command
                   len(eeprom_data),  # Size of data to write
                   eeprom_addr]  # Start EEPROM address, where write
        request.append(self._checksum(request[1:]))  # Checksum of command
        request += eeprom_data
        request.append(self._checksum(eeprom_data))  # Checksum of data

        return bytes(request)

    def _check_response(self,
                        request: Union[bytes, list, tuple],
                        response: Union[bytes, list, tuple],
                        expected_response_length):
        if not isinstance(response, (bytes, list, tuple)):
            raise ResponseError(response)
        if not all((isinstance(x, int) and 0x00 <= x <= 0xFF) for x in response):
            raise ResponseError(response)

        response_cmd = response[:len(request)]
        response_data = response[len(request):]

        if len(response) != expected_response_length:
            # TODO: возможно ли другая причина исключения кроме времени?
            raise ResponseError(response,
                                f'Time is over! No enough data were getting! '
                                f'Response length is {len(response)}, but '
                                f'should be {expected_response_length}.')

        # Check command part
        if self._checksum(response_cmd[:-1]) != response_cmd[-1] \
                or response[4] != COMMAND['RESPONSE'] \
                or response[:4] != request[:4] \
                or response_cmd[5:-1] != request[5:-1]:
            raise ResponseError(response, f'Response command part failed!')

        # Check data part
        if self._checksum(response_data[:-1]) != response_data[-1]:
            raise ResponseError(response,
                                f'Data checksum failed! Data checksum is '
                                f'{hex_repr(response_data[-1])}, but should be '
                                f'{hex_repr(self._checksum(response_data[:-1]))}.')

    def send_cmd(self,
                 node_addr: Union[bytes, list, tuple],
                 procedure: int) -> bool:
        """Send command to node.

        Parameters
        ----------
        node_addr : Union[bytes, list, tuple]
            Target node address to which send command. It should be 3 bytes or
            3 int (list or tuple).
        procedure : int
            It should be one of the PROCEDURE constant: ``SWITCH_ON``,
            ``STEP_UP``, ``SWITCH_INVERSION``, ``SWITCH_OFF``, ``STEP_DOWN``,
            ``GLOBAL_ON``, ``GLOBAL_OFF``, ``SET_MODE``, ``RESET_MODE`` and etc.

        Returns
        -------
        bool
            True if command was successfully sent, False otherwise.

        Examples
        --------
        >>> self.send_cmd(node_addr=b'\x12\x23\x34', procedure=0x02)
        True
        """

        _LOGGER.debug(f'Calling send_cmd() with Args: {{'
                      f'\'node_addr\': {hex_repr(node_addr)}, '
                      f'\'procedure\': {hex_repr(procedure)}}}')

        try:
            request = self._request_cmd(node_addr=node_addr,
                                        procedure=procedure)
        except (NodeAddrError, ProcedureError) as ex:
            _LOGGER.exception(f'Invalid input parameters: {ex}')
            raise

        _LOGGER.debug(f'Request: {hex_repr(request)}')

        # controller_is_blocked = True
        # time_to_wait = self.__unlock_timeout

        with self.__threading_lock, self.__multiprocessing_lock:
        # with self.__lock:
            # ==================== RADIO CONTROLLER START ====================
            if not self._controller.is_open:
                _LOGGER.info('Open serial port')
                self._controller.open()
            else:
                _LOGGER.info('Serial port is already opened')

            # No write to UART to wait for packet boundary
            # time_now = time()
            # sleep(UART_INTERVAL - (time_now - self.__last_uart) if time_now - self.__last_uart < UART_INTERVAL else 0.0)

            # Wait while radiocontroller is busy
            # while self.__is_busy:
            #     pass
            # self.__is_busy = True

            # ----- COMMUNICATION START -----
            # Send request
            self._controller.reset_input_buffer()
            self._controller.reset_output_buffer()

            # try:
            #     request_length = self._controller.write(request)
            #     self._controller.flush()
            # except SerialException as ex:
            #     _LOGGER.exception(f'Error while sending request: {ex}')
            #     raise
            # else:
            #     # Check that all bytes were sent
            #     if request_length != len(request):
            #         raise RequestLengthError(request_length, len(request))

            try:
                request_length = self._controller.write(request)
                self._controller.flush()
            except SerialException as ex:
                _LOGGER.exception(f'Error while sending request: {ex}')
                raise
            else:
                # Check that all bytes were sent
                if request_length != len(request):
                    raise RequestLengthError(request_length, len(request))
            finally:
                self.__last_uart = time()
            # ----- COMMUNICATION END -----

            if self.__block:
                sleep(0.3)

            sleep(0.08)
            while self._controller.out_waiting != 0:
                pass
            # self.__is_busy = False

        return True

    def read(self,
             node_addr: Union[bytes, list, tuple],
             eeprom_addr: int,
             data_size: int) -> bytes:
        """
        Read data from Node EEPROM
        Node's examples: relay, dimmer, motor, thermoregulator

        Parameters
        ----------
        node_addr
        eeprom_addr
        data_size

        Returns
        -------

        """

        _LOGGER.debug(f'Calling read() with Args:'
                      f'\'node_addr\': {hex_repr(node_addr)}, '
                      f'\'eeprom_addr\': {hex_repr(eeprom_addr)}, '
                      f'\'data_size\': {hex_repr(data_size)}')

        try:
            self._node_addr = node_addr
            self._data_length = data_size
            self._eeprom_addr = eeprom_addr
        except (NodeAddrError, DataLengthError, EEPROMAddrError) as ex:
            _LOGGER.exception(f'Invalid input parameters: {ex}')
            raise ex

        request, expected_response_length = self._request_read(node_addr=self._node_addr,
                                                               data_length=self._data_length,
                                                               eeprom_addr=self._eeprom_addr)

        _LOGGER.debug(f'Request: {hex_repr(request)}')

        with self.__threading_lock, self.__multiprocessing_lock:
        # with self.__lock:
            # ==================== RADIO CONTROLLER START ====================
            if not self._controller.is_open:
                _LOGGER.info('Open serial port')
                self._controller.open()
            else:
                _LOGGER.info('Serial port is already opened')

            # No write to UART to wait for packet boundary
            # time_now = time()
            # sleep(UART_INTERVAL - (time_now - self.__last_uart) if time_now - self.__last_uart < UART_INTERVAL else 0.0)

            # ----- COMMUNICATION START -----
            # Send request
            self._controller.reset_input_buffer()
            self._controller.reset_output_buffer()

            try:
                request_length = self._controller.write(request)
                self._controller.flush()
            except SerialException as ex:
                _LOGGER.exception(f'Error while sending request: {ex}')
                raise
            else:
                # Check that all bytes were sent
                if request_length != len(request):
                    raise RequestLengthError(request_length, len(request))

            # Receive response
            try:
                time1 = time()
                response = self._controller.read(expected_response_length)
                self._controller.flush()
                time2 = time()
            except SerialException as ex:
                #     _LOGGER.exception(f'Unknown error in serial port while '
                #                       f'receiving response: {ex}')
                raise
            else:
                # Check that all bytes were received correctly
                self._check_response(request, response, expected_response_length)
            # ----- COMMUNICATION END -----

            if self.__block:
                sleep(0.1)

            # sleep(0.1)
            while self._controller.out_waiting != 0:
                pass
            # ==================== RADIO CONTROLLER END ======================

        _LOGGER.debug(f'Response transfer time: {time2 - time1} sec')
        _LOGGER.debug(f'Request length -> {request_length}. '
                      f'Response length -> {len(response)}.')
        _LOGGER.debug(f'EEPROM data: {hex_repr(response[request_length:-1])}')
        _LOGGER.debug(f'EEPROM data: {self._pretty_eeprom(response[request_length:-1])}')

        return response[request_length:-1]  # Last byte is check sum

    def write(self,
              node_addr: Union[bytes, list, tuple],
              eeprom_addr: int,
              data: Union[int, bytes, list, tuple]) -> bool:
        """
        Write data to Node EEPROM.
        Node's examples: relay, dimmer, motor, thermoregulator

        Parameters
        ----------
        node_addr
        eeprom_addr
        data

        Returns
        -------

        """

        _LOGGER.debug(f'Calling write() with Args:'
                      f'\'node_addr\': {hex_repr(node_addr)}, '
                      f'\'eeprom_addr\': {hex_repr(eeprom_addr)}, '
                      f'\'data\': {hex_repr(data)}')

        try:
            self._node_addr = node_addr
            self._eeprom_addr = eeprom_addr
            self._eeprom_data = data
        except (NodeAddrError, EEPROMAddrError, EEPROMDataError) as ex:
            _LOGGER.exception(f'Invalid input parameters: {ex}')
            raise ex

        request = self._request_write(node_addr=self._node_addr,
                                      eeprom_data=self._eeprom_data,
                                      eeprom_addr=self._eeprom_addr)

        _LOGGER.debug(f'Request: {hex_repr(request)}')

        with self.__threading_lock, self.__multiprocessing_lock:
        # with self.__lock:
            # ==================== RADIO CONTROLLER START ====================
            if not self._controller.is_open:
                _LOGGER.info('Open serial port')
                self._controller.open()
            else:
                _LOGGER.info('Serial port is already opened')

            # No write to UART to wait for packet boundary
            time_now = time()
            sleep(UART_INTERVAL - (time_now - self.__last_uart) if time_now - self.__last_uart < UART_INTERVAL else 0.0)

            # ----- COMMUNICATION START -----
            # Send request
            self._controller.reset_input_buffer()
            self._controller.reset_output_buffer()

            # try:
            #     request_length = self._controller.write(request)
            #     self._controller.flush()
            # except SerialException as ex:
            #     _LOGGER.exception(f'Error while sending request: {ex}')
            #     raise
            # else:
            #     # Check that all bytes were sent
            #     if request_length != len(request):
            #         raise RequestLengthError(request_length, len(request))

            try:
                request_length = self._controller.write(request)
                self._controller.flush()
            except SerialException as ex:
                _LOGGER.exception(f'Error while sending request: {ex}')
                raise
            else:
                # Check that all bytes were sent
                if request_length != len(request):
                    raise RequestLengthError(request_length, len(request))
            finally:
                self.__last_uart = time()
            # ----- COMMUNICATION END -----

            if self.__block:
                expected_block_time = 0.3 + request_length / 280
                sleep(expected_block_time)

            sleep(0.08)
            while self._controller.out_waiting != 0:
                pass
            # ==================== RADIO CONTROLLER END ======================

        return True
