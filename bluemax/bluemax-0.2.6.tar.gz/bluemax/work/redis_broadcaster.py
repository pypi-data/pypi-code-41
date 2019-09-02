"""
    Implements broadcasting to redis
"""
import asyncio
import logging
from bluemax import get_settings
from bluemax.web.broadcaster import Broadcaster
from bluemax.utils import json_utils
from .redis_pubsub import redis_publish, redis_subscribe

LOGGER = logging.getLogger(__name__)


class RedisBroadcaster(Broadcaster):
    """
    Connects the local queue to redis and
    redis to the local broadcaster(consumer)
    """

    def __init__(self):
        self.consumer = None
        super().__init__()

    async def broadcaster(self, queue, consumer):
        """ Connect websockets to manager broadcast queue """
        self.consumer = consumer
        LOGGER.info("subscribing to redis")
        self.handle_broadcast()
        LOGGER.info("listening to queue")
        while True:
            value = await queue.get()
            self._publish_(*value)
            queue.task_done()

    @redis_publish(key=get_settings("redis_broadcast_q", "broadcast"))
    def _publish_(self, signal, message, client_filter=None):
        """ will broadcast to redis """
        msg = json_utils.dumps((signal, message, client_filter))
        LOGGER.debug("broadcasted to redis: %s", msg)
        return msg

    @redis_subscribe(key=get_settings("redis_broadcast_q", "broadcast"))
    async def handle_broadcast(self, message=None):
        """ called by redis sub """
        LOGGER.info("got broadcast: %s", message)
        args = json_utils.loads(message)
        asyncio.ensure_future(self.consumer(*args))
