#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Flow config: parsing and representation"""

from pathlib import Path
from typing import List

from ruamel import yaml

import titanfe.log as logging
from titanfe.classes import Brick
from titanfe.utils import pairwise
from titanfe.constants import FlowState

log = logging.getLogger(__name__)


class Flow:  # pylint: disable=too-few-public-methods
    """Represent a flow configuration with it bricks and connections

    Arguments:
        flow_config (dict): the flow configuration as dict
        bricks_config (dict): the bricks part of the configuration as dict
        path_to_bricks (Path): path to directory holding the "./bricks" folder
    """

    def __init__(self, flow_config, bricks_config, path_to_bricks):
        self.name = flow_config["Name"]
        self.uid = hash(self.name)
        self.state = FlowState.Inactive

        bricks_config_by_name = {b["Name"]: b for b in bricks_config}
        self.chain = [
            Brick.from_config(self.name, bricks_config_by_name[name], path_to_bricks)
            for name in flow_config["Chain"]
        ]

        self.inlet, self.sink = self.chain[0], self.chain[-1]
        self.bricks_by_uid = {b.uid: b for b in self.chain}

        self.connections = dict(pairwise(self.chain))
        self.connections[self.sink] = None

    def __repr__(self):
        return f"Flow({self.name}, {self.connections}, {self.chain})"


def parse_flows(config_file) -> List[Flow]:
    """parse a flow configuration file (yaml)"""
    config_root = Path(config_file).resolve().parent
    with open(config_file) as cf:  # pylint: disable=invalid-name
        config = yaml.safe_load(cf)

    flows = [Flow(flow, config["Bricks"], config_root) for flow in config["Flows"]]

    return flows
