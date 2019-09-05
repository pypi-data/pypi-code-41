from typing import List, ClassVar
import logging.config
import asyncio
import uvloop

from . import helpers

from macrobase_driver.driver import MacrobaseDriver, Context
from macrobase_driver.driver import MacrobaseDriver, Context
from macrobase_driver.logging import get_logging_config
from macrobase_driver.hook import HookHandler

from sanic_macrobase.config import SanicDriverConfig
from sanic_macrobase.route import Route
from sanic_macrobase.hook import SanicHookNames

from structlog import get_logger
from sanic import Sanic, Blueprint
from sanic.config import Config


log = get_logger('SanicDriver')


class SanicDriver(MacrobaseDriver):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.name is None:
            self.name = 'SanicDriver'
        
        config = kwargs.get('config', None)
        if config is None:
            config = SanicDriverConfig()
        self.config = config
        self._hooks: Dict[SanicHookNames, List[HookHandler]] = {}
        self._routes = []
        self._preload_server()

    def _preload_server(self):
        self._sanic = Sanic(name=self.name, log_config=get_logging_config(self.config))
        self._sanic.config = Config()

    def update_config(self, config: SanicDriverConfig):
        """
        Add sanic driver config
        """
        self.config.update(config)

    def add_hook(self, name: SanicHookNames, handler):
        if name not in self._hooks:
            self._hooks[name] = []

        self._hooks[name].append(HookHandler(self, handler))

    def add_routes(self, routes: List[Route]):
        """
        Add HTTP routes
        """
        self._routes.extend(routes)

    def _apply_routes(self):
        prefix = self.config.APP_BLUEPRINT

        if prefix is None or len(prefix) == 0:
            server = self._sanic
        else:
            server = Blueprint(prefix, url_prefix=prefix)

        if self.config.HEALTH_ENDPOINT:
            from .endpoint import HealthEndpoint
            server.add_route(HealthEndpoint(self.context, self.config), '/health', {'GET', 'POST'})

        [server.add_route(
            r.handler,
            r.uri,
            methods=r.methods,
            host=r.host,
            strict_slashes=r.strict_slashes,
            version=r.version,
            name=r.name) for r in self._routes]

        if isinstance(server, Blueprint):
            self._sanic.blueprint(server)

    def _apply_logging(self):
        self._logging_config = get_logging_config(self.config)
        logging.config.dictConfig(self._logging_config)

    def _apply_hooks(self):
        for name, handlers in self._hooks.items():
            for handler in handlers:
                self._sanic.listener(name.value)(handler)

        # async def lock_context(driver, context: Context, loop):
        #     context.lock()
        #
        # self._sanic.listener(SanicHookNames.after_server_start.value)(HookHandler(self, lock_context))
        pass

    def _prepare_server(self):
        self._sanic.config.from_object(self.config)
        self._apply_logging()
        self._apply_hooks()
        self._apply_routes()

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)

        self._prepare_server()

        try:
            self._sanic.run(
                host=self.config.APP_HOST,
                port=self.config.APP_PORT,
                debug=self.config.DEBUG,
                workers=self.config.WORKERS,
                access_log=self.config.ACCESS_LOG)
        except Exception as e:
            log.error(e)
            self._sanic.stop()
