from concurrent.futures.thread import ThreadPoolExecutor
from queue import Queue
from typing import Callable

import zmq

from keios_zmq.log_provider import LogProvider
from keios_zmq.zmq_server import ZMQMessage, ZMQServer


class PoolKeiosZMQ(ZMQServer):
    """
    threadpool based server wrapper for keios implementations
    """
    log = LogProvider.get_logger("keios-py-zmq-connector")

    def __init__(self, port: int, message_handler: Callable[[bytearray], bytearray]):
        self._zmq_context = zmq.Context.instance()
        self._socket = self._zmq_context.socket(zmq.ROUTER)
        self._socket.bind("tcp://*:{}".format(port))
        self._socket.setsockopt(zmq.LINGER, 1)
        self._message_handler = message_handler
        self._stopped = False
        self._inbound_queue: Queue[ZMQMessage] = Queue()
        self._outbound_queue: Queue[ZMQMessage] = Queue()
        self._io_pool = ThreadPoolExecutor(max_workers=2)
        self._cb_pool = ThreadPoolExecutor(max_workers=10)

    def _initialize_pools(self):
        self._io_pool.submit(self._inbound_worker)
        self._io_pool.submit(self._outbound_worker)
        for i in range(10):
            self._cb_pool.submit(self._callback_worker)

    def _inbound_worker(self):
        """
        Polls the ZMQ socket for incoming messages and puts them onto the corresponding
        inbound queue to be handled by the callback workers.
        """
        self.log.debug("inbound_worker started")
        poller = zmq.Poller()
        poller.register(self._socket, 1)
        while not self._stopped:
            poll_items = dict(poller.poll())

            if self._socket in poll_items:
                addr, msg = self._socket.recv_multipart()
                self.log.debug("message received")
                self._inbound_queue.put(ZMQMessage(addr, msg))
                self.log.debug(f"inbound message put on inbound queue)")

    def _callback_worker(self):
        """
        Takes messages from the inbound queue, process them by calling the given self._message_handler and puts
        the result on the outbound queue.
        """
        self.log.debug("callback_worker started")
        while not self._stopped:
            work_item = self._inbound_queue.get()
            self._inbound_queue.task_done()
            self.log.debug("inbound message taken from inbound queue")
            try:
                self._outbound_queue.put(ZMQMessage(work_item.identifier, self._message_handler(work_item.msg)))
                self.log.debug("done processing")
            except Exception as e:
                self.log.exception("error during message_handler evaluation", e)

    def _outbound_worker(self):
        """
        Takes processed messages from the outbound queue and sends them back its origin denoted by zmq identifier
        """
        self.log.debug("outbound_worker started")
        while not self._stopped:
            to_send = self._outbound_queue.get()
            self._outbound_queue.task_done()
            self.log.debug("outbound message taken from outbound queue")
            try:
                self._socket.send_multipart([to_send.identifier, to_send.msg])
                self.log.debug("response sent")
            except Exception as e:
                self.log.exception("could not send response", e)

    def start_server(self):
        self._initialize_pools()
        self.log.info("pool-keios-zmq server started")

    def close(self):
        self._cb_pool.shutdown()
        self._io_pool.shutdown()
        self._stopped = True
        self._socket.close()
        self._zmq_context.term()
