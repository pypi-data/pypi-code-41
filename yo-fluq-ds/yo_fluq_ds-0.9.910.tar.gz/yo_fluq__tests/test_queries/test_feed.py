from yo_fluq import *
from unittest import TestCase

class TestFeed(TestCase):
    def test_feed_and_continue(self):
        q = Query.args(1,2,3,4).feed_fluent(Query.push()).split_by_group(lambda z: z%2).sum().execute()
        self.assertDictEqual({0:6,1:4}, q)
