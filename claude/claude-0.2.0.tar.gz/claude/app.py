import asyncio
import logging
import os
from time import sleep, time

import pkg_resources
from aiohttp import web
from jinja2 import Template

from .api import Api
from .config_sync_service import ConfigSyncService
from .javascript_libraries import javascript_libraries
from .config import AppConfig, Mode, default_dashboard_data
from .chromecast_proxy_service import chromecast_proxy_service

logger = logging.getLogger(__name__)

class App:

    def __init__(self, database_file: str, debug: bool):

        self.config = AppConfig()
        self.config.init_logger(debug)
        self.config.load(database_file)
        self.debug = debug

        self.aio_app = web.Application()

        current_directory = os.path.dirname(__file__)

        with open(os.path.join(current_directory, 'templates/index.html')) as f:
            self._index_template = Template(f.read())


        self.api = Api(self.aio_app)
        self.config_syncer = ConfigSyncService(self.config)

        self.aio_app.router.add_get('/', self.index)
        self.aio_app.router.add_static('/static', os.path.join(current_directory, 'static'))
        self.aio_app.router.add_route('GET', '/config-sync', self.config_syncer.controller)
        self.aio_app.router.add_route('GET', '/chromecast-proxy/{friendly_name}', chromecast_proxy_service)

    async def index(self, request):

        mode = Mode.DEVELOPMENT if self.debug else Mode.PRODUCTION

        version = str(time()) if self.debug else pkg_resources.get_distribution("claude").version

        resp_text = self._index_template.render(
            version = version,
            dev_mode = mode == Mode.DEVELOPMENT,
            initial_data = self.config.dashboard_config_loader.data or default_dashboard_data,
            javascript_libraries = javascript_libraries[mode],
        )

        return web.Response(body = resp_text, content_type = 'text/html')
