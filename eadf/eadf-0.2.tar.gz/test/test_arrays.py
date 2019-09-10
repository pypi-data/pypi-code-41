# Copyright 2019 S. Pawar, S. Semper
#     https://www.tu-ilmenau.de/it-ems/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import numpy as np
from eadf.arrays import *
from unittest.mock import patch


class TestURA(unittest.TestCase):
    def setUp(self):
        self.array = generateURA(5, 6, 0.5, 0.75)

    def test_numElements(self):
        self.assertEqual(self.array.numElements, 5 * 6)

    def test_arrPosSize(self):
        self.assertEqual(self.array.arrPos.shape, (3, 5 * 6))

    @patch('builtins.print')
    def test_numElementsXFail(self, mock):
        self.array = generateURA(-5, 6, 0.5, 0.5)
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_numSpacingXFail(self, mock):
        self.array = generateURA(5, 6, -0.5, 0.5)
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_numElementsYFail(self, mock):
        self.array = generateURA(5, -6, 0.5, 0.5)
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_numSpacingYFail(self, mock):
        self.array = generateURA(5, 6, 0.5, -0.5)
        self.assertTrue(mock.called)


class TestULA(unittest.TestCase):
    def setUp(self):
        self.array = generateULA(11, 0.5)

    def test_numElements(self):
        self.assertEqual(self.array.numElements, 11)

    def test_arrPosSize(self):
        self.assertEqual(self.array.arrPos.shape, (3, 11))

    @patch('builtins.print')
    def test_numElementsFail(self, mock):
        self.array = generateULA(-11, 0.5)
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_numSpacingFail(self, mock):
        self.array = generateULA(11, -0.5)
        self.assertTrue(mock.called)


class TestUCA(unittest.TestCase):
    def setUp(self):
        self.array = generateUCA(11, 0.5)

    def test_numElements(self):
        self.assertEqual(self.array.numElements, 11)

    def test_arrPosSize(self):
        self.assertEqual(self.array.arrPos.shape, (3, 11))

    @patch('builtins.print')
    def test_numElementsFail(self, mock):
        self.array = generateUCA(-11, 0.5)
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_numRadiusFail(self, mock):
        self.array = generateUCA(11, -0.5)
        self.assertTrue(mock.called)


class TestStackedUCA(unittest.TestCase):
    def setUp(self):
        self.array = generateStackedUCA(11, 3, 0.5, 0.5)

    def test_numElements(self):
        self.assertEqual(self.array.numElements, 11 * 3)

    def test_arrPosSize(self):
        self.assertEqual(self.array.arrPos.shape, (3, 11 * 3))

    @patch('builtins.print')
    def test_numElementsFail(self, mock):
        self.array = generateStackedUCA(-11, 3, 0.5, 0.5)
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_numStacksFail(self, mock):
        self.array = generateStackedUCA(11, -3, 0.5, 0.5)
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_numRadiusFail(self, mock):
        self.array = generateStackedUCA(11, 3, -0.5, 0.5)
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_numHeightFail(self, mock):
        self.array = generateStackedUCA(11, 3, 0.5, -0.5)
        self.assertTrue(mock.called)


class TestUniformArbitrary(unittest.TestCase):
    def setUp(self):
        self.array = generateUniformArbitrary(
            np.random.randn(3, 10)
        )

    def test_numElements(self):
        self.assertEqual(self.array.numElements, 10)

    def test_arrPosSize(self):
        self.assertEqual(self.array.arrPos.shape, (3, 10))

    @patch('builtins.print')
    def test_arrPosFail(self, mock):
        generateUniformArbitrary(
            np.random.randn(2, 10)
        )
        self.assertTrue(mock.called)


if __name__ == '__main__':
    unittest.main()
