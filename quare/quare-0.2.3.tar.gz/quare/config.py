# -*- coding: utf-8 -*-
"""Configuration handling. Exports config class."""

import os
from pathlib import Path

import yaml

from .exceptions import ConfigNotFoundError
from .ui_messages import MISSING_CONF_ERROR_MESSAGE


class quareConfig:
    """Parses a configuration file and stores/retrieves its values."""

    DEFAULT_CONFIG_FILENAME = os.path.join(str(Path.home()), ".quare-conf.yaml")

    def __init__(self, config_path=None):
        self._find_config(config_path)
        self.raw_config = {}
        self._read_config()
        self._chats = []
        self._docs = []

    def _find_config(self, config_path):
        if config_path is not None and os.path.isfile(config_path):
            self.config_path = config_path
        else:
            self.config_path = self.DEFAULT_CONFIG_FILENAME

    def _read_config(self):
        if os.path.isfile(self.config_path):
            with open(self.config_path) as conf:
                self.raw_config = yaml.safe_load(conf.read())
            self.defaults = self.raw_config.get("defaults", {})
        else:
            raise ConfigNotFoundError(MISSING_CONF_ERROR_MESSAGE)

    @property
    def default_docs(self):
        if not self._docs:
            self._docs = self.defaults.get("documents", [])
        return self._docs

    @property
    def default_chats(self):
        if not self._chats:
            self._chats = self.defaults.get("chats", [])
        return self._chats
