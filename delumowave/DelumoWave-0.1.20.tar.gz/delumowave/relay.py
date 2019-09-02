#!/usr/bin/env python3

import logging
from typing import Union, Optional

from delumowave.config.delumo import HARDWARE_TYPE
from delumowave.config.relay import (RELAY, BRIGHTNESS, STATE, DIMMING_STEP)
from delumowave.controller import (DelumoWaveController, hex_repr,
                                   NodeVersionError, NodeAddrError,
                                   RequestLengthError, ResponseError,
                                   RadioControllerBlocked, NotSupportedError)

_LOGGER = logging.getLogger(__name__)


def debug_msg(func):
    def wrapper(*args, **kwargs):
        def args_to_str(x):
            if isinstance(x, bool):
                return f'{x}'
            elif isinstance(x, int):
                return f'0x{x:02X}'
            else:
                return f'{x}'

        args_str = ', '.join([args_to_str(x) for x in args[1:]])
        kwargs_str = ', '.join([f'{x}=' + args_to_str(y) for x, y in kwargs.items()])

        _LOGGER.debug(f'Invoke {func.__name__}(' + args_str + kwargs_str + ')')
        status = func(*args, **kwargs)
        _LOGGER.debug(f'Completion {func.__name__}(' + args_str + kwargs_str + ')')
        return status

    return wrapper


