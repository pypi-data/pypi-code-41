#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""A Brick"""
import asyncio

import titanfe.log as logging
from titanfe.utils import create_uid, first

from .runner import BrickRunner

log = logging.getLogger(__name__)


class Brick:
    """Encapsulate the Brick functions"""
    def __init__(self, flow, name, module):
        self.uid = create_uid("B-")

        self.flow = flow
        self.name = name
        self.module = module

        self.inlet = False
        self.output = None
        self.runners = []

    def __repr__(self):
        return f"Brick({self.name}, {self.uid}, {self.module}, output={self.output})"

    @classmethod
    def from_config(cls, flow, brick_config, root_path):
        return cls(
            flow=flow,
            name=brick_config["Name"],
            module=str(root_path / brick_config["Module"]),
        )

    def start(self):
        self.start_new_runner()

    def start_new_runner(self):
        runner = BrickRunner(self).start()
        self.runners.append(runner)
        self.flow.control_peer.runners[runner.uid] = runner

        log.debug('%s started runner %s', self, runner)

    async def stop(self):
        for runner in self.runners:
            await runner.stop()
            del self.flow.control_peer.runners[runner.uid]
            self.runners.remove(runner)

    async def runner_available(self) -> BrickRunner:
        """waits until a runner for the brick has registered it's input address"""
        runner = first(runner for runner in self.runners if runner.input_address is not None)
        while not runner:
            await asyncio.sleep(0.0001)
            runner = first(runner for runner in self.runners if runner.input_address is not None)

        return runner

    def to_dict(self):
        return {
            "flow": self.flow.name,
            "name": self.name,
            "module": self.module,
            "inlet": self.inlet,
            "uid": self.uid,
        }
