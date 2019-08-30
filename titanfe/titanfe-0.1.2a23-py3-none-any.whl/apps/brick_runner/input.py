#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""The INPUT side of a brick (runner)"""

import asyncio

from titanfe.classes import Packet
from titanfe.connection import Connection
from titanfe.utils import get_ip_address


class Input:
    """The Input side of a brick runner has a listener to which the output of another brick can
       connect. The Input will then request new packets until it's QueueLimit is exceeded and again
       once the "low level" is reached.
       The Input will also emit queue metrics every 0.1 sec if there are packets in the queue.

    Arguments:
        runner (BrickRunner): instance of a parent brick runner
    """

    def __init__(self, runner):
        self.name = "Input"  # todo: differentiate on multiple Inputs
        self.runner = runner
        self.log = runner.log.getChild("Input")

        self.packets = asyncio.Queue()
        self.batch_size = 25
        self.low_queue_level = 10
        # TODO: Adjust batchsize/lowlevel dynamically
        # based on how long items are queued/take to process?

        self.metric_emitter = runner.metric_emitter

        self.server = None
        self.server_address = None
        self.server_task = None
        self.metrics_task = None

    @classmethod
    async def create(cls, runner) -> "Input":
        """Creates a new instance and starts it's listener- and metrics-tasks"""
        input = cls(runner)  # pylint: disable=redefined-builtin
        await input.start()
        return input

    async def start(self):
        """start serving and schedule emits of queue metrics"""
        self.server = await asyncio.start_server(self.receive_input, host=get_ip_address())
        self.server_address = self.server.sockets[0].getsockname()
        self.metrics_task = asyncio.create_task(self.emit_queue_metrics())
        self.server_task = asyncio.create_task(self.server.serve_forever())

    async def receive_input(self, reader, writer):
        """get packets on a connection from another brick runner's output"""
        connection = Connection(reader, writer, self.log)

        while True:
            await asyncio.sleep(0)  # be cooperative
            await self.low_queue_level_reached()
            await connection.send(("SEND", self.batch_size))
            for _ in range(self.batch_size):
                packet = await connection.receive()
                packet = Packet.from_dict(packet)
                packet.update_input_entry()
                await self.packets.put(packet)

    async def low_queue_level_reached(self) -> True:
        """awaitable that returns True as soon as the queue level is 'low'"""
        while self.packets.qsize() > self.low_queue_level:
            await asyncio.sleep(0.0001)
        return True

    async def emit_queue_metrics(self):
        """endless coroutine to emit queue metrics every 100 ms if the queue ain't empty
        to be scheduled as task and cancelled when no longer required"""
        while not self.runner.brick:
            # await assignment
            await asyncio.sleep(0.001)

        while True:
            queue_length = self.packets.qsize()
            if queue_length:
                await self.metric_emitter.emit_for_queue(self.runner, self.name, queue_length)
            await asyncio.sleep(0.1)

    def __aiter__(self):
        return self

    async def __anext__(self) -> Packet:
        """awaitable to get the next available packet from the input queue"""
        packet = await self.packets.get()

        # TODO:
        # reconsider when/where to put "task done", might wanna wrap it in a
        # class method instead and set from outside after actually finishing an item
        self.packets.task_done()

        packet.update_input_exit()
        return packet
