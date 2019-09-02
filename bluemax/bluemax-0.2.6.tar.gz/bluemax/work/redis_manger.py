""" A manager that delegates to redis """
import asyncio
import logging
from bluemax.settings import get_settings
from bluemax.rpc import BroadcastMixin, Rpc
from bluemax.utils import json_utils
from bluemax.performer import Performer
from bluemax.services import ServicesManager
from .redis_pubsub import redis_subscribe
from . import rd_session

LOGGER = logging.getLogger(__name__)


class RemoteException(Exception):
    """ We cannot serialise Exceptions so this is the message """


class RedisManager(BroadcastMixin, Performer, Rpc):
    """
        A subclass of manager that delegates
        to a redis queue. It also subscribes
        to broadcasts and sends them on.
    """

    def __init__(self, *args, **kwargs):
        """ Store state and schedule setup """
        BroadcastMixin.__init__(self)
        Performer.__init__(self)
        Rpc.__init__(self, *args, **kwargs)
        self._broadcast_q_ = asyncio.Queue()
        self._loop = asyncio.get_event_loop()
        self._futures_ = {}
        # set off subscriptions
        self.handle_broadcast()

    async def shutdown(self):
        """ Shut down the pool """
        redis = rd_session.pool()
        redis.close()

    @property
    def procedures(self):
        """ return a list of publicly available functions """
        procs = getattr(self._package_, "__all__")
        if get_settings("services"):
            procs = procs + ServicesManager._SERVICE_ACTIONS_
        return procs

    @redis_subscribe(key=get_settings("redis_broadcast_q", "broadcast"))
    def handle_broadcast(self, message=None):
        """ called by redis sub """
        LOGGER.info("got broadcast: %s", message)
        args = json_utils.loads(message)
        self._broadcast_(*args)
