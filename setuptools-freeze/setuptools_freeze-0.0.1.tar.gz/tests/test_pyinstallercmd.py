import os
import unittest
from distutils.core import Distribution
from setuptools_freeze.integration import PyInstallerCmd


class PyInstallerCmdTest(unittest.TestCase):

    def test_basic(self):
        dist = Distribution({
            'entry_points': {
                'console_scripts': ['name=package:main']
            }
        })
        cmd = PyInstallerCmd(dist)
        name, module, func = next(cmd._get_console_scripts())
        self.assertEqual('name', name)
        self.assertEqual('package', module)
        self.assertEqual('main', func)
