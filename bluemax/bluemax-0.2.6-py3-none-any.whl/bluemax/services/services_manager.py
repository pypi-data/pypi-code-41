"""
    A service is a task that runs in the background.
    It can be started and stopped.
"""
import asyncio
import logging

LOGGER = logging.getLogger(__name__)


class ServicesManager:

    _SERVICE_ACTIONS_ = [
        "start_service",
        "stop_service",
        "start_all_services",
        "stop_all_services",
        "available_services",
        "status_services"
    ]

    def __init__(self, services):
        self._services = {srv.__name__: srv for srv in self._discover_(services)}
        self._tasks = {}

    @classmethod
    def _discover_(cls, services):
        """ utility to discover public functions in a module """
        _services = services.__all__ if hasattr(services, "__all__") else dir(services)
        for name in _services:
            if name[0] == "_":
                continue
            service = getattr(services, name)
            if callable(service):
                yield service

    @property
    def available_services(self):
        """ names of available services """
        return [name for name in self._services]

    async def status_services(self):
        """ returns a list of services and a list of running """
        return {
            "running": [str(key) for key in self._tasks],
            "services": self.available_services
        }

    async def start_service(self, name: str):
        """ create a task of a function """
        if name not in self._tasks:
            LOGGER.info("running service %s", name)
            task = asyncio.ensure_future(self._services[name]())
            self._tasks[name] = task

    async def stop_service(self, name: str):
        """ stop a task """
        if name in self._tasks:
            LOGGER.info("stopping service %s", name)
            task = self._tasks[name]
            task.cancel()
            LOGGER.info("stopped service %s", name)
            del self._tasks[name]

    async def start_all_services(self):
        """ run all services """
        for name in self.available_services:
            await self.start_service(name)

    async def stop_all_services(self):
        """ helper to shut down """
        for name in list(self._tasks):
            await self.stop_service(name)
