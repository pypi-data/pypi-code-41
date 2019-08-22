#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""The actual brick runner"""

import asyncio
import pathlib
import time

import janus

import titanfe.log as logging
from titanfe.apps.brick_runner.adapter import BrickAdapter
from titanfe.apps.brick_runner.controlpeer import ControlPeer
from titanfe.apps.brick_runner.input import Input
from titanfe.apps.brick_runner.metrics import MetricEmitter
from titanfe.apps.brick_runner.output import Output
from titanfe.classes import Packet, Brick
from titanfe.utils import get_module, time_delta_in_ms


class BrickRunner:
    """The BrickRunner will create an Input, get an Assignment from the control peer,
       create corresponding outputs and then start processing packets from the input.

    Arguments:
        uid (str): a unique id for the runner
        controlpeer_address (NetworkAddress): (host, port) of the control peer's server
        kafka_bootstrap_servers (str):
            'host[:port]' string (or list of 'host[:port]' strings)
            to contact the Kafka bootstrap servers on
    """

    def __init__(self, uid, controlpeer_address, kafka_bootstrap_servers):
        self.uid = uid
        self.log = logging.getLogger(f"{__name__}.{self.uid}")
        self.loop = asyncio.get_event_loop()
        self.kafka_bootstrap_servers = kafka_bootstrap_servers

        cp_host, cp_port = controlpeer_address.rsplit(":", 1)
        self.cp_address = cp_host, int(cp_port)

        self.brick_push_queue = janus.Queue()

        # done async in setup
        self.input, self.outputs = None, None
        self.control_peer = None
        self.brick = None
        self.brick_module = None
        self.metric_emitter = None
        self.brick_execution_start = None

    async def setup(self):
        """does the inital setup parts that have to be awaited (because of asyncio)"""
        self.metric_emitter = await MetricEmitter.create(self.kafka_bootstrap_servers, self.log)
        self.input = await Input.create(self)

        self.control_peer = ControlPeer(
            self.cp_address, self.uid, self.input.server_address, self.log
        )

        self.brick, self.outputs = await self.get_assignment()
        self.brick_module = get_module(pathlib.Path(self.brick.module))

        asyncio.create_task(self.process_pushed_results())

    @classmethod
    async def create(cls, uid, controlpeer_address, kafka_bootstrap_servers):
        """Creates a brick runner instance and does the initial setup phase before returning it"""
        br = cls(uid, controlpeer_address, kafka_bootstrap_servers)  # pylint: disable=invalid-name
        await br.setup()
        return br

    async def run(self):
        """process items from the input"""
        self.log.info("start runner: %s", self.uid)
        async for packet in self.input:
            packet = await self.execute_brick(packet)
            if packet:
                await self.queue_for_output(packet)

    @property
    def execution_time(self):
        return time_delta_in_ms(self.brick_execution_start)

    async def get_assignment(self):
        """get an assignment from the control peer"""
        assignment = await self.control_peer.request_assignment()
        self.log.info("received assignment: %r", assignment)

        _, brick, output_destination = assignment

        brick = Brick.from_dict(brick)

        if output_destination:
            name, address = output_destination
            output = await Output.create(self, name, address)
            return brick, [output]

        return brick, []

    async def queue_for_output(self, packet):
        """add packet to the output queues"""
        for output in self.outputs:
            await output.add(packet)

    async def execute_brick(self, packet):
        """run the brick module for the given packet in a separate thread

        Returns:
            Packet: the result as payload wrapped in a Packet
        """
        self.brick_execution_start = time.time_ns()
        result = await self.loop.run_in_executor(None, self.execute_brick_module, packet)

        # wait for potentially pushed result to be queued for output to keep the order intact
        await self.brick_push_queue.async_q.join()

        await self.metric_emitter.emit_for_packet(self, packet, self.execution_time)
        await self.metric_emitter.emit_for_brick(self, self.execution_time)

        if not result:
            return None

        if packet.payload == "TRIGGER INLET":
            # TODO: find a better way?
            packet = Packet(result)
        else:
            packet.payload = result

        return packet

    def execute_brick_module(self, packet):
        """do the actual execution of the brick module and return it's result"""
        self.log.info(
            "execute brick: [%s](%s){%s} for packet %s with input: %r",
            self.brick.flow, self.brick_module.__name__, self.brick.uid,
            packet.uid, packet.payload,
        )

        adapter = BrickAdapter(self.brick.name, self.brick_push_queue.sync_q.put, self.log)
        try:
            brick_parameter = None
            result = self.brick_module.do_brick_processing(adapter, brick_parameter, packet.payload)
            return result
        except Exception:  # pylint: disable=broad-except
            self.log.error("brick execution failed", exc_info=True)
            return None

    async def process_pushed_results(self):
        """get results emitted during the brick execution, wrap them in packets and
           add them to the output queues of this runner until the queue is closed and empty."""
        while not (self.brick_push_queue.closed and self.brick_push_queue.async_q.empty()):
            # probably blocks on a full push_queue? should we:
            # await asyncio.sleep(0)
            result = await self.brick_push_queue.async_q.get()
            packet = Packet(result)

            await self.metric_emitter.emit_for_packet(self, packet, self.execution_time)

            await self.queue_for_output(packet)
            self.brick_push_queue.async_q.task_done()
