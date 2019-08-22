# -*- coding: utf-8 -*-
"""
rate limiting with leaky bucket algorithm
"""
import time
import logging

__author__ = 'christian'
__created__ = '06.08.17'


class LeakyBucketRateLimiter(object):
    """
    Leaky Bucket Algorithm based rate limiter including a hourly bucket limit

    >>> from pyleakybucket.ratelimiting import LeakyBucketRateLimiter
    >>> from redis import StrictRedis
    >>> redis = StrictRedis()
    >>> limiter = LeakyBucketRateLimiter(redis)
    >>> limiter.acquire("my_request", 10, 1000, 20, consumer_name="Consumer")

    >>> for i in range(11):
    ...     print(limiter.acquire("my_request", 10, 1000, 20, consumer_name="Consumer"))
    ...
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (False, 0.985522985458374)
    >>> for i in range(11):
    ...     print(limiter.acquire("my_request", 10, 1000, 20, consumer_name="Consumer"))
    ...
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (False, 3563.840945959091)
    """
    EXPIRE_TIME_HOUR = 60 * 60  # a complete hour has 3600 seconds

    def __init__(self, redis, ):
        """
        rate limiter will use a redis connection

        :param redis: Redis Connection object i.e. StrictRedis
        """
        self.logger = logging.getLogger(__name__)
        self.redis = redis

    def acquire(self, request_name, bucket_size, restore_rate, max_hourly, consumer_name="default"):
        """
        acquire a free bucket for the given request

        :param request_name: request name as string
        :type request_name: str
        :param bucket_size: maximum amount of request (bucket size)
        :type bucket_size: int
        :param restore_rate: in 1/1000 seconds, 5 items per second == 200
        :type restore_rate: int
        :param max_hourly: hard limit of requests per hour
        :type max_hourly: int
        :param consumer_name: optional consumer name (defaults to "default")
                              to handle multiple consumers
        :returns: True if a free bucket slot was acquired, False if blocked + blocking time
        :rtype: tuple
        """
        self.logger.info("%s::acquire: [request: %s] [consumer: %s]",
                         self.__class__.__name__, request_name, consumer_name)
        available, wait_time = self._find_bucket_slot(request_name, bucket_size, restore_rate,
                                                      max_hourly, consumer_name)
        self.logger.info(
            "%s::acquire: [request: %s] [consumer: %s] [available: %s] [wait_time: %s]",
            self.__class__.__name__, request_name, consumer_name, available, wait_time)
        return available, wait_time

    def _find_bucket_slot(self, request_name, bucket_size, restore_rate, max_hourly, consumer_name):
        """
        find a free bucket slot or returns false if not found + wait time

        :param request_name: request name as string
        :type request_name: str
        :param bucket_size: maximum amount of request (bucket size)
        :type bucket_size: int
        :param restore_rate: in 1/1000 seconds, 5 items per second == 200
        :type restore_rate: int
        :param max_hourly: hard limit of requests per hour
        :type max_hourly: int
        :param consumer_name: consumer name (defaults to "default")
                              to handle multiple consumers
        :returns: True if a free slot was found, False otherwise + wait time in seconds
        :rtype: tuple
        """
        restore_rate = float(restore_rate) / float(1000)
        log_key = "{consumer_name}:{request_name}".format(consumer_name=consumer_name,
                                                          request_name=request_name)
        hourly_log_key = "hourly_" + log_key
        lock_key = "{log_key}:lock".format(log_key=log_key)
        ttl = max(int(bucket_size * restore_rate), 1)  # ttl at least 1 second
        self.logger.debug(
            "%s::_find_bucket_slot: start for [log_key: %s] with [bucket_size: %s] and "
            "[restore_rate: %s] and [hourly: %s]",
            self.__class__.__name__, log_key, bucket_size, restore_rate, max_hourly)

        with self.redis.lock(lock_key, timeout=10):
            self.logger.debug("%s::_find_bucket_slot: locked for [lock_key: %s]",
                              self.__class__.__name__, lock_key)
            llen = self.redis.llen(log_key)
            hourly_llen = self.redis.llen(hourly_log_key)
            newest = self.redis.lindex(log_key, 0)
            oldest = self.redis.lindex(log_key, -1)
            hourly_oldest = self.redis.lindex(hourly_log_key, -1)
            self.logger.debug("%s::_find_bucket_slot: [llen: %s] [hourly_llen: %s]",
                              self.__class__.__name__, llen, hourly_llen)
            now = time.time()
            is_full, wait_time = self._is_hourly_list_full(hourly_log_key, hourly_llen,
                                                           max_hourly, hourly_oldest, now)
            if is_full:
                return False, wait_time

            is_full, wait_time = self._is_list_full(llen, bucket_size, oldest, now)
            if is_full:
                return False, wait_time

            expires_at = now + restore_rate  # new element will expire after restore time
            if llen > 0:
                newest = float(newest)
                if newest > now:
                    # new element will expire after the previous element has expired + restore time
                    expires_at = newest + restore_rate

            self.logger.debug("%s::_find_bucket_slot: list free, new element [expires_at: %s]",
                              self.__class__.__name__, expires_at)

            self._set_new_expiry(
                log_key, hourly_log_key, expires_at, bucket_size, hourly_llen, ttl
            )
            return True, 0

    def _is_hourly_list_full(self, hourly_log_key, hourly_llen, max_hourly, hourly_oldest,
                             now):
        """
        returns a True + wait time > 0 if the hourly list is full, False + 0 otherwise

        :param hourly_log_key: redis key for hourly bucket
        :param hourly_llen: current number of elements in the hourly bucket
        :type hourly_llen: int
        :param max_hourly: hourly bucket size
        :type max_hourly: int
        :param hourly_oldest: oldest element (timestamp) of the hourly bucket
        :param now: current timestamp
        :type now: float
        :returns: True if the hourly bucket is full, False otherwise + wait time in seconds
        :rtype: tuple
        """
        if hourly_llen >= max_hourly:
            hourly_end = float(hourly_oldest) + self.EXPIRE_TIME_HOUR
            self.logger.debug(
                "%s::_is_hourly_list_full: [start: %s] [end: %s]",
                self.__class__.__name__, hourly_oldest, hourly_end)
            if now <= hourly_end:
                wait_time = hourly_end - now
                self.logger.debug("%s::_is_hourly_list_full: list blocked [wait_time: %s]",
                                  self.__class__.__name__, wait_time)
                return True, wait_time
            else:
                self.redis.delete(hourly_log_key)
        return False, 0

    def _is_list_full(self, llen, bucket_size, oldest, now):
        """
        returns a True + wait time > 0 if the list is full, False + 0 otherwise

        :param llen: current number of elements in the bucket
        :type llen: int
        :param bucket_size: bucket size
        :type bucket_size: int
        :param oldest: oldest element (timestamp) of the bucket
        :param now: current timestamp
        :type now: float
        :returns: True if the bucket is full, False otherwise + wait time in seconds
        :rtype: tuple
        """
        if llen >= bucket_size:
            oldest_time_difference = now - float(oldest)
            self.logger.debug("%s::_is_list_full: [oldest_time_difference: %s]",
                              self.__class__.__name__, oldest_time_difference)
            if oldest_time_difference < 0:
                # if the oldest element is not yet expired there is no free space in the bucket
                wait_time = abs(oldest_time_difference)
                self.logger.debug("%s::_is_list_full: list blocked [wait_time: %s]",
                                  self.__class__.__name__, wait_time)
                return True, wait_time
        return False, 0

    def _set_new_expiry(self, log_key, hourly_log_key, expires_at, bucket_size, hourly_llen,
                        ttl):
        """
        set new expire times by adding a new element to the lists

        :param log_key: redis bucket key
        :param hourly_log_key: redis key for hourly bucket
        :param expires_at: new expiry timestamp
        :param bucket_size: bucket size
        :param hourly_llen: current number of elements in the hourly bucket
        :type hourly_llen: int
        :param ttl: time to live for redis bucket in seconds
        :type ttl: int
        """
        self.redis.lpush(log_key, expires_at)
        self.redis.lpush(hourly_log_key, time.time())

        # there is no need to store more elements than the bucket size
        self.redis.ltrim(log_key, 0, bucket_size - 1)

        # expire the complete bucket if it is not used anymore
        self.redis.expire(log_key, ttl)

        # start a new hourly-bucket session with the first new element and expire after 60 mins
        if hourly_llen == 0:
            self.redis.expire(hourly_log_key, self.EXPIRE_TIME_HOUR)
