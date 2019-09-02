"""
    Web server with rpc handler
"""
import logging
import tornado.web
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.web import StaticFileHandler
from bluemax.settings import get_settings, extend
from bluemax.utils import qname_to_class
from .broadcaster import Broadcaster
from .authentication import LogoutHandler
from .auth_static_file_handler import AuthStaticFileHandler
from .rpc_websocket import RpcWebsocket, RpcHandler

BROADCASTER = Broadcaster()
LOGGER = logging.getLogger(__name__)


def make_app(loop=None):
    """ Return a tornado app with settings and routes """
    global BROADCASTER  # pylint: disable=W0603
    settings = get_settings("tornado", {})
    assert get_settings("procedures"), "procedures required to remote!"
    default_manager = (
        "bluemax.services:ServicesRpc"
        if get_settings("services")
        else "bluemax.rpc:ContextRpc"
    )
    manager = qname_to_class(settings.get("manager", default_manager))
    settings["manager"] = manager.rpc_for(
        get_settings("procedures"), services=get_settings("services"), loop=loop
    )
    settings.setdefault("debug", get_settings("debug", False))
    routes = [(r"/rpc", RpcHandler), (r"/ws", RpcWebsocket)]
    if settings.get("auth_handler"):
        settings.setdefault("cookie_name", "bluemax-user")
        settings.setdefault("cookie_secret", "<change me - it was a dark and stormy..>")
        auth_handler = qname_to_class(settings.get("auth_handler"))
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
            LOGGER.info("serving from %s", settings.get("static_dir"))
    elif settings.get("static_dir"):
        # we use this because out static_dir is root for spa
        # static_path created a static by tornado
        routes.append(
            (
                r"/(.*)",
                StaticFileHandler,
                {"path": settings.get("static_dir"), "default_filename": "index.html"},
            )
        )
        LOGGER.info("serving from %s", settings.get("static_dir"))
    if get_settings("urls_extend"):
        routes = extend(get_settings("urls_extend"), routes)
    LOGGER.debug("tornado routes: %s", routes)
    LOGGER.debug("tornado settings: %s", settings)
    app = tornado.web.Application(routes, **settings)
    if get_settings("broadcaster"):
        BROADCASTER = qname_to_class(get_settings("broadcaster"))()
    BROADCASTER.start(settings["manager"].get_broadcast_queue(), RpcWebsocket.broadcast)
    return app


def main():
    """ run the tornado web server """
    app = make_app()
    port = get_settings("bluemax", {}).get("port", get_settings("PORT", "8080"))
    address = get_settings("bluemax", {}).get("address", "127.0.0.1")
    app.listen(int(port), address)
    LOGGER.info("listening on port %s", port)
    if app.settings.get("debug") is True:
        LOGGER.info("running in debug mode")
    ioloop = IOLoop.current()
    keep_alive_interval = int(get_settings("keep_alive_interval", "30000"))
    PeriodicCallback(RpcWebsocket.keep_alive, keep_alive_interval).start()
    try:
        ioloop.start()
    except KeyboardInterrupt:
        LOGGER.info("stopping")
        ioloop.stop()
