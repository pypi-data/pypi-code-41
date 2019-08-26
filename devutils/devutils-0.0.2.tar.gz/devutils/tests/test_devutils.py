from unittest import TestCase

import devutils.utils
import sys

class Test(TestCase):
    def test_import(self):
        devutils.utils.add_sys_path("test_module")

        import test_module

        test_module.hello()
