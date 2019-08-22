# -*- coding: utf-8 -*-
"""
integration test throttling ratelimit
"""
import time
import unittest

import fakeredis

from pyleakybucket.ratelimiting import LeakyBucketRateLimiter

__author__ = 'christian'
__created__ = '02.09.17'


class LockingFakeRedis(fakeredis.FakeStrictRedis):
    def lock(self, key, timeout=None):
        return LockObject()


class LockObject(object):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class TestLeakyBucketRateLimiter(unittest.TestCase):
    def setUp(self):
        self.redis = LockingFakeRedis()
        self.ratelimiter = LeakyBucketRateLimiter(self.redis)

    def tearDown(self):
        self.redis.flushdb()

    def test_01_acquire_simple(self):
        """
        a simple api request should be ok
        """
        result = self.ratelimiter.acquire("my_api_request", 5, 1000, 10, consumer_name="TEST")
        self.assertEqual(result, (True, 0))

    def test_02_acquire_many(self):
        """
        many request should lead to a throttle after the 5th request
        """
        request_name = "my_api_request"
        bucket_size = 5
        restore_rate = 1000
        max_hourly = 20
        for _counter in range(5):
            self.ratelimiter.acquire(
                request_name, bucket_size, restore_rate, max_hourly, consumer_name="TEST"
            )

        result = self.ratelimiter.acquire(
            request_name, bucket_size, restore_rate, max_hourly, consumer_name="TEST"
        )
        self.assertFalse(result[0])  # the 6th request is throttled
        time.sleep(restore_rate / 1000)

        result = self.ratelimiter.acquire(
            request_name, bucket_size, restore_rate, max_hourly, consumer_name="TEST"
        )
        self.assertEqual(result, (True, 0))  # after leaking a while, the next request is ok again

    def test_03_acquire_many_hourly_exceeded(self):
        """
        many request can lead to a hourly blocking if this limit is reached
        """
        request_name = "my_api_request"
        max_amount = 10
        restore_rate = 1000
        max_hourly = 5
        for _counter in range(5):
            result = self.ratelimiter.acquire(
                request_name, max_amount, restore_rate, max_hourly, consumer_name="TEST"
            )
            self.assertTrue(result[0])

        result = self.ratelimiter.acquire(
            request_name, max_amount, restore_rate, max_hourly, consumer_name="TEST"
        )
        self.assertFalse(result[0])
        # the 6th request is throttled because the hourly limit was reached

        time.sleep(restore_rate / 1000)
        result = self.ratelimiter.acquire(
            request_name, max_amount, restore_rate, max_hourly, consumer_name="TEST"
        )
        self.assertFalse(result[0])  # even leaking does not free up a new request

    def test_04_acquire_many_hourly_exceeded_and_reset(self):
        """
        many request can lead to a hourly blocking,
        but after that hour the requests will be ok again
        """
        request_name = "my_api_request"
        max_amount = 10
        restore_rate = 1000
        max_hourly = 5
        for _counter in range(5):
            self.ratelimiter.acquire(
                request_name, max_amount, restore_rate, max_hourly, consumer_name="TEST"
            )

        result = self.ratelimiter.acquire(
            request_name, max_amount, restore_rate, max_hourly, consumer_name="TEST"
        )
        self.assertFalse(result[0])  # the 6th request is blocked
        time.sleep(restore_rate / 1000)
        result = self.ratelimiter.acquire(
            request_name, max_amount, restore_rate, max_hourly, consumer_name="TEST"
        )
        self.assertFalse(result[0])  # and remains blocked

        self.ratelimiter.EXPIRE_TIME_HOUR = 1  # set hourly expire to 1 second

        result = self.ratelimiter.acquire(
            request_name, max_amount, restore_rate, max_hourly, consumer_name="TEST"
        )
        self.assertTrue(result[0])  # after the 'hour' has expired, new request will be ok
