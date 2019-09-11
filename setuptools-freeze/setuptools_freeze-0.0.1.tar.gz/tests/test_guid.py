import unittest
from setuptools_freeze.integration import guid

class Dummy: pass

class guidTest(unittest.TestCase):

    def test_basic(self):
        dist = Dummy()
        setattr(dist, 'metadata', Dummy())
        guid(dist, '', '???')
        self.assertEqual('???', dist.metadata.guid)
