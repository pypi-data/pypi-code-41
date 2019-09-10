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

import numpy as np
import unittest
from eadf.eadf import *
from eadf.arrays import *
from unittest.mock import patch


class TestInit(unittest.TestCase):
    @patch('builtins.print')
    def test_InitFail1(self, mock):
        EADF(
            np.ones((39, 40, 2, 1, 10)),
            np.ones(40),
            np.ones(20),
            np.ones(1),
            np.random.randn(3, 10)
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_InitFail2(self, mock):
        EADF(
            np.ones((40, 40, 2, 1, 10)),
            np.ones(39),
            np.ones(20),
            np.ones(1),
            np.random.randn(3, 10)
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_InitFail3(self, mock):
        EADF(
            np.ones((40, 40, 2, 1, 10)),
            np.ones(40),
            np.ones(20),
            np.ones(2),
            np.random.randn(3, 10)
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_InitFail4(self, mock):
        EADF(
            np.ones((40, 40, 2, 1, 10)),
            np.ones(40),
            np.ones(20),
            np.ones(1),
            np.random.randn(2, 10)
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_InitFail5(self, mock):
        EADF(
            np.ones((40, 40, 2, 1, 10)),
            np.ones(40),
            np.ones(20),
            np.ones(1),
            np.random.randn(2, 10)
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_InitFail6(self, mock):
        EADF(
            np.ones((40, 40, 2, 1, 10)),
            np.ones(40),
            np.ones(20),
            np.ones(1),
            np.random.randn(3, 9)
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_InitFail7(self, mock):
        EADF(
            np.ones((40, 40, 2, 2, 10)),
            np.ones(40),
            np.ones(20),
            np.ones(2),
            np.random.randn(3, 10)
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_InitFailNone(self, mock):
        EADF(
            np.ones((40, 40, 2, 1, 10)),
            np.ones(40),
            np.ones(20),
            np.ones(1),
            np.random.randn(3, 10)
        )
        self.assertFalse(mock.called)


class TestProperties(unittest.TestCase):
    def setUp(self):
        self.antenna = EADF(
            np.ones((40, 40, 2, 1, 10)),
            np.ones(40),
            np.ones(20),
            np.ones(1),
            np.random.randn(3, 10)
        )

    def test_arrIndAziCompress(self):
        self.assertTrue(np.allclose(
            self.antenna.arrIndAziCompress,
            np.ones(40) > 0
        ))

    def test_arrIndEleCompress(self):
        self.assertTrue(np.allclose(
            self.antenna.arrIndEleCompress,
            np.ones(40) > 0
        ))

    def test_arrFourier(self):
        self.assertTrue(np.allclose(
            self.antenna.arrFourierData,
            np.fft.fft2(
                np.ones((40, 40, 2, 3, 10)),
                axes=(0, 1)
            ) / (40 * 40)
        ))

    def test_arrRawData(self):
        self.assertTrue(np.allclose(
            self.antenna.arrRawData,
            np.ones((40, 40, 2, 3, 10))
        ))

    def test_arrPos(self):
        self.assertEqual(self.antenna.arrPos.shape, (3, 10))

    def test_numElements(self):
        self.assertEqual(self.antenna.numElements, 10)

    def test_arrAngAzi(self):
        self.assertTrue(np.allclose(np.ones(40), self.antenna.arrAngAzi))

    def test_arrAngEle(self):
        self.assertTrue(np.allclose(np.ones(20), self.antenna.arrAngEle))

    def test_arrFreq(self):
        self.assertTrue(np.allclose(np.ones(1), self.antenna.arrFreq))

    def test_setCompressionFactor(self):
        self.uca = generateUniformArbitrary(
            np.random.randn(3, 32)
        )
        self.uca.compressionFactor = 0.99

        # test if the compression factor property was set correctly
        self.assertTrue(self.uca.compressionFactor > 0.99)

        # test if the subindices were calculated correctly
        self.assertTrue(
            np.sqrt(np.sum(np.linalg.norm(
                self.uca.arrFourierData[
                    self.uca.arrIndEleCompress
                ][
                    :,
                    self.uca.arrIndAziCompress,
                    ...
                ],
                axis=(0, 1)
            ) ** 2)) > 0.99
        )

    @patch('builtins.print')
    def test_setCompressionFactor_fail(self, mock):
        self.uca = generateUniformArbitrary(
            np.random.randn(3, 32)
        )
        self.uca.compressionFactor = -0.1
        self.assertTrue(self.uca.compressionFactor == 1.0)
        self.uca.compressionFactor = 1.1
        self.assertTrue(self.uca.compressionFactor == 1.0)
        self.assertTrue(mock.called)


class TestMethods(unittest.TestCase):
    def setUp(self):
        self.antenna = EADF(
            np.ones((40, 40, 2, 1, 10)),
            np.ones(40),
            np.ones(20),
            np.ones(1),
            np.random.randn(3, 10)
        )

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.scatter')
    def test_visualizeCut(self, scatter, show):
        self.antenna.visualizeCut(60, 1.67, [0], 1, list(range(3)))
        self.assertTrue(scatter.called)
        self.assertTrue(show.called)

    @patch('matplotlib.pyplot.show')
    def test_visualize2D(self, mock):
        self.antenna.visualize2D(40, 20, 0, 1, [0])
        self.assertTrue(mock.called)

    @patch('matplotlib.pyplot.show')
    def test_visualize3D(self, mock):
        self.antenna.visualize3D(40, 20, 0, 1, [0])
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_sampleFail1(self, mock):
        self.antenna.sample(np.arange(5), np.arange(5), 0)
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_sampleFail2(self, mock):
        self.antenna.sample(np.arange(5), np.arange(5), 2)
        self.assertTrue(mock.called)

    def test_sample(self):
        self.antenna.sample(np.arange(5), np.arange(5), 1)

    def test_sampleDeriv(self):
        self.antenna.sampleDerivative(np.arange(5), np.arange(5), 1)

    @patch('builtins.print')
    def test_initEvenFail(self, mock):
        EADF(
            np.ones((4, 6, 2, 6, 5)),
            np.arange(4),
            np.arange(2),
            np.arange(2),
            np.random.randn(3, 5)
        )
        self.assertTrue(mock.called)


if __name__ == '__main__':
    unittest.main()
