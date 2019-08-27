# Copyright 2018, 2019 Felix Krull
# Licensed under the MIT license, see LICENSE for details.

from ..config import Config


class DeployError(RuntimeError):
    pass


class DeployStep:
    def __init__(self, config: Config) -> None:
        self.config = config

    @property
    def title(self) -> str:
        raise NotImplementedError

    def run(self):
        raise NotImplementedError

    def cleanup(self):
        pass
