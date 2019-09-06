#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Flow config: parsing and representation"""
from enum import IntEnum
from pathlib import Path
from typing import List

from ruamel import yaml

from titanfe.utils import pairwise, create_uid
import titanfe.log as logging

from .brick import Brick

log = logging.getLogger(__name__)


class FlowState(IntEnum):
    ACTIVE = 1
    INACTIVE = 2


class Flow:
    """Represent a flow configuration with it bricks and connections

    Arguments:
        flow_config (dict): the flow configuration as dict
        bricks_config (dict): the bricks part of the configuration as dict
        path_to_bricks (Path): path to directory holding the "./bricks" folder
    """

    def __init__(self, control_peer, flow_config, bricks_config, path_to_bricks):
        self.control_peer = control_peer

        self.name = flow_config["Name"]
        self.uid = create_uid("F-")
        self.state = FlowState.INACTIVE

        bricks_config_by_name = {b["Name"]: b for b in bricks_config}
        self.bricks = [
            Brick.from_config(self, bricks_config_by_name[name], path_to_bricks)
            for name in flow_config["Chain"]
        ]

        self.bricks[0].inlet = True
        self.bricks_by_uid = {b.uid: b for b in self.bricks}

        for brick, next_brick in pairwise(self.bricks):
            brick.output = next_brick

    def __repr__(self):
        return f"Flow({self.name}, {self.bricks})"

    def start(self):
        """start brick runners for each brick in the flow"""
        log.debug("start flow: %s", self.name)
        for brick in self.bricks:
            brick.start()

    async def stop(self):
        """send a stop signal to all bricks"""
        log.info("stopping all bricks for: %s", self)
        for brick in self.bricks:
            await brick.stop()
        self.state = FlowState.INACTIVE
        log.info("%s stopped", self)


def parse_flows(control_peer, config_file) -> List[Flow]:
    """parse a flow configuration file (yaml)"""
    config_root = Path(config_file).resolve().parent
    with open(config_file) as cf:  # pylint: disable=invalid-name
        config = yaml.safe_load(cf)

    flows = [Flow(control_peer, flow, config["Bricks"], config_root) for flow in config["Flows"]]

    return flows
