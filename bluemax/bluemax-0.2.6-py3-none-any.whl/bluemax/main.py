import importlib
import logging
import logging.config
from collections import OrderedDict
import yaml
from . import context
from .settings import SETTINGS
from .web.rpc_websocket import RpcHandler, RpcWebsocket
from .tasks.utils import Colored
from .tasks.utils import pid_file
from .utils.describe import Procedure

log = logging.getLogger(__name__)


class Bluemax:
    """
    Bring up in order:

        extend_settings
        extend_logging
        extend_urls

    then:

        Web
        Services
        Worker
    """

    def __init__(self, module=None, settings=None, conf=None):
        self._procedures = None
        self._services = None
        self._application = None
        self._broadcaster = None
        self._urls = None
        self.settings = None

        if conf:
            with open(conf, "r") as file:
                settings = yaml.safe_load(file)

        self.settings = self.extend_settings(settings if settings else {})

        logging_config = self.extend_logging(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "standard": {
                        "format": "%(asctime)s %(levelname)s %(name)s: %(message)s"
                    }
                },
                "handlers": {
                    "default": {
                        "level": self.settings.get("logging", "INFO"),
                        "formatter": "standard",
                        "class": "logging.StreamHandler",
                        "stream": "ext://sys.stdout",  # Default is stderr
                    }
                },
                "loggers": {
                    "": {"handlers": ["default"], "propagate": True}  # root logger
                },
            }
        )
        if logging_config:
            logging.config.dictConfig(logging_config)

        if module is None:
            module = self.settings.get("procedures")
        assert module, "module required"
        mod = self._get_module_(module)
        if mod:
            self.settings.update(mod)
        if self.settings.get("log_extend"):
            logging_config = self._qname_to_class_(self.settings["log_extend"])(
                logging_config
            )
            if logging_config:
                logging.config.dictConfig(logging_config)
        if self.settings.get("settings_extend"):
            self.settings = self._qname_to_class_(self.settings["settings_extend"])(
                self.settings
            )
        SETTINGS.update(self.settings)

    @classmethod
    def describe(cls, target):
        """
            Will inspect each function in target.__all__
            and return an instance of Procedure for each
        """
        result = OrderedDict()
        for key in target.__all__:
            f = getattr(target, key)
            s = Procedure(key, f)
            log.debug(s)
            result[key] = s
        return result

    @classmethod
    def _qname_to_class_(cls, qname):
        """ returns a class from module_name:class_name """
        if isinstance(qname, str):
            _modules, _class = qname.split(":")
            return getattr(importlib.import_module(_modules), _class)
        return qname

    @classmethod
    def _import_module_(cls, name):
        "Its ok not to have the module but not ok to not have dependants."
        try:
            logging.debug("looking for module %s", name)
            return importlib.import_module(name)
        except ModuleNotFoundError as ex:
            if name not in str(ex):
                raise

    def _get_module_(self, name):
        """ import the project and return configuration options """

        options = {}
        if name is None:
            print("module expected")
        else:
            importlib.import_module(name)
            self._procedures = importlib.import_module(f"{name}.procedures")
            if self._procedures:
                if not getattr(self._procedures, "__all__"):
                    print(f"expected __all__ in procedures module")
                else:
                    options["procedures"] = f"{name}.procedures"
                    ext_log = self._import_module_(f"{name}.log")
                    if ext_log:
                        options["log_extend"] = f"{name}.log:extend"
                    ext_settings = self._import_module_(f"{name}.settings")
                    if ext_settings:
                        options["settings_extend"] = f"{name}.settings:extend"
                    ext_urls = self._import_module_(f"{name}.urls")
                    if ext_urls:
                        options["urls_extend"] = f"{name}.urls:extend"
                    services = self._import_module_(f"{name}.services")
                    if services:
                        options["services"] = f"{name}.services"
                        self._services = services
            else:
                print(f"expected procedures in {name}")

        return options

    def make_app(self, with_services=False, loop=None):
        """ returns a tornado Application configured with urls and settings"""
        from tornado.web import Application, StaticFileHandler
        from bluemax.web.authentication import LogoutHandler
        from bluemax.web.auth_static_file_handler import AuthStaticFileHandler

        settings = {}
        settings.update(self.settings["tornado"])

        default_manager = (
            "bluemax.services:ServicesRpc"
            if with_services
            else "bluemax.rpc:ContextRpc"
        )
        manager = self._qname_to_class_(settings.get("manager", default_manager))

        settings["manager"] = manager.rpc_for(
            self.settings.get("procedures"),
            services=self.settings.get("services"),
            loop=loop,
        )
        routes = [(r"/rpc", RpcHandler), (r"/ws", RpcWebsocket)]
        if settings.get("auth_handler"):
            settings.setdefault("cookie_name", "bluemax-user")
            settings.setdefault(
                "cookie_secret", "<change me - it was a dark and stormy..>"
            )
            auth_handler = self._qname_to_class_(settings.get("auth_handler"))
            settings["login_url"] = "/login"
            routes.insert(0, (r"/logout", LogoutHandler))
            routes.insert(0, (r"/login", auth_handler))
            if settings.get("static_dir"):
                # we use this because out static_dir is root for spa
                # static_path created a static by tornado
                routes.append(
                    (
                        r"/(.*)",
                        AuthStaticFileHandler,
                        {
                            "path": settings.get("static_dir"),
                            "default_filename": "index.html",
                        },
                    )
                )
                log.info("serving from %s", settings.get("static_dir"))
        elif settings.get("static_dir"):
            # we use this because out static_dir is root for spa
            # static_path created a static by tornado
            routes.append(
                (
                    r"/(.*)",
                    StaticFileHandler,
                    {
                        "path": settings.get("static_dir"),
                        "default_filename": "index.html",
                    },
                )
            )
            log.info("serving from %s", settings.get("static_dir"))
        self._urls = self.extend_urls(routes)
        if self.settings.get("urls_extend"):
            self._urls = self._qname_to_class_(self.settings["urls_extend"])(self._urls)
        log.debug("tornado urls: %s", self._urls)
        log.debug("tornado settings: %s", settings)
        return Application(self._urls, **settings)

    def stand_alone(self):
        """
        run web, services and procedures, no redis
        """
        default_manager = (
            "bluemax.services:ServicesRpc"
            if self._services
            else "bluemax.rpc:ContextRpc"
        )
        self.settings.setdefault("tornado", {}).setdefault("manager", default_manager)
        self.web(with_services=True)

    def stand_two(self):
        """
        run web, services and procedures but can scale
        the broadcaster uses redis to connect all websockets.
        """
        default_manager = (
            "bluemax.services:ServicesRpc"
            if self._services
            else "bluemax.rpc:ContextRpc"
        )
        self.settings.setdefault("tornado", {}).setdefault("manager", default_manager)
        self.settings.setdefault(
            "broadcaster", "bluemax.work.redis_broadcaster:RedisBroadcaster"
        )
        self.web(with_services=True)

    def web(self, with_services=False, pid="server.pid"):
        """
        runs tornado application, awaiting KeyboardInterrupt
        called directly assumes redis_url
        """
        from tornado.ioloop import IOLoop, PeriodicCallback

        self.settings.setdefault("tornado", {}).setdefault(
            "manager", "bluemax.work:RedisManager"
        )
        self._application = self.make_app(with_services=with_services)

        port = self.settings.get("bluemax", {}).get("port", "8080")
        address = self.settings.get("bluemax", {}).get("address", "127.0.0.1")
        self._application.listen(int(port), address)
        log.info("listening on http://%s:%s", address, port)

        self._broadcaster = self._qname_to_class_(
            self.settings.get("broadcaster", "bluemax.web.broadcaster:Broadcaster")
        )()
        self._broadcaster.start(
            self._application.settings["manager"].get_broadcast_queue(),
            RpcWebsocket.broadcast,
        )

        ioloop = IOLoop.current()
        keep_alive_interval = int(self.settings.get("keep_alive_interval", "30000"))
        PeriodicCallback(RpcWebsocket.keep_alive, keep_alive_interval).start()

        with pid_file(pid):
            try:
                ioloop.start()
            except KeyboardInterrupt:
                log.info("stopping")
                ioloop.stop()

    def _run_loop_(self, loop, manager):
        """ run an async ioloop """
        try:
            loop.run_forever()
        finally:
            log.info("stopping")
            loop.run_until_complete(manager.shutdown())
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

    def services(self, pid="services.pid"):
        """ run just services """
        import asyncio
        from bluemax.services.server import Services

        assert self.settings.get("redis_url"), "required to distrubute broadcasts"
        manager = Services(self._services)
        context._MANAGER_ = manager  # pylint: disable=W0212
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(manager.start_all_services())
        with pid_file(pid):
            self._run_loop_(loop, manager)

    def worker(self, pid="worker.pid"):
        """ run just procedures """
        import asyncio
        from bluemax.work.worker import Worker

        assert self.settings.get("redis_url"), "required to distrubute work queue"
        manager = Worker.rpc_for(
            self.settings["procedures"],
            max_workers=self.settings.get("max_workers"),
            max_threads=self.settings.get("max_threads"),
        )
        loop = asyncio.get_event_loop()
        with pid_file(pid):
            self._run_loop_(loop, manager)

    def config(self):
        """ displays resultant config """
        log.info("\n---\n%s", yaml.dump(self.settings))
        print(Colored.blue("available:"))
        for description in self.describe(self._procedures).values():
            print("  ", description)
        if self._services:
            print(Colored.blue("services:"))
            for description in self.describe(self._services).values():
                print("  ", description)
        print("", flush=True)

    def extend_logging(self, config):
        """ overide this to extend logging """
        return config

    def extend_settings(self, settings):
        """ overide this to extend settings """
        return settings

    def extend_urls(self, urls):
        """ overide this to extend urls """
        return urls
