#! /usr/bin/python3

import unittest
import doctest
import DNS
from DNS.tests import test_suite

unittest.TextTestRunner().run(test_suite())
