import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict

from aiohttp import web

from .controller_base import ControllerBase

logger = logging.getLogger(__name__)

class ControllerCache:

    @dataclass
    class Item:
        data: Any
        expired: datetime

    def __init__(self):
        self._data: Dict[str, self.Item] = {}

    def set(self, key: str, data, expiry: timedelta):
        self._data[key] = self.Item(data, datetime.now() + expiry)

    def get(self, key: str):
        item = self._data.get(key)
        if item is None:
            return None
        if item.expired < datetime.now():
            return None
        return item.data

    def cached_json_controller(self, expiry: timedelta):
        def wrapper(func):
            @wraps(func)
            async def decor(controller: ControllerBase, request: web.Request):
                data = self.get(request.path)
                if data and not request.query.get('force-refetch') and expiry.total_seconds() > 0:
                    logger.debug("Get '%s' data from cache", request.path)
                    return web.json_response(data)

                data = await func(controller, request)

                self.set(request.path, data, expiry)

                return web.json_response(data)
            return decor
        return wrapper
