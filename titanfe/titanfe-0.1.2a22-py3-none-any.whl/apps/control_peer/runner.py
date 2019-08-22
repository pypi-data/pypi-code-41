#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Encapsulate brick runner related things"""

import subprocess
import sys

import titanfe.log as logging
from titanfe.utils import create_uid

log = logging.getLogger(__name__)


class BrickRunner:
    """The BrickRunner can be used to start brick runner processes and hold corresponding data

    Arguments:
        controlpeer_address (NetworkAddress): the address on which the control peer is listening
        kafka_bootstrap_servers (str):
            'host[:port]' string (or list of 'host[:port]' strings)
            to contact the Kafka bootstrap servers on
    """

    def __init__(self, controlpeer_address, kafka_bootstrap_servers):
        self.cp_address = controlpeer_address
        self.uid = create_uid(prefix="R-")
        self.kafka_bootstrap_servers = kafka_bootstrap_servers

        self.input_address = None
        self.send = None
        self.receive = None

        self.brick = None
        self.destination = None
        self.has_inlet = False

    def __repr__(self):
        return f"BrickRunner(id={self.uid}, brick={self.brick}, input_address={self.input_address}"

    def start(self) -> "BrickRunner":
        """Start a new brick runner process"""
        host, port = self.cp_address
        br_command = [
            sys.executable,
            "-m",
            "titanfe.apps.brick_runner",
            "-id",
            str(self.uid),
            "-controlpeer",
            f"{host}:{port}",
            "-kafka",
            self.kafka_bootstrap_servers,
        ]

        log.debug("command: %r", br_command)
        br_process = subprocess.Popen(br_command)
        br_exitcode = br_process.poll()
        if br_exitcode is not None:
            log.error("Failed to start runner. (%s)", br_exitcode)
            return None

        return self
