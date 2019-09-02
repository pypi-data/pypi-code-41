"""
    A json rpc 2.0 websocket
"""
import asyncio
import logging
import time
import uuid
from tornado.web import RequestHandler, HTTPError
from tornado.websocket import WebSocketHandler
from bluemax.utils import json_utils
from .authentication import UserMixin

LOGGER = logging.getLogger(__name__)


class JsonRpcException(Exception):
    """ Throw xception that capture message """

    def __init__(self, code, message):
        super().__init__(self, message)
        self.js_code = code
        self.js_message = message


class JsonRpcMixin:
    """ Common functions used by both ws and http """

    @property
    def manager(self):
        """ return the manager setting """
        return self.settings["manager"]

    @property
    def procedures(self):
        """ returns the managers procedure names """
        return self.manager.procedures

    def is_authenticated(self):
        """
        Raise an error if we should login otherwise
        return user
        """
        user = None
        if self.settings.get("login_url", None):
            user = self.get_current_user()
            if user is None:
                raise HTTPError(403)
        return user

    @classmethod
    def get_params(cls, content):
        """ split params into args and kwargs """
        if isinstance(content["params"], dict):
            return [], content["params"]
        if isinstance(content["params"], list):
            return content["params"], {}
        raise JsonRpcException(-32602, "Params neither list or dict")

    async def handle_content(self, content):  # noqa: 901
        """ Assumes a json 2.0 method conent """
        LOGGER.info(content)
        result = {"jsonrpc": "2.0"}
        try:
            if content.get("jsonrpc") != "2.0":
                raise JsonRpcException(-32600, "protocol not supported")
            ref = content.get("id", None)
            if ref:
                result["id"] = ref

            method = content.get("method")
            if method is None:
                raise JsonRpcException(-32600, "no method")
            if method[0] == "_":
                raise JsonRpcException(-32600, "method private")
            if method not in self.procedures:
                raise JsonRpcException(-32600, f"no such method: {method}")

            user = self.is_authenticated()
            args, kwargs = self.get_params(content)
            logging.debug("%s %s %s %s", user, method, args, kwargs)
            response = self.manager.perform(user, method, *args, **kwargs)
            if response:  # can return None or future
                response = await response
            if asyncio.iscoroutine(response) or asyncio.isfuture(response):
                result["result"] = await response
            else:
                result["result"] = response
            if ref is None:
                result = None  # its a notification

        except JsonRpcException as ex:
            LOGGER.exception(ex)
            result["error"] = {"code": ex.js_code, "message": ex.js_message}
        except Exception as ex:  # pylint: disable=W0703
            LOGGER.exception(ex)
            result["error"] = {"code": -32000, "message": str(ex)}
        LOGGER.debug(repr(result))
        return result


class RpcHandler(UserMixin, JsonRpcMixin, RequestHandler):  # pylint: disable=W0223
    """ marshall json rpc 2.0 requests and respond """

    async def post(self):
        """ We only hanlde the post method """
        self.is_authenticated()
        content = json_utils.loads(self.request.body)
        result = await self.handle_content(content)
        if result:
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.write(json_utils.dumps(result))


class RpcWebsocket(UserMixin, JsonRpcMixin, WebSocketHandler):  # pylint: disable=W0223
    """ implementation """

    _clients_ = []

    def filter_client(self, filter_clients=None):  # pylint: disable=W0613,R0201
        """ Does this client meet these criteria """
        return False

    @classmethod
    def keep_alive(cls):
        msg = str(time.time()).encode("utf8")
        for client in cls._clients_:
            client.ping(msg)

    @classmethod
    async def broadcast(cls, signal, message, filter_clients=None):
        """ broadcasts signal:message to all clients """
        LOGGER.debug("broadcasting %s: %s", signal, message)
        data = json_utils.dumps({"signal": signal, "message": message})
        for client in cls._clients_:
            if not client.filter_client(filter_clients):
                client.write_message(data)

    def initialize(self):
        """ set our id """
        self._id = str(uuid.uuid4())  # pylint: disable=W0201

    def open(self, *args, **kwargs):
        """ websocket open - register user """
        user = self.is_authenticated()
        self._clients_.append(self)
        if user:
            LOGGER.info("user: %s", user)
            self.write_message(
                json_utils.dumps({"signal": "set_user", "message": user})
            )

    async def on_message(self, data):  # pylint: disable=W0221
        """ handle the action """
        content = json_utils.loads(data)
        loop = asyncio.get_running_loop()
        asyncio.ensure_future(self.handle_result(content), loop=loop)

    async def handle_result(self, content):
        """ handle the result of a perform """
        result = await self.handle_content(content)
        if result:
            self.write_message(json_utils.dumps(result))

    def on_close(self):
        """ unregister us """
        self._clients_.remove(self)
