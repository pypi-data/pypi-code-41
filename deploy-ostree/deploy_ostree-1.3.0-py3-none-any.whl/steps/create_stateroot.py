# Copyright 2018, 2019 Felix Krull
# Licensed under the MIT license, see LICENSE for details.

from . import DeployStep
from ..run import run


class CreateStateroot(DeployStep):
    @property
    def title(self) -> str:
        return 'Creating stateroot: %s' % self.config.stateroot

    def run(self):
        if self.config.stateroot_dir.exists():
            print("already exists, skipping")
            return
        run([
            'ostree', 'admin', 'os-init',
            '--sysroot=%s' % self.config.sysroot,
            self.config.stateroot
        ], check=True)
