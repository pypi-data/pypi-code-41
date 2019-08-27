# Copyright 2018, 2019 Felix Krull
# Licensed under the MIT license, see LICENSE for details.

from . import DeployStep
from ..config import Config
from ..run import run


class DeleteRemote(DeployStep):
    def __init__(self, cfg: Config) -> None:
        self.remote = cfg.remote
        self.ostree_repo = cfg.ostree_repo

    @property
    def title(self) -> str:
        return 'Removing remote: %s' % self.remote

    def run(self):
        run([
            'ostree', 'remote', 'delete',
            '--repo=%s' % self.ostree_repo,
            '--if-exists',
            self.remote
        ], check=True)
