import unittest
import sys
import os
import argparse
from pype.modules import profiles
from pype.utils.profiles import Profile, get_profiles

try:
    from cStringIO import StringIO
except:
    try:
        from StringIO import StringIO
    except:
        from io import StringIO


class TestProfiles(unittest.TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()
        self.parser = argparse.ArgumentParser(prog='pype', description='Test')
        self.subparsers = self.parser.add_subparsers(dest='modules')

    def test_get_profiles(self):
        profs = get_profiles({})
        self.assertEqual(profs['test'].info['description'], 'Test Profile')
        self.assertEqual(profs['test'].__name__, "test")
        self.assertTrue(isinstance(profs['test'], Profile))

    def test_profiles(self):
        profiles.profiles(None, self.subparsers, None, ['info', '-p', 'test'], None)
        self.assertEqual(sys.stdout.getvalue()[0:17], "Name       : test")

    def tearDown(self):
        sys.stdout = self.held


if __name__ == '__main__':
    unittest.main()
