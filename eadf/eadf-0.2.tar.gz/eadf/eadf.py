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
r"""
Main EADF Object Class
----------------------
"""

import numpy as np
from .core import *
from .plot import *


class EADF(object):
    @property
    def arrIndAziCompress(
        self
    ) -> np.ndarray:
        """Subselection indices for the compressed array in azimuth (ro)

        Returns
        -------
        np.ndarray
            Subselection in spatial Fourier domain in azimuth

        """
        return self._arrIndAziCompress

    @property
    def arrIndEleCompress(
        self
    ) -> np.ndarray:
        """Subselection indices for the compressed array in elevation (ro)

        Returns
        -------
        np.ndarray
            Subselection in spatial Fourier domain in elevation

        """
        return self._arrIndEleCompress

    @property
    def arrAngAzi(
        self
    ) -> np.ndarray:
        """Return Array Containing the sampled Azimuth Angles

        Returns
        -------
        np.ndarray
            Sampled Azimuth Angles

        """
        return self._arrAngAzi

    @property
    def arrAngEle(
        self
    ) -> np.ndarray:
        """Return Array Containing the sampled Co-Elevation Angles

        Returns
        -------
        np.ndarray
            Sampled Co-Elevation Angles

        """
        return self._arrAngEle

    @property
    def arrFreq(
        self
    ) -> np.ndarray:
        """Return Array Containing the Sampled Frequencies

        Returns
        -------
        np.ndarray
            Sampled Frequencies Angles

        """
        return self._arrFreq

    @property
    def numElements(
        self
    ) -> int:
        """Number of Array Elements (read only)

        Returns
        -------
        int
            Number of Antenna Elements

        """
        return self._numElements

    @property
    def arrFourierData(
        self
    ) -> np.ndarray:
        """Return the Fourier Data used to represent the antenna. (read only)

        Returns
        -------
        np.ndarray
            2D Fourier Data
        """

        return self._arrFourierData

    @property
    def arrPos(
        self
    ) -> np.ndarray:
        """Positions of the Elements as 3 x numElements

        Returns
        -------
        np.ndarray
            Positions of the Elements as 3 x numElements

        """

        return self._arrPos

    @property
    def arrRawData(
        self
    ) -> np.ndarray:
        """Return the Raw Data used during construction. (read only)

        Returns
        -------
        np.ndarray
            Raw Data in 2 * Co-Ele x Azi x Pol x Freq x Element
        """

        return self._arrRawData

    @property
    def compressionFactor(
        self
    ) -> float:
        """Compression Factor

        Returns
        -------
        float
            Compression factor in (0,1]

        """
        return self._compressionFactor

    @compressionFactor.setter
    def compressionFactor(
        self,
        numValue: float
    ) -> None:
        """Set the Compression Factor

        The EADF allows to reduce the number of parameters of a given
        beampattern by reducing the number of Fourier coefficients.
        This should be done carefully, since one should not throw away
        necessary information. So, we define a compression factor 'p', which
        determines how much 'energy' the remaining Fourier coefficients
        contain.
        So we have the equation: E_c = p * E, where 'E' is the energy of the
        uncompressed array.

        Parameters
        ----------
        numValue : float
            Factor to be set. Must be in (0,1]. The actual subselection
            is done such that the remaining energy is always greater or
            equal than the specified value, which minimizes the expected
            computation time.

        """
        if (numValue <= 0.0) or (numValue > 1.0):
            print("Supplied Value must be in (0, 1]")
        else:
            self._compressionFactor = self._setCompressionFactor(numValue)

    def _setCompressionFactor(
        self,
        numValue: float
    ) -> float:
        """Calculate Subselection-Indices

        This method takes the supplied compression factor, which is
        not with respect to the number of Fourier coefficients to use
        but rather the amount of energy still present in them. this is
        achieved by analysing the spatial spectrum of the whole array in the
        following way:
        1. Flip the spectrum all into one quadrant
        2. normalize it with respect to the complete energy
        3. find all combinations of subsizes in azimuth and elevation
        such that the energy is lower than numValue
        4. find the pair of elevation and azimuth index such that it
        minimizes the execution time during sampling

        Parameters
        ----------
        numValue : float
            Factor to be set. Must be in (0,1].

        Returns
        -------
        float
            Returns the actual compression factor

        """

        # calculate the energy of the whole array
        # first get the norm of each spectrum, then sum along
        # pol, freq and elem
        numTotalEnergy = np.sum(np.linalg.norm(
            self._arrFourierData,
            axis=(0, 1)
        ))

        # find the middle indices in the first two components
        middleAzi = int((self._numAziInit + (self._numAziInit % 2))/2)
        middleEle = int((self._numEleInit + (self._numEleInit % 2))/2)

        # first do the flipping, such that the spectra in all quadrants
        # overlap, then do cumulative sums in all direction
        # then we sum these results across pol, freq and elem
        # so for each element we have the relative energy
        # the array would contain if we selected this index as
        # bounds for the subselection
        arrFoldedFourierData = np.sum(np.sqrt(np.cumsum(
            np.cumsum(
                # top left, no flipping
                np.abs(self._arrFourierData[:middleEle, :middleAzi] ** 2)
                # bottom left, flip along elevation
                + np.abs(
                    self._arrFourierData[
                        middleEle:, :middleAzi
                    ][::-1, ...] ** 2
                )
                # top right, flip along azimuth
                + np.abs(
                    self._arrFourierData[
                        :middleEle, middleAzi:
                    ][:, ::-1, ...] ** 2
                )
                # bottom right, flip along elevation and azimuth
                + np.abs(
                    self._arrFourierData[
                        middleEle:, middleAzi:
                    ][::-1, ::-1, ...] ** 2
                ),
                axis=0
            ),
            axis=1
        )), axis=(2, 3, 4)) / numTotalEnergy

        # find all subarrays such that they have less energy than required
        # the others will be the ones that we might select from
        arrInFeasibleSizes = arrFoldedFourierData < numValue

        # cost function is just the product of the two indexes, since
        # we have to essentially do linear time operations when
        # sampling
        arrCost = np.outer(
            np.linspace(1, middleEle, middleEle),
            np.linspace(1, middleAzi, middleAzi)
        )

        # all infeasible indices will be set to infinity, such that
        # the are not considered when finding the optimal cost indices
        arrCost[arrInFeasibleSizes] = np.inf

        # find the minimum in the 2D array of cost values
        minCostInd = np.unravel_index(
            np.argmin(arrCost, axis=None),
            arrCost.shape
        )

        # now get the actual subselection arrays as booleans
        # here we have to apply the inverse fftshift
        # we have the +1, since minCostInd contains indices starting at
        # 0, but the linspace thingy is done from "1"
        self._arrIndAziCompress = np.fft.ifftshift(np.abs(np.linspace(
            -middleAzi,
            +middleAzi,
            self._numAziInit
        )) <= minCostInd[1] + 1)

        self._arrIndEleCompress = np.fft.ifftshift(np.abs(np.linspace(
            -middleEle,
            +middleEle,
            self._numEleInit
        )) <= minCostInd[0] + 1)

        # return the compression factor we determined
        return arrFoldedFourierData[minCostInd[0], minCostInd[1]]

    def sample(
        self,
        arrAngAzi: np.ndarray,
        arrAngEle: np.ndarray,
        numFreq: float
    ) -> np.ndarray:
        """Sample the Beampattern at Angles for a certain Frequency

        The supplied array need to have the same length. The returned
        array has again the same length. This method samples the EADF object
        for a given wave frequency for all polarizations and array elements.
        So it yields a Ang x Pol x Element np.ndarray. For the freqency
        interpolation, we use a linear interpolation scheme.

        Since we have no crystalline sphere to guess, we cannot do
        extrapolation, so the requested frequency has to be between the
        minimum and maximum frequency the array was excited with.

        Parameters
        ----------
        arrAngAzi : np.ndarray
            Sample at these azimuths
        arrAngEle : np.ndarray
            Sample at these elevations
        numFreq : float
            Sample at this frequency

        Returns
        -------
        np.ndarray
            Beampattern values at the requested angles

        """
        if numFreq < self._arrFreq[0]:
            print("sample: supplied frequency must be in sampled intervall")
            return
        if numFreq > self._arrFreq[-1]:
            print("sample: supplied frequency must be in sampled intervall")
            return
        # check if we are dealing with a narrowband array
        if self._arrFreq.shape[0] == 1:
            # check if we asked for the wrong frequency
            if numFreq != self._arrFreq[0]:
                print("sample:")
                print("antennna was excited with only one freq. this wasnt it")
                return
            else:
                # if not, we basically have to do no interpolation
                arrFreqInd = np.array([0])
                arrInterWeights = np.array([1])
        else:
            # we start with a simple linear interpolation
            # this should be switched out with methods that generate
            # interpolation weights and so forth for higher order methods
            numInd2 = np.min(np.arange(
                self._arrFreq.shape[0])[self._arrFreq > numFreq]
            )
            numInd1 = numInd2 - 1

            arrFreqInd = np.array([numInd1, numInd2])
            arrInterWeights = np.array([
                self._arrFreq[numInd2] - numFreq,
                numFreq - self._arrFreq[numInd1]
            ]) / self._arrFreq[numInd2] - self._arrFreq[numInd1]

        # now we evaluate the pattern and return it's interpolation
        arrA = evaluatePattern(
            arrAngAzi,
            arrAngEle,
            self._muAzi[self._arrIndAziCompress],
            self._muEle[self._arrIndEleCompress],
            arrFreqInd,
            self._arrFourierData[
                self._arrIndEleCompress
            ][:, self._arrIndAziCompress]
        )

        return np.expand_dims(
            np.average(arrA, axis=2, weights=arrInterWeights), axis=2
        )

    def sampleDerivative(
        self,
        arrAngAzi: np.ndarray,
        arrAngEle: np.ndarray,
        numFreq: float
    ) -> np.ndarray:
        """Sample the Beampattern's Derivative with respect to Angles

        The supplied arrays need to have the same length. The returned
        arrays in the tuple have again the same length. This method samples
        the EADF object for a given wave frequency all polarizations and
        array elements. So it yields a Ang x Pol x Element np.ndarray
        in both tuple entries.

        Since we have no crystalline sphere to guess, we cannot do
        extrapolation, so the requested frequency has to be between the
        minimum and maximum frequency the array was excited with.

        Parameters
        ----------
        arrAngAzi : np.ndarray
            Sample at these azimuths
        arrAngEle : np.ndarray
            Sample at these elevations
        numFreq : float
            Sample at this frequency

        Returns
        -------
        (np.ndarray, np.ndarray)
            Tuple of the two derivative vectors (azi, ele)

        """
        if numFreq < self._arrFreq[0]:
            print("sample: supplied frequency must be in sampled intervall")
            return
        if numFreq > self._arrFreq[-1]:
            print("sample: supplied frequency must be in sampled intervall")
            return
        # check if we are dealing with a narrowband array
        if self._arrFreq.shape[0] == 1:
            # check if we asked for the wrong frequency
            if numFreq != self._arrFreq[0]:
                print("sample:")
                print("antennna was excited with only one freq. this wasnt it")
                return
            else:
                # if not, we basically have to do no interpolation
                arrFreqInd = np.array([0])
                arrInterWeights = np.array([1])
        else:
            # we start with a simple linear interpolation
            # this should be switched out with methods that generate
            # interpolation weights and so forth for higher order methods
            numInd2 = np.min(np.arange(
                self._arrFreq.shape[0])[self._arrFreq > numFreq]
            )
            numInd1 = numInd2 - 1

            arrFreqInd = np.array([numInd1, numInd2])
            arrInterWeights = np.array([
                self._arrFreq[numInd2] - numFreq,
                numFreq - self._arrFreq[numInd1]
            ]) / self._arrFreq[numInd2] - self._arrFreq[numInd1]

        # evaulate the derivative
        arrDerivAzi, arrDerivEle = evaluatePatternDerivative(
            arrAngAzi,
            arrAngEle,
            self._muAzi[self._arrIndAziCompress],
            self._muEle[self._arrIndEleCompress],
            arrFreqInd,
            self._arrFourierData[
                self._arrIndEleCompress
            ][:, self._arrIndAziCompress]
        )

        return((
            np.expand_dims(
                np.average(arrDerivAzi, axis=2, weights=arrInterWeights),
                axis=2
            ),
            np.expand_dims(
                np.average(arrDerivEle, axis=2, weights=arrInterWeights),
                axis=2
            )
        ))

    def visualizeCut(
        self,
        numAzi: int,
        numAngEle: float,
        numPol: list,
        numFreq: float,
        arrIndElem: list,
        fun=None
    ) -> None:
        """Visualize the Beampattern Along a Certain Angle of Co-Elevation

        This plots several beam patterns along one co-elevation level.
        It also positions the elements in the correct 2D-position from top
        down.

        Example
        -------
        >>> import eadf
        >>> A = eadf.arrays.generateStackedUCA(11, 3, 1.5, 0.5)
        >>> A.visualizeCut(60, 1.67, [0], 0, list(range(11)))

        Parameters
        ----------
        numAzi : int
            Number of regularly spaced azimuth grid points
        numAngEle : float
            Co-Elevation angle to make the cut at
        numPol : list
            Can be either [0], [1] or [0,1]. Selects the polarizations
        numFreq : float
            Freqency to plot
        arrIndElem : list
            Antenna elements to plot
        fun : method
            function to apply to the elements values
            right before plotting. popular choices are np.real or np.imag
            if not specified we use np.abs( . )

        """

        # sample the angles on a regular grid
        arrAngAzi, arrAngEle = sampleAngles(
            numAzi, 1, lstEndpoints=[True, False]
        )

        # set the elevation angle array to the specified elevation
        # angle
        arrAngEle[:] = numAngEle

        # now generate the grid
        grdAngAzi, grdAngEle = anglesToGrid(arrAngAzi, arrAngEle)

        # now sample the array values on the grid
        arrPlotData = self.sample(grdAngAzi, grdAngEle, numFreq)

        plotCut2D(
            # now subselect the samples values to the specified
            # polarisation, elements and frequency (the 0)
            arrPlotData[
                :, numPol, 0, arrIndElem
            ].reshape((-1, 1, len(arrIndElem))),
            grdAngAzi,
            self._arrPos[:, arrIndElem],
            fun
        )

    def visualize2D(
        self,
        numAzi: int,
        numEle: int,
        numPol: int,
        numFreq: float,
        arrIndElem: list,
        fun=None
    ) -> None:
        """Plot an Image of several Elements' Beampatterns

        Example
        -------

        >>> import eadf
        >>> A = eadf.arrays.generateStackedUCA(11, 3, 1.5, 0.5)
        >>> A.visualize2D(40, 20, 0, 0, [0])

        Parameters
        ----------
        numAzi : int
            number of samples in azimuth direction
        numEle : int
            number of samples in co-elevation direction
        numPol : int
            polarisation 0, or 1?
        numFreq : float
            Frequency to plot at
        arrIndElem : list
            Description of parameter `arrIndElem`.
        fun : method
            function to apply to the elements values
            right before plotting. popular choices are np.real or np.imag
            if not specified we use np.abs( . )
        """

        arrAngAzi, arrAngEle = sampleAngles(
            numAzi, numEle, lstEndpoints=[True, True]
        )
        grdAngAzi, grdAngEle = anglesToGrid(arrAngAzi, arrAngEle)
        arrPlotData = self.sample(grdAngAzi, grdAngEle, numFreq)

        plotBeamPattern2D(
            arrPlotData[:, numPol, 0, arrIndElem],
            grdAngAzi,
            grdAngEle,
            numAzi,
            numEle
        )

    def visualize3D(
        self,
        numAzi: int,
        numEle: int,
        numPol: int,
        numFreq: float,
        arrIndElem: list,
        fun=None
    ) -> None:
        """Plot the Array with 3D Beampatterns

        We first sample the array for on a regular grid in co-elevation
        and azimuth and then we put deformed spheres at the elements
        positions to represent the array elements. for this a fixed
        polarization and a fixed wave-frequency have to be selected.

        Example
        -------

        >>> import eadf
        >>> A = eadf.arrays.generateStackedUCA(11, 3, 1.5, 0.5)
        >>> A.visualize3D(40, 20, 0, 0, [0])

        Parameters
        ----------
        numAzi : int
            number of samples in azimuth direction
        numEle : int
            number of samples in co-elevation direction
        numPol : int
            polarisation 0, or 1?
        numFreq : float
            Frequency to sample at
        arrIndElem : list
            Description of parameter `arrIndElem`.
        fun : method
            function to apply to the elements values
            right before plotting. popular choices are np.real or np.imag
            if not specified we use np.abs( . )
        """

        arrAngAzi, arrAngEle = sampleAngles(
            numAzi, numEle, lstEndpoints=[True, True]
        )
        grdAngAzi, grdAngEle = anglesToGrid(arrAngAzi, arrAngEle)
        arrPlotData = self.sample(grdAngAzi, grdAngEle, numFreq)

        plotBeamPattern3D(
            # the 0 picks out the one frequency we sampled at
            arrPlotData[:, numPol, 0, arrIndElem],
            grdAngAzi,
            grdAngEle,
            self._arrPos[:, arrIndElem],
            numAzi,
            numEle
        )

    def __init__(
        self,
        arrData: np.ndarray,
        arrAngAzi: np.ndarray,
        arrAngEle: np.ndarray,
        arrFreq: np.ndarray,
        arrPos: np.ndarray
    ) -> None:
        """Initialize an EADF Object

        Here we assume that the input data is given in the internal data
        format already. If you have antenna data, which is not in the
        internat data format, we advice you to use one of the importers,
        or implement your own.

        Parameters
        ----------
        arrData : np.ndarray
            2 * Co-Ele x Azi x Pol x Freq x Element
        arrAngAzi : np.ndarray
            Azimuth sampling positions.
        arrAngEle : np.ndarray
            Co-elevation sampling positions.
        arrFreq : np.ndarray
            Frequencies sampled at.
        arrPos : np.ndarray
            (3 x numElements) Positions of the single antenna elements.
            this is just for vizualisation purposes.
        """

        if (arrData.shape[0] % 2 != 0):
            print("EADF: arrData.shape[0] must be even.")
            return
        if arrAngAzi.shape[0] != arrData.shape[1]:
            print("EADF: arrData.shape[1](%d) must be equal to numAzi(%d)." % (
                arrData.shape[1], arrAngAzi.shape[0]
            ))
            return
        if (arrData.shape[0] != (2 * arrAngEle.shape[0])):
            print("EADF")
            print("arrData.shape[0](%d) must be equal to 2 x numEle(%d)." % (
                arrData.shape[0], 2 * arrAngEle.shape[0]
            ))
            return
        if arrFreq.shape[0] != arrData.shape[3]:
            print(
                "EADF: arrData dim 3(%d) must be equal to arrFreq dim 0(%d)." %
                (arrData.shape[3], arrFreq.shape[0])
            )
            return
        if arrPos.shape[0] != 3:
            print("EADF: arrPos must have exactly 3 rows")
            return
        if arrPos.shape[1] != arrData.shape[4]:
            print("EADF: num of positions %d doesnt match elem number %d" % (
                arrPos.shape[1], arrData.shape[4]
            ))
            return
        if np.any((arrFreq[:-1] - arrFreq[1:]) >= 0):
            print("EADF: frequencies must be sorted")
            return

        # make a local copy of the raw input data
        self._arrRawData = np.copy(arrData)
        self._arrPos = np.copy(arrPos)
        self._numElements = self._arrPos.shape[1]
        self._numAziInit = arrAngAzi.shape[0]
        self._numEleInit = 2 * arrAngEle.shape[0]
        self._arrAngAzi = np.copy(arrAngAzi)
        self._arrAngEle = np.copy(arrAngEle)
        self._arrFreq = np.copy(arrFreq)

        # generate the Fourier representation and the according
        # frequency bins
        self._arrFourierData, self._muAzi, self._muEle = sampledToFourier(
            arrData
        )

        # initially we don't do any compression
        self._compressionFactor = 1.0
        self._arrIndEleCompress = (np.ones(self._numEleInit) > 0)
        self._arrIndAziCompress = (np.ones(self._numAziInit) > 0)
