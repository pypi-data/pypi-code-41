# Copyright 2018, 2019 Felix Krull
# Licensed under the MIT license, see LICENSE for details.

from pathlib import Path
from typing import Sequence
from . import DeployStep
from ..config import Config, Url
from ..run import run


class FileRemote(DeployStep):
    def __init__(self, cfg: Config, path: Path) -> None:
        self.remote = cfg.remote
        self.path = path
        self.ostree_repo = cfg.ostree_repo

    @property
    def title(self) -> str:
        return 'Adding OSTree remote: %s' % self.path

    def run(self):
        run([
            'ostree', 'remote', 'add',
            '--repo=%s' % self.ostree_repo,
            '--no-gpg-verify',
            self.remote,
            'file://%s' % self.path.absolute()
        ], check=True)


class HttpRemote(DeployStep):
    def __init__(self, cfg: Config, url: Url) -> None:
        self.remote = cfg.remote
        self.url = url
        self.ostree_repo = cfg.ostree_repo

    @property
    def title(self) -> str:
        return 'Adding OSTree remote: %s' % self.url

    def run(self):
        run([
            'ostree', 'remote', 'add',
            '--repo=%s' % self.ostree_repo,
            '--no-gpg-verify',
            self.remote,
            str(self.url),
        ], check=True)


def get_steps(cfg: Config) -> Sequence[DeployStep]:
    if isinstance(cfg.source, Path):
        return [FileRemote(cfg, cfg.source)]
    elif isinstance(cfg.source, Url):
        return [HttpRemote(cfg, cfg.source)]

    # Config should prevent this case
    raise RuntimeError('invalid config')
