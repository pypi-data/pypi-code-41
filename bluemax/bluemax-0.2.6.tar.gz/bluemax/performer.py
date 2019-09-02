import asyncio
import logging
import uuid
from bluemax.utils import json_utils
from bluemax.settings import get_settings
from bluemax.work.redis_pubsub import redis_publish, redis_subscribe
from bluemax.services import ServicesManager


LOGGER = logging.getLogger(__name__)


class RemoteException(Exception):
    """ We cannot serialise Exceptions so this is the message """


class Performer:
    def __init__(self):
        self._futures_ = {}
        self.REPY_CHANNEL = f"channel:{uuid.uuid4()}"
        redis_subscribe(self.handle_reply, key=self.REPY_CHANNEL)()

    @redis_publish(key=get_settings("redis_broadcast_q", "broadcast"))
    def broadcast(self, signal, message, filter_clients=None):  # pylint: disable=W0221
        """ broadcast, because there may be more than one """
        return json_utils.dumps((signal, message, filter_clients))

    @redis_publish(key=get_settings("redis_work_q", "perform"), cmd="rpush")
    def send_perform(self, content):  # pylint: disable=R0201
        """ format performance content """
        return json_utils.dumps(content)

    @redis_publish(key=get_settings("redis_service_q", "service"))
    def send_service(self, content):  # pylint: disable=R0201
        """ format performance content """
        return json_utils.dumps(content)

    def perform(self, user, qname, *args, **kwargs):  # pylint: disable=W0221
        """ create task add it to queue """
        future_id = str(uuid.uuid4())
        content = {
            "user": user,
            "qname": qname,
            "args": args,
            "kwargs": kwargs,
            "future_id": future_id,
            "reply": self.REPY_CHANNEL,
        }
        future = None
        LOGGER.info(content)
        if qname in ServicesManager._SERVICE_ACTIONS_:
            self.send_service(content)
        else:
            future = asyncio.Future()
            self._futures_[future_id] = future
            self.send_perform(content)
        return future

    def handle_reply(self, msg=None):
        """ called by redis sub """
        result = json_utils.loads(msg)
        LOGGER.debug("response: %s", result)
        future = self._futures_.get(result.get("future_id"), None)
        if future:
            if result.get("result"):
                future.set_result(result["result"])
            else:
                future.set_exception(RemoteException(result.get("error")))
        if result.get("broadcasts"):
            for message in result["broadcasts"]:
                self.broadcast(*message)
