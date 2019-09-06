from typing import Callable

import zmq

from keios_zmq.log_provider import LogProvider
from keios_zmq.zmq_server import ZMQServer


class KeiosZMQ(ZMQServer):
    """
    Blocking KeiosZMQ server
    """
    log = LogProvider.get_logger("keios-zmq-server")

    def __init__(self, port: int, message_handler: Callable[[bytearray], bytearray]):
        self._port = port
        self._zmq_context = zmq.Context()
        self._socket = self._zmq_context.socket(zmq.ROUTER)
        self._socket.bind("tcp://*:{}".format(port))
        self._socket.setsockopt(zmq.LINGER, 1)
        self._message_handler = message_handler
        self.stopped = False

    def internal_handler(self):
        while not self.stopped:
            try:
                addr, msg = self.internal_receive_message()
                self.log.debug("msg received - identity: {}, data: {}".format(addr, msg))
                self.internal_send_message(addr, self._message_handler(msg))
            except zmq.error.ContextTerminated as e:
                pass  # this error is expected from .close()

    def internal_receive_message(self):
        """
        Wraps blocking zmq recv
        :return:
        """
        identity, data = self._socket.recv_multipart()
        return [identity, data]

    def internal_send_message(self, identity, message):
        return self._socket.send_multipart([identity,
                                            message])

    def start_server(self):
        self.log.info(f"blocking-zmq-server started on port: {self._port}")
        self.internal_handler()

    def close(self):
        self.stopped = True
        self._socket.close()
        self._zmq_context.term()
