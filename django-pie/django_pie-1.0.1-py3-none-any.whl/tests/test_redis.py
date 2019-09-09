# coding: utf-8
import uuid
from django.test import TestCase

from django_pie.decorator import test_print
from django_pie.redis import redis_key, get_redis
from redis.exceptions import LockError


class TestRedis(TestCase):
    def setUp(self):
        pass

    @test_print
    def test_redis_key(self):
        key = redis_key('a', 'b', 'c')
        self.assertEqual(key, 'a:b:c')

    @test_print
    def test_get_redis(self):
        rds = get_redis()
        key = uuid.uuid4().hex
        value = 'foobar'
        rds.set(key, value)
        self.assertEqual(rds.get(key), value)
        rds.delete(key)

        # lock
        try:
            with rds.lock(key, timeout=5, blocking_timeout=1) as lock:
                print('get lock: %s', lock)
                raise LockError
        except LockError:
            print('do not get lock')

        self.assertEqual(rds.exists(key), False)
