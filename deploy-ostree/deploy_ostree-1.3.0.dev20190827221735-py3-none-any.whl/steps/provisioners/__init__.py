# Copyright 2018, 2019 Felix Krull
# Licensed under the MIT license, see LICENSE for details.

from typing import Sequence
from ...config import Config, ProvisionerConfig, BuiltinProvisionerConfig, ScriptProvisionerConfig
from .. import DeployStep
from .builtin import BuiltinProvisioner
from .script import ScriptProvisioner


_TYPES = {
    BuiltinProvisionerConfig: BuiltinProvisioner,
    ScriptProvisionerConfig: ScriptProvisioner,
}


def create_provisioner(cfg: Config, provisioner: ProvisionerConfig) -> DeployStep:
    cls = _TYPES[type(provisioner)]
    return cls(cfg, provisioner)


def get_steps(cfg: Config) -> Sequence[DeployStep]:
    return [create_provisioner(cfg, provisioner) for provisioner in cfg.provisioners]
