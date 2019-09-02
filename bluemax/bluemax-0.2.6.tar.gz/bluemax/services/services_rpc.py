import asyncio
import importlib
import logging
from bluemax.rpc import ContextRpc
from .services_manager import ServicesManager

LOGGER = logging.getLogger(__name__)


class ServicesRpc(ServicesManager, ContextRpc):
    def __init__(self, package, services, *args, **kwargs):
        ServicesManager.__init__(self, importlib.import_module(services))
        ContextRpc.__init__(self, package, *args, **kwargs)
        asyncio.ensure_future(self.start_all_services())

    @property
    def procedures(self):
        """ return a list of publicly available functions """
        return getattr(self._package_, "__all__") + self._SERVICE_ACTIONS_

    def qname_to_func(self, qname):
        """ return the service or function for the qname """
        if qname in self._SERVICE_ACTIONS_:
            return getattr(self, qname)
        return super().qname_to_func(qname)

    async def shutdown(self, wait=True):
        """ We have runnning resources that require tidy up """
        await self.stop_all_services()
        await ContextRpc.shutdown(self)
