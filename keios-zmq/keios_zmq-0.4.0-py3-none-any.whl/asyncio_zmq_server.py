import asyncio
from asyncio import Queue

import aiozmq
import zmq

from keios_zmq.log_provider import LogProvider
from keios_zmq.zmq_server import ZMQServer, ZMQMessage


class AsyncioKeiosZMQ(ZMQServer):
    log = LogProvider.get_logger("asyncio-keios-zmq-server")

    def __init__(self, port, handler):
        self._port = port
        self._handler = handler

    async def start(self, loop):
        task_queue = Queue()
        router = await aiozmq.create_zmq_stream(zmq.ROUTER, bind="tcp://*:{}".format(self._port))
        loop.create_task(self._inbound_task(loop, router, task_queue))
        loop.create_task(self._outbound_task(router, task_queue))

    async def _outbound_task(self, router, q: Queue):
        while True:
            item = await q.get()
            q.task_done()

            if item.done():
                self.log.debug("item is processed, sending response.")
                msg = item.result()
                router.write([msg.identifier, msg.msg])
            else:
                # put back on the queue if not done processing
                await asyncio.sleep(0.001)
                await q.put(item)

    async def _inbound_task(self, loop, router, q: Queue):
        while True:
            addr, msg = await router.read()
            task = asyncio.create_task(self.process(loop, ZMQMessage(addr, msg)))
            await q.put(task)
            self.log.info("task put on queue")

    async def process(self, loop, msg: ZMQMessage):
        self.log.debug("processing message")
        result = await loop.run_in_executor(None, self._handler, msg.msg)
        self.log.debug("done processing")
        return ZMQMessage(msg.identifier, result)

    def start_server(self):
        self.log.info("starting asyncio-keios-zmq-server on port %d", self._port)
        loop = asyncio.get_event_loop()
        loop.create_task(self.start(loop))
        loop.run_forever()

    def close(self):
        pass
