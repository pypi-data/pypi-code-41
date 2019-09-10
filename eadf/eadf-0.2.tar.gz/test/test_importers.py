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
from unittest.mock import patch
from eadf.importers import *
from eadf.arrays import *
import numpy as np


class TestFromAngleListData(unittest.TestCase):
    def setUp(self):
        # create a UCA and recreate it from its Fourier representation
        self.array1 = generateUCA(11, 1.5)
        self.arrAzi = np.random.uniform(0, 2 * np.pi, 240)
        self.arrEle = np.random.uniform(0, np.pi, 240)
        self.array2 = fromAngleListData(
            self.arrAzi,
            self.arrEle,
            self.array1.sample(self.arrAzi, self.arrEle, 1),
            self.array1.arrFreq,
            self.array1.arrPos,
            80,
            40,
            1e-1,
            method='SH'
        )

    def test_sampling(self):
        # test if the sampled values are the same for both arrays
        arrAzi, arrEle = sampleAngles(40, 20)
        arrAzi, arrEle = anglesToGrid(arrAzi, arrEle)
        # import matplotlib.pyplot as plt
        # plt.subplot(311)
        # plt.imshow(np.imag(
        #     self.array1.sample(arrAzi, arrEle)[:, 0, 0, 0].reshape(20, 40)
        # ))
        # plt.colorbar()
        # plt.subplot(312)
        # plt.imshow(np.imag(
        #     self.array2.sample(arrAzi, arrEle)[:, 0, 0, 0].reshape(20, 40)
        # ))
        # plt.colorbar()
        # plt.subplot(313)
        # plt.imshow(np.abs(
        #     self.array1.sample(arrAzi, arrEle)[:, 0, 0, 0].reshape(20, 40)
        #     - self.array2.sample(arrAzi, arrEle)[:, 0, 0, 0].reshape(20, 40)
        # ))
        # plt.colorbar()
        # plt.show()

        self.assertTrue(
            (np.linalg.norm(
                self.array1.sample(self.arrAzi, self.arrEle, 1) -
                self.array2.sample(self.arrAzi, self.arrEle, 1)
            ) / np.linalg.norm(
                self.array1.sample(self.arrAzi, self.arrEle, 1))
            ) < 0.1
        )

    @patch('builtins.print')
    def test_shapeFail1(self, mock):
        fromAngleListData(
            np.ones(3),
            np.ones(4),
            np.ones((4, 2, 3, 4)),
            np.ones(3),
            np.ones((3, 4)),
            80,
            40,
            1e-1,
            method='SH'
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_shapeFail2(self, mock):
        fromAngleListData(
            np.ones(4),
            np.ones(3),
            np.ones((4, 2, 3, 4)),
            np.ones(3),
            np.ones((3, 4)),
            80,
            40,
            1e-1,
            method='SH'
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_shapeFail3(self, mock):
        fromAngleListData(
            np.ones(4),
            np.ones(4),
            np.ones((3, 2, 3, 4)),
            np.ones(3),
            np.ones((3, 4)),
            80,
            40,
            1e-1,
            method='SH'
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_numFail1(self, mock):
        fromAngleListData(
            np.ones(3),
            np.ones(3),
            np.ones((3, 2, 3, 4)),
            np.ones(3),
            np.ones((3, 4)),
            -80,
            40,
            1e-1,
            method='SH'
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_numFail2(self, mock):
        fromAngleListData(
            np.ones(3),
            np.ones(3),
            np.ones((3, 2, 3, 4)),
            np.ones(3),
            np.ones((3, 4)),
            80,
            -40,
            1e-1,
            method='SH'
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_shapeFail4(self, mock):
        fromAngleListData(
            np.ones(4),
            np.ones(4),
            np.ones((4, 2, 3, 4)),
            np.ones(3),
            np.ones((3, 3)),
            80,
            40,
            1e-1,
            method='SH'
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_shapeFail5(self, mock):
        fromAngleListData(
            np.ones(4),
            np.ones(4),
            np.ones((4, 2, 3, 4)),
            np.ones(2),
            np.ones((3, 4)),
            80,
            40,
            1e-1,
            method='SH'
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_aziFail(self, mock):
        fromAngleListData(
            np.ones(4),
            np.ones(4),
            np.ones((4, 2, 3, 4)),
            np.ones(2),
            np.ones((3, 4)),
            -80,
            40,
            1e-1,
            method='SH'
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_eleFail(self, mock):
        fromAngleListData(
            np.ones(4),
            np.ones(4),
            np.ones((4, 2, 3, 4)),
            np.ones(2),
            np.ones((3, 4)),
            80,
            -40,
            1e-1,
            method='SH'
        )
        self.assertTrue(mock.called)


class TestFromFourierData(unittest.TestCase):
    def setUp(self):
        # create a UCA and recreate it from its Fourier representation
        self.array1 = generateUCA(11, 0.5)
        self.arrAzi = np.random.uniform(0, 2 * np.pi, 20)
        self.arrEle = np.random.uniform(0, np.pi, 20)
        self.array2 = fromFourierData(
            self.array1.arrFourierData,
            self.array1.arrFreq,
            self.array1.arrPos
        )

    def test_sampling(self):
        # test if the sampled values are the same for both arrays
        self.assertTrue(np.allclose(
            self.array1.sample(
                self.arrAzi, self.arrEle, self.array1.arrFreq[0]
            ),
            self.array2.sample(
                self.arrAzi, self.arrEle, self.array2.arrFreq[0]
            )
        ))

    @patch('builtins.print')
    def test_shapeFail1(self, mock):
        fromFourierData(
            np.ones((3, 8, 2, 3, 4)),
            np.ones(3),
            np.ones((3, 4))
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_shapeFail2(self, mock):
        fromFourierData(
            np.ones((4, 8, 2, 7, 4)),
            np.ones(3),
            np.ones((3, 4))
        )
        self.assertTrue(mock.called)

    @patch('builtins.print')
    def test_shapeFail3(self, mock):
        fromFourierData(
            np.ones((4, 8, 2, 3, 4)),
            np.ones(3),
            np.ones((3, 3))
        )
        self.assertTrue(mock.called)


if __name__ == '__main__':
    unittest.main()
