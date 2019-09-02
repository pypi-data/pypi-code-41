#!/usr/bin/env python3

import logging
from typing import Union, Optional

# from delumowave.config.relay import (RELAY, BRIGHTNESS, STATE, DIMMING_STEP)
from delumowave.config.node import (NODE, STATE)
from delumowave.config.delumo import HARDWARE_TYPE
from delumowave.controller import (DelumoWaveController, hex_repr,
                                   NodeVersionError, NodeAddrError,
                                   RequestLengthError, ResponseError,
                                   RadioControllerBlocked, NotSupportedError)

_LOGGER = logging.getLogger(__name__)


class DelumoWaveNode:
    def __init__(self,
                 controller: DelumoWaveController,
                 node_addr: Union[bytes, list, tuple],
                 node_version: int = max(NODE, key=int)):
        _LOGGER.debug(f'DelumoWaveNode __init__() with Args: {{'
                      f'\'node_addr\': {hex_repr(node_addr)}, '
                      f'\'controller\': {controller}}}')

        self.controller = controller

        try:
            self._node_addr = node_addr
            self._node_version = node_version
        except (NodeAddrError, NodeVersionError) as ex:
            _LOGGER.exception(f'Invalid input parameters: {ex}')
            raise

        #: Node constants for appropriate firmware version
        self.NODE = NODE[self._node_version]

    @property
    def _node_version(self) -> int:
        return self.__node_version

    @_node_version.setter
    def _node_version(self, node_version: int):
        if not isinstance(node_version, int):
            raise NodeVersionError(node_version)
        elif not 0x00 <= node_version <= 0xFF:
            raise NodeVersionError(node_version)

        self.__node_version = node_version

    def switch(self) -> bool:
        """
        Switch node state (``ON`` - 0x55 or ``OFF`` - 0xFF)

        Returns
        -------
        bool
            True if the command to invert state of node was successfully sent, False otherwise.
        """

        _LOGGER.debug('Calling invert()')

        try:
            procedure = self.NODE['PROCEDURE']['SWITCH']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for {hex_repr(self._node_version)} node firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            return self.controller.send_cmd(node_addr=self._node_addr,
                                            procedure=procedure)
        except (RequestLengthError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            return False

    def global_on(self) -> bool:
        """
        Global on node
        """

        _LOGGER.debug('Global on')

        try:
            procedure = self.NODE['PROCEDURE']['GLOBAL_ON']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for {hex_repr(self._node_version)} node firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            return self.controller.send_cmd(node_addr=self._node_addr,
                                            procedure=procedure)
        except (RequestLengthError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            return False

    def global_off(self) -> bool:
        """
        Global off node
        """

        _LOGGER.debug('Global on')

        try:
            procedure = self.NODE['PROCEDURE']['GLOBAL_OFF']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for {hex_repr(self._node_version)} node firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            return self.controller.send_cmd(node_addr=self._node_addr,
                                            procedure=procedure)
        except (RequestLengthError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            return False

    def set_mode(self) -> bool:
        pass

    def reset_mode(self) -> bool:
        pass

    @property
    def hardware_type(self) -> Optional[str]:
        """
        Get node hardware type
        """

        _LOGGER.debug('Get hardware type')

        try:
            eeprom_addr = self.NODE['EEPROM']['HARDWARE_TYPE']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for {hex_repr(self._node_version)} node firmware version.'
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
            _LOGGER.debug(f'Unknown device! Could not identify the hardware type -> {hex_repr(hardware_type)}')
            raise

        return hardware_type

    @hardware_type.setter
    def hardware_type(self, hardware_type: str):
        """
        Set node hardware type
        """

        _LOGGER.debug(f'Set hardware type {hardware_type}')

        try:
            hardware_type_byte = HARDWARE_TYPE[hardware_type.strip().upper()]
        except KeyError:
            _LOGGER.debug(f'Could not identify the hardware_type -> {hardware_type}')
            raise

        try:
            eeprom_addr = self.NODE['EEPROM']['HARDWARE_TYPE']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for {hex_repr(self._node_version)} node firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            status = self.controller.write(node_addr=self._node_addr,
                                           eeprom_addr=eeprom_addr,
                                           data=hardware_type_byte)
        except (RequestLengthError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            raise

        _LOGGER.debug(f'Hardware type -> {hex_repr(hardware_type_byte)} {"OK!" if status else "Failed!"}')

    @property
    def firmware_version(self) -> Optional[int]:
        """
        Get node firmware version
        """
        # TODO: Реализовать, когда будет единый байт для всех устройств
        return

    @firmware_version.setter
    def firmware_version(self, firmware_version):
        """
        Set node firmware version
        """
        # TODO: Реализовать, когда будет единый байт для всех устройств
