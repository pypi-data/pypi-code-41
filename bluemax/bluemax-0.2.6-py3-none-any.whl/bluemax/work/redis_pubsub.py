# pylint: disable=C0103
"""
    Like aws_pubsub but for redis
"""
import asyncio
import functools
import logging
from . import rd_session

LOGGER = logging.getLogger(__name__)


class redis_publish:
    """
        decorator to publish to redis

        usage::

            @redis_publish
            def foo():
                # will publish 'foo' to redis:foo
                return 'foo'

            @redis_publish(queue_name='bar')
            def foo():
                # will publish 'foo' to redis:bar
                return 'foo'
    """

    def __init__(self, method=None, key=None, cmd="publish"):
        LOGGER.debug("__init__(%r, %r)", method, key)
        if method and hasattr(method, "__call__"):
            self.method = method
        else:
            self.method = None
        self.key = key
        self.cmd = cmd

    def __get__(self, obj, type_=None):
        return functools.partial(self, obj)

    async def _publish_(self, *args, **kwargs):
        """ Called each time we are called """
        if asyncio.iscoroutinefunction(self.method):
            document = await self.method(*args, **kwargs)
        else:
            document = self.method(*args, **kwargs)
        pool = await rd_session.pool()
        await pool.execute(self.cmd, self.key, document)
        LOGGER.debug("queued %s -> %r", self.key, document)

    def __call__(self, *args, **kwargs):
        """ Called by actor, we return a task """
        LOGGER.debug("__call__(%r, %r) %r", args, kwargs, self.method)
        if self.method is None:
            self.method = args[0]
            return self
        if self.key is None:
            self.key = self.method.__name__

        LOGGER.info("method %r", self.method)
        task = asyncio.ensure_future(self._publish_(*args, **kwargs))
        return task


class redis_subscribe:
    """
        decorator subscribe to redis

        usage::

            @redis_subscribe
            def foo(message):
                # will subscribe to redis:foo
                print(message)

            @redis_subscribe(queue_name='bar')
            def foo(message):
                # will subscribe to redis:bar
                print(message)
    """

    def __init__(self, method=None, key=None):
        LOGGER.debug("__init__(%r, %r)", method, key)
        if method and hasattr(method, "__call__"):
            self.method = method
        else:
            self.method = None
        self.key = key

    def __get__(self, obj, type_=None):
        return functools.partial(self, obj)

    async def _subscribe_(self, *args, **kwargs):
        """ read our queue and call our method """
        conn = await rd_session.connect()
        response = await conn.subscribe(self.key)
        channel = response[0]
        LOGGER.info("subscribed to: %s", self.key)
        try:
            while await channel.wait_message():
                document = await channel.get(encoding="utf-8")
                LOGGER.debug("Got Message: %s", document)
                _args = list(args) + [document]
                if asyncio.iscoroutinefunction(self.method):
                    asyncio.ensure_future(self.method(*_args, **kwargs))
                else:
                    self.method(*_args, **kwargs)
        finally:
            conn.close()

    def __call__(self, *args, **kwargs):
        """ called to set us running """
        LOGGER.debug("__call__(%r, %r) %r", args, kwargs, self.method)
        if self.method is None:
            self.method = args[0]
            return self
        if self.key is None:
            self.key = self.method.__name__
        task = asyncio.ensure_future(self._subscribe_(*args, **kwargs))
        return task


class redis_cmd:
    """
        decorator subscribe to redis

        usage::

            @redis_subscribe
            def foo(message):
                # will subscribe to redis:foo
                print(message)

            @redis_subscribe(queue_name='bar')
            def foo(message):
                # will subscribe to redis:bar
                print(message)
    """

    def __init__(self, method=None, key=None, cmd="get", cmd_args=None):
        LOGGER.debug("__init__(%r, %r)", method, key)
        if method and hasattr(method, "__call__"):
            self.method = method
        else:
            self.method = None
        self.key = key
        self.cmd = cmd
        self.cmd_args = cmd_args if cmd_args else []
        self.conn = None

    def __get__(self, obj, type_=None):
        return functools.partial(self, obj)

    async def execute(self, cmd, key):
        """ raw execute of cmd on redis connection """
        result = await self.conn.execute(cmd, key, *self.cmd_args)
        LOGGER.debug("Result %s", result)
        return result

    async def _subscribe_(self, *args, **kwargs):
        """ read our queue and call our method """
        self.conn = await rd_session.pool()
        LOGGER.info("cmd %s to: %s", self.cmd, self.key)
        while True:
            document = await self.execute(self.cmd, self.key)
            LOGGER.debug("Got %s: %s", self.key, document)
            _args = list(args) + [document]
            if asyncio.iscoroutinefunction(self.method):
                asyncio.ensure_future(self.method(*_args, **kwargs))
            else:
                self.method(*_args, **kwargs)

    def __call__(self, *args, **kwargs):
        """ called to set us running """
        LOGGER.debug("__call__(%r, %r) %r", args, kwargs, self.method)
        if self.method is None:
            LOGGER.info("method null: %s", args)
            self.method = args[0]
            return self
        if self.key is None:
            self.key = self.method.__name__
        LOGGER.info("method %r", self.method)
        task = asyncio.ensure_future(self._subscribe_(*args, **kwargs))
        return task