class DelumoWaveRelay:
    def __init__(self,
                 controller: DelumoWaveController,
                 node_addr: Union[bytes, list, tuple],
                 node_version: int = max(RELAY, key=int)):
        """
        This class provide methods to manage relay/dimmer.

        Parameters
        ----------
        node_addr : Union[bytes, list, tuple]
            Node address. Three latest meaningful bytes. For example:
            ``b'\\x12\\xA7\\xE4'``, ``[173, 34, 211]``, ``[0x7A, 0x19, 0xF0]``.
        node_version : int
            Node firmware version. One byte from 0x00 to 0xFF.
            By default, latest available firmware version.
        port_path : str, optional
            Device name: depending on operating system. e.g. ``/dev/ttyUSB0``,
            ``/dev/ttyAMA0`` on GNU/Linux or ``COM3`` on Windows.
            By default, ``/dev/ttyAMA0`` is used.
        unlock_timeout : float
        sleep_time : float
        block : float
        logging_level : Union[str, int, None], optional
            Available logging levels: ``DEBUG``, ``INFO``, ``WARNING``,
            ``ERROR``, ``CRITICAL``, ``NOTSET``. Also it could be written by
            numeric values.
            By default, logging is disabled.
        """

        _LOGGER.debug(f'DelumoWaveRelay __init__() with Args: {{'
                      f'\'node_addr\': {hex_repr(node_addr)}, '
                      f'\'controller\': {controller}}}')

        self.controller = controller

        try:
            self._node_addr = node_addr
            self._node_version = node_version
        except (NodeAddrError, NodeVersionError) as ex:
            _LOGGER.exception(f'Invalid input parameters: {ex}')
            raise

        #: Increase dimmer brightness by dimming step
        self.dim_up = self.relay_on
        #: Decreasing dimmer brightness by dimming step
        self.dim_down = self.relay_off
        #: Relay/dimmer constants for appropriate firmware version
        self.RELAY = RELAY[self._node_version]

    @debug_msg
    def invert(self) -> bool:
        """
        Invert state (``ON`` - 0x55 or ``OFF`` - 0xFF) of relay/dimmer

        Returns
        -------
        bool
            True if the command to invert state of relay/dimmer was
            successfully sent, False otherwise.
        """

        try:
            procedure = self.RELAY['PROCEDURE']['SWITCH_INVERSION']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            return self.controller.send_cmd(node_addr=self._node_addr,
                                            procedure=procedure)
        except (RequestLengthError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            return False

    @debug_msg
    def relay_on(self) -> bool:
        """
        Switch on relay/dimmer by executing command with procedure ``SWITCH_ON``

        Returns
        -------
        bool
            True if the command to switch on relay/dimmer was successfully sent,
            False otherwise.
        """

        try:
            procedure = self.RELAY['PROCEDURE']['SWITCH_ON']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            return self.controller.send_cmd(node_addr=self._node_addr,
                                            procedure=procedure)
        except (RequestLengthError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            return False

    @debug_msg
    def relay_off(self) -> bool:
        """
        Switch off relay/dimmer by executing command with procedure
        ``SWITCH_OFF``

        Returns
        -------
        bool
            True if the command to switch off relay/dimmer was successfully
            sent, False otherwise.
        """

        try:
            procedure = self.RELAY['PROCEDURE']['SWITCH_OFF']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            return self.controller.send_cmd(node_addr=self._node_addr,
                                            procedure=procedure)
        except (RequestLengthError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            return False

    @debug_msg
    def turn_on(self) -> bool:
        """
        Switch on dimmer by writing state to EEPROM
        """

        try:
            procedure = self.RELAY['PROCEDURE']['GLOBAL_ON']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            return self.controller.send_cmd(node_addr=self._node_addr,
                                            procedure=procedure)
        except (RequestLengthError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            return False

    @debug_msg
    def turn_off(self) -> bool:
        """
        Switch off dimmer by writing state to EEPROM
        """

        try:
            procedure = self.RELAY['PROCEDURE']['GLOBAL_OFF']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            return self.controller.send_cmd(node_addr=self._node_addr,
                                            procedure=procedure)
        except (RequestLengthError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            return False

    @property
    @debug_msg
    def time_to_turn_off(self) -> Optional[int]:
        """
        Get time to relay/dimmer off in hours
        """

        try:
            eeprom_addr = self.RELAY['EEPROM']['TIME_RELAY_OFF']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            time_to_relay_off = self.controller.read(node_addr=self._node_addr,
                                                     eeprom_addr=eeprom_addr,
                                                     data_size=0x01)[0]
        except (RequestLengthError, ResponseError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            raise

        _LOGGER.debug(f'Time to relay off -> {hex_repr(time_to_relay_off)}')

        return time_to_relay_off

    @time_to_turn_off.setter
    @debug_msg
    def time_to_turn_off(self, time_in_hours: int):
        """
        Set time to relay/dimmer off in hours
        """

        try:
            eeprom_addr = self.RELAY['EEPROM']['TIME_RELAY_OFF']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            status = self.controller.write(node_addr=self._node_addr,
                                           eeprom_addr=eeprom_addr,
                                           data=time_in_hours)
        except (RequestLengthError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            raise

        _LOGGER.debug(f'Time to relay off -> {hex_repr(time_in_hours)}.'
                      f' {"OK!" if status else "Failed!"}')

    @property
    @debug_msg
    def hardware_type(self) -> Optional[str]:
        """
        Get hardware type of node (relay or dimmer)
        """

        try:
            eeprom_addr = self.RELAY['EEPROM']['HARDWARE_TYPE']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            hardware_type = self.controller.read(node_addr=self._node_addr,
                                                 eeprom_addr=eeprom_addr,
                                                 data_size=0x01)[0]
        except (RequestLengthError, ResponseError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            raise

        _LOGGER.debug(f'Hardware type -> {hex_repr(hardware_type)}')

        try:
            hardware_type = next((x for x, y in HARDWARE_TYPE.items() if y == hardware_type), None)
            _LOGGER.debug(f'Device -> {hardware_type}')
        except KeyError:
            _LOGGER.debug(f'Unknown device! Could not identify the hardware '
                          f'type -> {hex_repr(hardware_type)}')
            raise

        return hardware_type

    @hardware_type.setter
    @debug_msg
    def hardware_type(self, hardware_type: str):
        """
        Set hardware type of node (relay or dimmer)
        """

        try:
            hardware_type_byte = HARDWARE_TYPE[hardware_type.strip().upper()]
        except KeyError:
            _LOGGER.debug(f'Could not identify the hardware_type -> '
                          f'{hardware_type}')
            raise

        try:
            eeprom_addr = self.RELAY['EEPROM']['HARDWARE_TYPE']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            status = self.controller.write(node_addr=self._node_addr,
                                           eeprom_addr=eeprom_addr,
                                           data=hardware_type_byte)
        except (RequestLengthError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            raise

        _LOGGER.debug(f'Hardware type -> {hex_repr(hardware_type_byte)}'
                      f' {"OK!" if status else "Failed!"}')

    @property
    @debug_msg
    def firmware_version(self) -> Optional[int]:
        """
        Get firmware version of node
        """

        try:
            eeprom_addr = self.RELAY['EEPROM']['FIRMWARE_VERSION']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            firmware_version = self.controller.read(node_addr=self._node_addr,
                                                    eeprom_addr=eeprom_addr,
                                                    data_size=0x01)[0]
        except (RequestLengthError, ResponseError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            raise

        _LOGGER.debug(f'Relay firmware version -> {hex_repr(firmware_version)}')

        return firmware_version

    @firmware_version.setter
    @debug_msg
    def firmware_version(self, firmware_version):
        """
        Set firmware version of node
        """

        try:
            eeprom_addr = self.RELAY['EEPROM']['FIRMWARE_VERSION']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            status = self.controller.write(node_addr=self._node_addr,
                                           eeprom_addr=eeprom_addr,
                                           data=firmware_version)
        except (RequestLengthError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            raise

        _LOGGER.debug(f'Relay firmware version -> {hex_repr(firmware_version)}'
                      f' {"OK!" if status else "Failed!"}')

    @property
    @debug_msg
    def state(self) -> Optional[bool]:
        """
        Get state of node - on (0x55) or off (0xFF)
        """

        try:
            eeprom_addr = self.RELAY['EEPROM']['STATE']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            state_byte = self.controller.read(node_addr=self._node_addr,
                                              eeprom_addr=eeprom_addr,
                                              data_size=0x01)[0]
        except (RequestLengthError, ResponseError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            raise

        _LOGGER.debug(f'Relay state -> {hex_repr(state_byte)}')

        try:
            state = next((x for x, y in STATE.items() if y == state_byte), None)
            _LOGGER.debug(f'Relay state -> {state}')
        except KeyError:
            _LOGGER.debug(f'Could not identify the state -> '
                          f'{hex_repr(state_byte)}')
            raise

        return state

    @state.setter
    @debug_msg
    def state(self, state: bool):
        """
        Set state of node - ON (0x55) or OFF (0xFF)
        """

        try:
            state_byte = STATE[state]
        except KeyError:
            _LOGGER.debug(f'Could not identify the state -> {state}')
            raise

        try:
            eeprom_addr = self.RELAY['EEPROM']['STATE']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            status = self.controller.write(node_addr=self._node_addr,
                                           eeprom_addr=eeprom_addr,
                                           data=state_byte)
        except (RequestLengthError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            raise

        _LOGGER.debug(f'Relay state -> {state} ({state_byte})'
                      f' {"OK!" if status else "Failed!"}')

    @property
    @debug_msg
    def brightness_level(self) -> Optional[int]:
        """
        Get brightness level of dimmer
        """

        try:
            eeprom_addr = self.RELAY['EEPROM']['BRIGHTNESS_LEVEL']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            brightness_level = self.controller.read(node_addr=self._node_addr,
                                                    eeprom_addr=eeprom_addr,
                                                    data_size=0x01)[0]
        except (RequestLengthError, ResponseError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            raise

        _LOGGER.debug(f'Relay brightness level -> {hex_repr(brightness_level)}')

        return brightness_level

    @brightness_level.setter
    @debug_msg
    def brightness_level(self, brightness_level: int):
        """
        Set brightness level of dimmer
        """

        if brightness_level > BRIGHTNESS['MAX']:
            brightness_level = BRIGHTNESS['MAX']
        if brightness_level < BRIGHTNESS['MIN']:
            brightness_level = BRIGHTNESS['MIN']

        try:
            eeprom_addr = self.RELAY['EEPROM']['BRIGHTNESS_LEVEL']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            status = self.controller.write(node_addr=self._node_addr,
                                           eeprom_addr=eeprom_addr,
                                           data=brightness_level)
        except (RequestLengthError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            raise

        _LOGGER.debug(f'Relay brightness level -> {hex_repr(brightness_level)}'
                      f' {"OK!" if status else "Failed!"}')

    @property
    @debug_msg
    def brightness_level_comfort(self) -> Optional[int]:
        """
        Get brightness level comfort of dimmer
        """

        try:
            eeprom_addr = self.RELAY['EEPROM']['BRIGHTNESS_LEVEL_COMFORT']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            brightness_level_comfort = self.controller.read(node_addr=self._node_addr,
                                                            eeprom_addr=eeprom_addr,
                                                            data_size=0x01)[0]
        except (RequestLengthError, ResponseError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            raise

        _LOGGER.debug(f'Relay brightness level comfort -> '
                      f'{hex_repr(brightness_level_comfort)}')

        return brightness_level_comfort

    @brightness_level_comfort.setter
    @debug_msg
    def brightness_level_comfort(self, brightness_level_comfort: int):
        """
        Set brightness level comfort of dimmer
        """

        if brightness_level_comfort > BRIGHTNESS['MAX']:
            brightness_level_comfort = BRIGHTNESS['MAX']
        if brightness_level_comfort < BRIGHTNESS['MIN']:
            brightness_level_comfort = BRIGHTNESS['MIN']

        try:
            eeprom_addr = self.RELAY['EEPROM']['BRIGHTNESS_LEVEL_COMFORT']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            status = self.controller.write(node_addr=self._node_addr,
                                           eeprom_addr=eeprom_addr,
                                           data=brightness_level_comfort)
        except (RequestLengthError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            raise

        _LOGGER.debug(f'Relay brightness level comfort -> '
                      f'{hex_repr(brightness_level_comfort)}'
                      f' {"OK!" if status else "Failed!"}')

    @property
    @debug_msg
    def dimming_speed(self) -> Optional[int]:
        """
        Get dimming speed
        """

        try:
            eeprom_addr = self.RELAY['EEPROM']['DIMMING_SPEED']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            dimming_speed = self.controller.read(node_addr=self._node_addr,
                                                 eeprom_addr=eeprom_addr,
                                                 data_size=0x01)[0]
        except (RequestLengthError, ResponseError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            raise

        _LOGGER.debug(f'Relay dimming speed -> {hex_repr(dimming_speed)}')

        return dimming_speed

    @dimming_speed.setter
    @debug_msg
    def dimming_speed(self, dimming_speed: int):
        """
        Set dimming speed
        """

        try:
            eeprom_addr = self.RELAY['EEPROM']['DIMMING_SPEED']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            status = self.controller.write(node_addr=self._node_addr,
                                           eeprom_addr=eeprom_addr,
                                           data=dimming_speed)
        except (RequestLengthError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            raise

        _LOGGER.debug(f'Relay dimming speed -> {hex_repr(dimming_speed)}'
                      f' {"OK!" if status else "Failed!"}')

    @property
    @debug_msg
    def dimming_step(self) -> Optional[int]:
        """
        Get dimming step
        """

        try:
            eeprom_addr = self.RELAY['EEPROM']['DIMMING_STEP']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            dimming_step = self.controller.read(node_addr=self._node_addr,
                                                eeprom_addr=eeprom_addr,
                                                data_size=0x01)[0]
        except (RequestLengthError, ResponseError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            raise

        _LOGGER.debug(f'Relay dimming step -> {hex_repr(dimming_step)}')

        return dimming_step

    @dimming_step.setter
    @debug_msg
    def dimming_step(self, dimming_step: int):
        """
        Set dimming step
        """

        if dimming_step > DIMMING_STEP['MAX']:
            dimming_step = DIMMING_STEP['MAX']
        if dimming_step < DIMMING_STEP['MIN']:
            dimming_step = DIMMING_STEP['MIN']

        try:
            eeprom_addr = self.RELAY['EEPROM']['DIMMING_STEP']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            status = self.controller.write(node_addr=self._node_addr,
                                           eeprom_addr=eeprom_addr,
                                           data=dimming_step)
        except (RequestLengthError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            raise

        _LOGGER.debug(f'Relay dimming step -> {hex_repr(dimming_step)}'
                      f' {"OK!" if status else "Failed!"}')

    @debug_msg
    def get_state_and_brightness_level(self):

        try:
            eeprom_addr = self.RELAY['EEPROM']['STATE']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            state_and_brightness_level = self.controller.read(node_addr=self._node_addr,
                                                              eeprom_addr=eeprom_addr,
                                                              data_size=0x02)
        except (RequestLengthError, ResponseError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            raise

        state_byte = state_and_brightness_level[0]
        brightness_level = state_and_brightness_level[1]

        try:
            state = next((x for x, y in STATE.items() if y == state_byte), None)
            _LOGGER.debug(f'Relay state -> {state}')
        except KeyError:
            _LOGGER.debug(f'Could not identify the state -> '
                          f'{hex_repr(state_byte)}')
            raise

        _LOGGER.debug(f'Relay brightness level -> {hex_repr(brightness_level)}')

        return state, brightness_level

    @debug_msg
    def set_state_and_brightness_level(self, state: bool, brightness_level: int):

        try:
            state_byte = STATE[state]
        except KeyError:
            _LOGGER.debug(f'Could not identify the state -> {state}')
            raise

        if brightness_level > BRIGHTNESS['MAX']:
            brightness_level = BRIGHTNESS['MAX']
        if brightness_level < BRIGHTNESS['MIN']:
            brightness_level = BRIGHTNESS['MIN']

        try:
            eeprom_addr = self.RELAY['EEPROM']['STATE']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} relay/dimmer ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            status = self.controller.write(node_addr=self._node_addr,
                                           eeprom_addr=eeprom_addr,
                                           data=[state_byte, brightness_level])
        except (RequestLengthError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            raise

        _LOGGER.debug(f'Relay state -> {state} ({state_byte})'
                      f' {"OK!" if status else "Failed!"}. '
                      f'Relay brightness level -> {hex_repr(brightness_level)}'
                      f' {"OK!" if status else "Failed!"}')
