#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `picturebot` package."""

import os
import unittest
import picturebot.helper as helper

class TestGeneralUtils(unittest.TestCase):

    def test_FullFilePathExists(self):
        '''Test the full file path'''

        # Obtain the expected full path
        pathExpected = os.path.join(os.path.dirname(helper.__file__), 'qq', 'ww', 'ee')
        # Obtain the returned path from the FullFilePathFunction
        pathTest = helper.FullFilePath('qq', 'ww', 'ee')

        self.assertEqual(pathExpected, pathTest, f'{pathTest} is not equal to {pathExpected}')

    def test_FullFilePathDoesNotExists(self):
        '''Negative test to check whether a certain full file path doesn't exists'''

        # Obtain the expected full path
        pathExpected = os.path.join(os.getcwd(), 'qq', 'ww', 'ee')
        # Obtain the returned path from the FullFilePathFunction
        pathTest = helper.FullFilePath('qq', 'ww', 'ee')

        self.assertNotEqual(pathExpected, pathTest, f'{pathTest} are equal {pathExpected}')

if __name__ == '__main__':
	unittest.main()
