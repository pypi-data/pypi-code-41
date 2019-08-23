import os
import shutil
import tempfile
import time
import unittest

import pymq
import redislite
from pymq.provider.redis import RedisConfig


class TestResource(object):

    def setUp(self):
        pass

    def tearDown(self):
        pass


class RedisResource(TestResource):
    tmpfile: str
    rds: redislite.Redis

    def setUp(self):
        self.tmpfile = tempfile.mktemp('.db', 'symmetry_test_')
        self.rds = redislite.Redis(self.tmpfile, decode_responses=True)
        self.rds.get('dummykey')  # run a first command to initiate

    def tearDown(self):
        self.rds.shutdown()

        os.remove(self.tmpfile)
        os.remove(self.rds.redis_configuration_filename)
        os.remove(self.rds.settingregistryfile)
        shutil.rmtree(self.rds.redis_dir)

        self.rds = None
        self.tmpfile = None


class AppTestCase(unittest.TestCase):
    redis = RedisResource()
    eventbus: pymq.EventBus

    @classmethod
    def setUpClass(cls) -> None:
        cls.redis.setUp()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.redis.tearDown()

    def setUp(self) -> None:
        self.eventbus = pymq.init(RedisConfig(self.redis.rds))

    def tearDown(self) -> None:
        pymq.shutdown()
        self.redis.rds.flushall()


def poll(fn, timeout, period=0.02):
    """
    Periodically checks whether the given function returns something, until the timeout is reached at which point a
    TimeoutError is raised.

    :param fn: the function to poll
    :param timeout: the timeout (in seconds)
    :param period: the period at which to poll (in seconds), default is 20ms
    :return: the result of the function
    """
    remaining = timeout

    while remaining > 0:
        result = fn()
        if result:
            return result

        time.sleep(period)
        remaining -= period

    raise TimeoutError
