#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""the actual control peer"""

import asyncio

from ujotypes import UjoStringC

from titanfe import log as logging
from titanfe.classes import Packet
from titanfe.connection import Connection
from titanfe.constants import FlowState

from .webapi.app import WebApi
from .flow import parse_flows
from .runner import BrickRunner

log = logging.getLogger(__name__)


class ControlPeer:
    """The control peer application will start runners as required for the flows/bricks
       as described in the given config file. Once the runners have registered themselves,
       they will get according assignments.

    Arguments:
        config_file (Path): path to the flow config yaml
        kafka_bootstrap_servers (str):
            'host[:port]' string (or list of 'host[:port]' strings)
            to contact the Kafka bootstrap servers on
    """

    def __init__(self, config_file, kafka_bootstrap_servers):
        self.loop = asyncio.get_event_loop()
        self.kafka_bootstrap_servers = kafka_bootstrap_servers

        self.flows = parse_flows(config_file)
        self.runners = {}
        self.runners_by_brick = {}

        self.server = None
        self.server_address = None
        self.webapi = None

    async def run(self):
        """run the application"""
        log.debug("running control peer")
        await self.setup_runner_communication()
        self.setup_webapi()
        self.start_flows()
        async with self.server:
            await self.server.serve_forever()

    async def setup_runner_communication(self):
        """create a server to communicate with brick runners"""
        log.debug("create server")
        self.server = await asyncio.start_server(self.communicate, "127.0.0.1", 8888)
        self.server_address = self.server.sockets[0].getsockname()

    def setup_webapi(self):
        self.webapi = WebApi(self)
        self.webapi.run()

    def start_flows(self):
        for flow in self.flows:
            self.start_flow(flow)

    def start_flow(self, flow):
        """start brick runners for each brick in the flow"""
        log.debug("start flow: %s", flow.name)
        flow.state = FlowState.Active
        for source, destination in flow.connections.items():
            runner = BrickRunner(self.server_address, self.kafka_bootstrap_servers).start()
            runner.brick = source
            runner.destination = destination
            if flow.inlet == source:
                runner.has_inlet = True

            self.runners[runner.uid] = runner
            self.runners_by_brick[source] = runner
            log.debug("started runner: %s", runner)

    async def runner_available(self, brick) -> BrickRunner:
        """waits until the runner for the given brick has registered its listener address"""
        runner = self.runners_by_brick[brick]
        while not runner.input_address:
            await asyncio.sleep(0.0001)
        return runner

    @staticmethod
    async def trigger_inlet(runner):
        """trigger the processing at the inlet runner by sending a signal packet"""
        connection = await Connection.open(runner.input_address)
        log.info("Trigger inlet on %s", runner)
        await connection.send(Packet(UjoStringC("TRIGGER INLET")).to_dict())

    async def communicate(self, reader, writer):
        """communicate with brick runners: handle registration and send assignment"""
        runner_connection = Connection(reader, writer)

        runner_registration = await runner_connection.receive()
        _, runner_uid, runner_address = runner_registration
        runner = self.runners.get(runner_uid)
        if not runner:
            log.error("No runner found for id: %s", runner_uid)
            log.debug("Available brick runner: %r", self.runners)
            return

        runner.input_address = runner_address
        runner.send = runner_connection.send
        runner.receive = runner_connection.receive

        log.info("Registration completed for runner: %s", runner)

        await runner.receive()
        output_target = None
        if runner.destination:
            output_to_runner = await self.runner_available(runner.destination)
            output_target = (output_to_runner.brick.name, output_to_runner.input_address)

        assignment = ("ASSIGNMENT", runner.brick.to_dict(), output_target)
        log.info("Assign runner: %r", assignment)
        await runner.send(assignment)

        if runner.has_inlet:
            asyncio.create_task(self.trigger_inlet(runner))

        while True:
            # for now there should not be coming much...
            # TODO: should we close the connection?
            msg = await runner_connection.receive()
            log.info("Got a message: %r", msg)
