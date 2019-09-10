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
from eadf.arrays import *
from eadf.core import *
import unittest
from unittest.mock import patch


class TestFourierConversion(unittest.TestCase):
    @patch('builtins.print')
    def test_fourierToSampledFail1(self, mock):
        fourierToSampled(
            np.ones((3, 4, 2, 1, 5))
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_fourierToSampledFail2(self, mock):
        fourierToSampled(
            np.ones((4, 4, 2, 1))
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_fourierToSampledFail3(self, mock):
        fourierToSampled(
            np.ones((4, 4, 3, 1, 5))
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_sampledToFourierFail1(self, mock):
        sampledToFourier(
            np.ones((3, 4, 2, 1, 5))
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_sampledToFourierFail2(self, mock):
        sampledToFourier(
            np.ones((4, 4, 2, 1))
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_sampledToFourierFail3(self, mock):
        sampledToFourier(
            np.ones((4, 4, 3, 1, 5))
        )
        self.assertTrue(mock.called)


class TestAngleSampling(unittest.TestCase):
    def setUp(self):
        pass

    def test_sampleAngles(self):
        arrAngAzi, arrAngEle = sampleAngles(
            4, 4, lstEndpoints=[False, False]
        )
        self.assertTrue(
            np.allclose(
                np.linspace(0, 2 * np.pi, 4, endpoint=False),
                arrAngAzi
            )
        )
        self.assertTrue(
            np.allclose(
                np.linspace(0, np.pi, 4, endpoint=False),
                arrAngEle
            )
        )

        arrAngAzi, arrAngEle = sampleAngles(
            4, 4, lstEndpoints=[True, False]
        )
        self.assertTrue(
            np.allclose(
                np.linspace(0, 2 * np.pi, 4, endpoint=True),
                arrAngAzi
            )
        )
        self.assertTrue(
            np.allclose(
                np.linspace(0, np.pi, 4, endpoint=False),
                arrAngEle
            )
        )

        arrAngAzi, arrAngEle = sampleAngles(
            4, 4, lstEndpoints=[False, True]
        )

        self.assertTrue(
            np.allclose(
                np.linspace(0, 2 * np.pi, 4, endpoint=False),
                arrAngAzi
            )
        )
        self.assertTrue(
            np.allclose(
                np.linspace(0, np.pi, 4, endpoint=True),
                arrAngEle
            )
        )

        arrAngAzi, arrAngEle = sampleAngles(
            4, 4
        )
        self.assertTrue(
            np.allclose(
                np.linspace(0, 2 * np.pi, 4, endpoint=False),
                arrAngAzi
            )
        )
        self.assertTrue(
            np.allclose(
                np.linspace(0, np.pi, 4, endpoint=False),
                arrAngEle
            )
        )

    @patch('builtins.print')
    def test_sampleAnglesFailAzi(self, mock):
        sampleAngles(0, 4)
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_sampleAnglesFailEle(self, mock):
        sampleAngles(4, 0)
        self.assertTrue(mock.called)


class TestInterpolateSH(unittest.TestCase):
    def setUp(self):
        # sample and then interpolate
        self.array = generateUCA(11, 1.5)
        self.arrEle1 = np.linspace(0.1 * np.pi, 0.9 * np.pi, 20)
        self.arrAzi1 = np.linspace(0, 2 * np.pi, 40)
        self.arrAzi1, self.arrEle1 = anglesToGrid(self.arrAzi1, self.arrEle1)
        self.arrEle2 = np.random.uniform(0.1 * np.pi, 0.9 * np.pi, 15)
        self.arrAzi2 = np.random.uniform(0, 2 * np.pi, 15)
        self.numN = 15
        self.arrValues1 = self.array.sample(
            self.arrAzi1,
            self.arrEle1,
            1
        )[:, 0, 0, 0].flatten()
        self.arrValues2 = self.array.sample(
            self.arrAzi2,
            self.arrEle2,
            1
        )[:, 0, 0, 0].flatten()

    def test_sample_same(self):
        # sample at the same angles we used for fitting
        arrInter = interpolateDataSphere(
            self.arrAzi1,
            self.arrEle1,
            self.arrValues1,
            self.arrAzi1,
            self.arrEle1,
            method='SH',
            numN=self.numN
        ).flatten()
        self.assertTrue(
            ((np.linalg.norm(arrInter - self.arrValues1)
                / np.linalg.norm(arrInter)) < 0.1)
        )

    def test_sample_rnd(self):
        # sample at different angles, error will be higher.
        # TODO: investigate if high error is a bug or just bad fitting
        arrInter = interpolateDataSphere(
            self.arrAzi1,
            self.arrEle1,
            self.arrValues1,
            self.arrAzi2,
            self.arrEle2,
            method='SH',
            numN=self.numN
        ).flatten()

        # check if error is small enough
        self.assertTrue(
            ((np.linalg.norm(arrInter - self.arrValues2)
                / np.linalg.norm(arrInter)) < 0.1)
        )

    @patch('builtins.print')
    def test_interpolateDataSphereNumNFail(self, mock):
        interpolateDataSphere(
            np.arange(4),
            np.arange(4),
            np.arange(4),
            np.arange(4),
            np.arange(4),
            method='SH',
            numN=-1
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_interpolateSHShape1Fail(self, mock):
        interpolateDataSphere(
            np.arange(4),
            np.arange(3),
            np.arange(4),
            np.arange(4),
            np.arange(4),
            method='SH',
            numN=5
        )
        self.assertTrue(mock.called)


class TestSymmmetrizePattern(unittest.TestCase):
    @patch('builtins.print')
    def test_symmetrizePatternFail(self, mock):
        symmetrizePattern(np.random.randn(3, 4, 4, 5))
        self.assertTrue(mock.called)


class TestInterpolateDataSphere(unittest.TestCase):
    def setUp(self):
        # sample and then interpolate
        self.array = generateUCA(11, 1.5)
        self.arrEle1 = np.linspace(0.1 * np.pi, 0.9 * np.pi, 20)
        self.arrAzi1 = np.linspace(0, 2 * np.pi, 40)
        self.arrAzi1, self.arrEle1 = anglesToGrid(self.arrAzi1, self.arrEle1)
        self.arrEle2 = np.random.uniform(0.1 * np.pi, 0.9 * np.pi, 15)
        self.arrAzi2 = np.random.uniform(0, 2 * np.pi, 15)
        self.numN = 15
        self.arrValues1 = self.array.sample(
            self.arrAzi1,
            self.arrEle1,
            1
        )[:, 0, 0].flatten()
        self.arrValues2 = self.array.sample(
            self.arrAzi2,
            self.arrEle2,
            1
        )[:, 0, 0].flatten()

    @patch('builtins.print')
    def test_method(self, mock):
        interpolateDataSphere(
            self.arrAzi1,
            self.arrEle1,
            self.arrValues1,
            self.arrAzi2,
            self.arrEle2,
            numN=self.numN,
            method='foo'
        )
        self.assertTrue(mock.called)


class TestRegularSamplingToGrid(unittest.TestCase):
    def setUp(self):
        self.array = np.ones((20, 2, 2, 2))

    def test_normal(self):
        self.assertTrue(np.allclose(
            regularSamplingToGrid(self.array, 5, 4),
            np.ones((4, 5, 2, 2, 2))
        ))

    @patch('builtins.print')
    def test_shapeFail(self, mock):
        regularSamplingToGrid(np.ones((20, 2, 2)), 5, 4)
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_sizeFail(self, mock):
        regularSamplingToGrid(np.ones((19, 2, 2, 2)), 5, 4)
        self.assertTrue(mock.called)


class TestColumnwiseKron(unittest.TestCase):
    def setUp(self):
        self.A = np.ones((4, 5))
        self.B = np.ones((6, 5))
        self.C = np.ones((6, 7))

    def test_normal(self):
        res = columnwiseKron(self.A, self.B)
        self.assertTrue(res.shape[0] == 4 * 6)
        self.assertTrue(res.shape[1] == 5)
        self.assertTrue(np.allclose(
            res, np.ones((24, 5))
        ))

    @patch('builtins.print')
    def test_fail(self, mock):
        columnwiseKron(self.A, self.C)
        self.assertTrue(mock.called)


if __name__ == '__main__':
    unittest.main()
