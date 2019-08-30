#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Encapsulate communication with the ControlPeer"""

from titanfe.connection import Connection


class ControlPeer:
    """The ControlPeer class encapsulates the connection and communication
       with the ControlPeer instance.

    Arguments:
        cp_address (NetworkAddress): the controlpeer's network address as (host, port)
        runner_uid (str): the runner's unique id
        runner_input_address (NetworkAdress): the runner's input address (host, port)
        log (logging.logger): the parent's logger instance
    """

    def __init__(self, cp_address, runner_uid, runner_input_address, log):
        self.log = log.getChild("ControlPeer")
        self.cp_address = cp_address

        self.runner_uid = runner_uid
        self.runner_listen_address = runner_input_address

        self.connection = None
        self.receive = None
        self.send = None

    async def connect(self):
        self.connection = await Connection.open(self.cp_address, self.log)
        self.receive, self.send = self.connection.receive, self.connection.send

    async def register(self):
        await self.connection.send(("REGISTER", self.runner_uid, self.runner_listen_address))

    async def request_assignment(self):
        """get an assignment from the controlpeer"""
        if not self.connection:
            await self.connect()
            await self.register()

        await self.send(("REQUEST ASSIGNMENT", self.runner_uid))
        assignment = await self.receive()
        return assignment

    async def alert_on_slow_queue(self):
        pass  # TODO
