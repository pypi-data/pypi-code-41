#!/usr/bin/env python3

import logging
from typing import Union

from delumowave.config.cover import COVER
from delumowave.controller import (DelumoWaveController, hex_repr,
                                   NodeVersionError, NodeAddrError,
                                   RequestLengthError, RadioControllerBlocked,
                                   NotSupportedError)

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


class DelumoWaveCover:
    def __init__(self,
                 controller: DelumoWaveController,
                 node_addr: Union[bytes, list, tuple],
                 node_version: int = max(COVER, key=int)):
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

        _LOGGER.debug(f'DelumoWaveCover __init__() with Args: {{'
                      f'\'node_addr\': {hex_repr(node_addr)}, '
                      f'\'controller\': {controller}}}')

        self.controller = controller

        try:
            self._node_addr = node_addr
            self._node_version = node_version
        except (NodeAddrError, NodeVersionError) as ex:
            _LOGGER.exception(f'Invalid input parameters: {ex}')
            raise

        self.COVER = COVER[self._node_version]

    @debug_msg
    def stop(self) -> bool:
        try:
            procedure = self.COVER['PROCEDURE']['STOP']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} cover ' \
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
    def step_up(self) -> bool:
        try:
            procedure = self.COVER['PROCEDURE']['STEP_UP']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} cover ' \
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
    def step_down(self) -> bool:
        try:
            procedure = self.COVER['PROCEDURE']['STEP_DOWN']
        except KeyError as ex:
            error_msg = f'{ex} is not supported for ' \
                        f'{hex_repr(self._node_version)} cover ' \
                        f'firmware version.'
            _LOGGER.exception(error_msg)
            raise NotSupportedError(error_msg)

        try:
            return self.controller.send_cmd(node_addr=self._node_addr,
                                            procedure=procedure)
        except (RequestLengthError, RadioControllerBlocked) as ex:
            _LOGGER.error(f'Radio communications failure! {ex}')
            return False
