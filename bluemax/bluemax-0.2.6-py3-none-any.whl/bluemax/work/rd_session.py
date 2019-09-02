""" Utilities for working with redis """
import asyncio
import logging
import aioredis
from bluemax.settings import get_settings

LOGGER = logging.getLogger(__name__)


async def connect(redis_url: str = None):
    """
        Create a single connection to redis using
        option.redis_url if none is supplied
    """
    redis_url = get_settings("redis_url") if redis_url is None else redis_url
    assert redis_url
    if redis_url.startswith("redis://:"):
        LOGGER.info("connecting to redis: redis://%s", redis_url.split('@')[-1])
    else:
        LOGGER.info("connecting to redis: %s", redis_url)
    loop = asyncio.get_event_loop()
    redis_conn = await aioredis.create_redis(redis_url, loop=loop)
    return redis_conn


_POOLS_ = {}


async def pool(redis_url: str = None):
    """
        Create a pool connection to redis using
        option.redis_url if none is supplied
    """
    redis_url = get_settings("redis_url") if redis_url is None else redis_url
    assert redis_url
    if redis_url.startswith("redis://:"):
        LOGGER.info("connecting to redis: redis://%s", redis_url.split('@')[-1])
    else:
        LOGGER.info("connecting to redis: %s", redis_url)
    con_pool = _POOLS_.get(redis_url)
    if con_pool is None:
        loop = asyncio.get_event_loop()
        con_pool = await aioredis.create_pool(
            redis_url, minsize=5, maxsize=10, loop=loop
        )
        _POOLS_[redis_url] = con_pool
    return con_pool


async def shutdown():
    for url in list(_POOLS_):
        redis_pool = _POOLS_[url]
        redis_pool.close()
        await redis_pool.wait_closed()
        del _POOLS_[url]
    _POOLS_.clear()
