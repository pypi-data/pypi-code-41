# PyRDMIA Python Library 2018
# RDM-IA implementation by
# Dirceu Maraschin Jr
# Lucas Tortelli

from .core import Rdmia
from .utils import *
from .regression import RLS

def _test():
    from doctest import DocTestSuite
    from inspect import getmodule
    from os import walk
    from os.path import abspath, dirname, join
    from unittest import TestSuite, TextTestRunner
    test_suite = TestSuite()
    for root, dirs, files in walk(dirname(abspath(__file__))):
        module_files = [join(root, file) for file in files if \
            file.endswith(".py")]
        test_suite.addTests(DocTestSuite(getmodule(None, file)) for file in \
            module_files)
    TextTestRunner().run(test_suite)


if __name__ == "__main__":
    _test()
