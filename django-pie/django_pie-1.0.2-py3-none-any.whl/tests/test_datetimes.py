# coding: utf-8
import time
import datetime

from django.test import TestCase

from django_pie.decorator import test_print
from django_pie.datetimes import get_timestamp, timestamp_to_datetime


class TestDatetimes(TestCase):
    def setUp(self):
        pass

    @test_print
    def test_get_timestamp(self):
        t = get_timestamp()
        self.assertEqual(len(str(t)), 10)
        t = get_timestamp(ms=True)
        self.assertEqual(len(str(t)), 13)
        t = get_timestamp(t=datetime.datetime.now())
        self.assertEqual(len(str(t)), 10)
        t = get_timestamp(t='2019-01-01 12:01:02')
        self.assertEqual(len(str(t)), 10)

    @test_print
    def test_timestamp_to_datetime(self):
        now = datetime.datetime.now()
        ts = get_timestamp(t=now)
        dt = timestamp_to_datetime(ts, to_str=True)
        self.assertEqual(now.strftime('%Y-%m-%d %H:%M:%S'), dt)
        dt = timestamp_to_datetime(ts)
        self.assertEqual(now.strftime('%Y-%m-%d %H:%M:%S'), dt.strftime('%Y-%m-%d %H:%M:%S'))
