from logging import Logger
from typing import Callable

from keios_zmq.asyncio_zmq_server import AsyncioKeiosZMQ
from keios_zmq.blocking_zmq_server import KeiosZMQ
from keios_zmq.log_provider import LogProvider
from keios_zmq.pool_zmq_server import PoolKeiosZMQ
from keios_zmq.zmq_async import AsyncKeiosZMQServer
from keios_zmq.zmq_server import ZMQServer


class KeiosZMQFactory:
    @staticmethod
    def get_server(name: str, handler: Callable[[bytearray], bytearray], port=8075) -> ZMQServer:
        log: Logger = LogProvider.get_logger(__name__)
        """
        :param name:
        :param handler:
        :param port:
        :return: a keios zmq server depending on the given name. Defaults to blocking keios zmq server
        """
        if name == "blocking":
            return KeiosZMQ(port, handler)
        if name == "pool":
            return PoolKeiosZMQ(port, handler)
        if name == "asyncio":
            return AsyncioKeiosZMQ(port, handler)
        log.warning(f"'{name}' is not a valid KeiosZMQ server implementation. Using blocking.")
        return KeiosZMQ(port, handler)
