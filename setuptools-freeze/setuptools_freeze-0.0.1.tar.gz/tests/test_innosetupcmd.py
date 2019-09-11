import os
import unittest
from distutils.core import Distribution
from distutils.tests import support
from setuptools_freeze.integration import InnoSetupCmd


class InnoSetupCmdTest(unittest.TestCase):

    def test_basic(self):
        dist = Distribution({'name': 'mypackage','guid': '???'})
        cmd = InnoSetupCmd(dist)
        cmd._check()
        for key in ['author', 'url', 'version', 'guid']:
            self.assertIn(key, cmd.data)
        self.assertEqual('???', cmd.data['guid'])
