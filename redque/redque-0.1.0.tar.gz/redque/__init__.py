# -*- coding:utf-8 -*-

import logging
import redis

__version = (0, 1, 0)
__version__ = version = '.'.join(map(str, __version))

logger = logging.getLogger('redque')


def try_except(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except redis.exceptions.ConnectionError as e:
            logger.error("Redis Connection Error: {0}".format(e))
            raise e
    return wrapper


class Queue:
    def __init__(self, redis_conn, queue_name, process_queue_name):
        self._redis = redis_conn
        self._queue_name = queue_name
        self._process_queue_name = process_queue_name
        self._last_message = None

    @try_except
    def length(self):
        return self._redis.llen(self._queue_name)

    @try_except
    def clear(self, clear_process_queue=False):
        self._redis.delete(self._queue_name)

        if clear_process_queue:
            self._redis.delete(self._process_queue_name)

    def empty(self):
        return self.length() <= 0

    @try_except
    def push(self, item):
        self._redis.lpush(self._queue_name, item)

    @try_except
    def pop(self, block=True, timeout=None):
        self._last_message = self._redis.brpoplpush(
            self._queue_name, self._process_queue_name, timeout
        ) if block else self._redis.rpoplpush(
            self._queue_name, self._process_queue_name
        )
        return self._last_message

    @try_except
    def commit(self):
        self._redis.lrem(self._process_queue_name, 0, self._last_message)

    @try_except
    def refill(self):
        while (True):
            message = self._redis.lpop(self._process_queue_name)
            if not message:
                break
            self._redis.rpush(self._queue_name, message)

    def process(self, fun, block=True, timeout=None):
        while (True):
            message = self.pop(block, timeout)
            if not message:
                break
            if fun(message):
                self.commit()

    # compat python queue

    def qsize(self):
        return self.length()

    def put(self, item):
        return self.push(item)

    def get(self, block=True, timeout=None):
        return self.pop(block, timeout)

    def task_done(self):
        return self.commit()
