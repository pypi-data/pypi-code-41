import os
import logging
from pathlib import Path

from enum import Enum

from configpp.soil import Config, Transport, Location

class Mode(Enum):

    DEVELOPMENT = 'development'
    PRODUCTION = 'production'

logger = logging.getLogger(__name__)


default_dashboard_data = {
    'dashboards': {},
    'widgets': {},
}

class AppConfig:

    dashboard_config_loader: Config

    def load(self, path_like: str):

        path = Path(path_like).expanduser().absolute()

        if not path.parent.is_dir():
            path.parent.mkdir(parents = True)

        self._location = Location(path.parent)

        self.dashboard_config_loader = Config(path.name, transport = Transport([self._location]))

        return self.dashboard_config_loader.load()

    def save(self):
        self.dashboard_config_loader.dump(self._location)

    def init_logger(self, debug: bool):
        logging.basicConfig(
            level = logging.DEBUG if debug else logging.INFO,
            format = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s: %(message)s',
        )
