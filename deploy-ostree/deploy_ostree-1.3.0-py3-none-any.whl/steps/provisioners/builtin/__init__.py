# Copyright 2018, 2019 Felix Krull
# Licensed under the MIT license, see LICENSE for details.

from .. import DeployStep
from ....config import Config, BuiltinProvisionerConfig
from .shell import shell_provisioner
from .machine_id import machine_id


class BuiltinProvisioner(DeployStep):
    PROVISIONERS = {
        'authorized-keys': shell_provisioner('authorized-keys'),
        'create-user': shell_provisioner('create-user'),
        'etc-fstab': shell_provisioner('etc-fstab'),
        'etc-network-interfaces': shell_provisioner('etc-network-interfaces'),
        'passwordless-sudo': shell_provisioner('passwordless-sudo'),
        'root-password': shell_provisioner('root-password'),
        'machine-id': machine_id,
    }

    def __init__(self, config: Config, provisioner: BuiltinProvisionerConfig) -> None:
        self.config = config
        self.provisioner = provisioner

    @property
    def title(self) -> str:
        return 'Provisioning: %s' % self.provisioner.name

    def run(self):
        self.PROVISIONERS[self.provisioner.name](self.config.deployment_dir, self.provisioner.args)
