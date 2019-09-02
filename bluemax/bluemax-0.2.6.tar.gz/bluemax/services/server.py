"""
    A service is a task that runs in the background.
    It can be started and stopped.
"""
import asyncio
import importlib
import logging
from bluemax import context
from bluemax.settings import get_settings
from bluemax.work.redis_pubsub import redis_subscribe
from bluemax.utils import json_utils
from bluemax.performer import Performer
from .services_manager import ServicesManager

LOGGER = logging.getLogger(__name__)


class Services(ServicesManager, Performer):
    """ This service manager only support async functions """

    def __init__(self, services):
        ServicesManager.__init__(self, services)
        Performer.__init__(self)
        self.handle_action()  # setup subscription
        LOGGER.debug("services %s", self.available_services)

    @redis_subscribe(key=get_settings("redis_services_q", "service"))
    async def handle_action(self, message=None):  # pylint: disable=R0201
        """ start and stop stuff """
        LOGGER.info(message)
        content = json_utils.loads(message)
        qname = content["qname"]
        if qname in self._SERVICE_ACTIONS_:
            func = getattr(self, qname)
            if asyncio.iscoroutinefunction(func):
                await func(*content["args"], **content["kwargs"])
            else:
                func(*content["args"], **content["kwargs"])

    async def shutdown(self):
        """ tidy up while we're here """
        await self.stop_all_services()
        LOGGER.info("shutting down redis subscriptions")


def main():
    """ run loop """
    assert get_settings("services")
    LOGGER.info("loading: %s", get_settings("services"))
    services_package = importlib.import_module(get_settings("services"))
    manager = Services(services_package)
    context._MANAGER_ = manager  # pylint: disable=W0212
    LOGGER.info("services: %s", manager.available_services)
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(manager.start_all_services())
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(manager.shutdown())
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
