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
Routines to import arrays
-------------------------

Basic Concepts
^^^^^^^^^^^^^^

Here we provide a collection of several importers to conveniently
create EADF objects from various data formats. For this purpose we
provide a set of so called *handshake formats*, which can be seen as
intermediate formats, which facilitate the construction of importers,
since for these hanshake formats we already provide tested conversion
routines to the internat data format.

Handshake Formats
^^^^^^^^^^^^^^^^^

For these formats there are readily available and tested importers. See
the respective importer methods for further details.

 - Regular (in space) Angular Data: 2*co-ele x azi x pol x freq x elem.
   This format is simply handled by the EADF class initialization. So, if your
   data is already in that format, just call EADF() with it.
 - Regular (in space) Spatial Fourier Data:
   2*co-ele-sptfreq x azi-sptfreq x pol x freq x elem
 - Angle List Data: Ang x Pol x Freq x Elem
"""

import numpy as np
from .eadf import EADF
from .core import *


def fromAngleListData(
    arrAngAziData: np.ndarray,
    arrAngEleData: np.ndarray,
    arrAngleListData: np.ndarray,
    arrFreqData: np.ndarray,
    arrPos: np.ndarray,
    numAzi: int,
    numEle: int,
    numErrorTol=1e-4,
    method='SH'
) -> EADF:
    """Importer from the Angle List Data Handshake format

    This format allows to specify a list of angles (azi, ele)_i and
    beam pattern values v_i = (pol, freq, elem)_i which are then
    interpolated along the two angular domains to get a regular grid in
    azimuth and co-elevation. By default this is done using vector spherical
    harmonics, since they can deal with irregular sampling patterns
    quite nicely. In this format for each angular sampling point, we
    need to have excited the array elements with the same frequencies.

    Parameters
    ----------
    arrAngAziData : np.ndarray
        Sampled Azimuth Angles
    arrAngEleData : np.ndarray
        Sampled Co-elevation Angles
    arrAngleListData : np.ndarray
        List in angle x pol x freq x element format
    arrFreqData : np.ndarray
        Frequencies the array was excited with in ascending order
    arrPos : np.ndarray
        Positions of the array elements
    numAzi : int
        number of regular azimuth samples used during interpolation > 0
    numEle : int
        number of regular elevation samples used during interpolation > 0
    numErrorTol : float
        error tolerance for coefficients fitting > 0
    method : string
        Interpolation Method, default='SH'

    Returns
    -------
    EADF
        Created Array

    """
    if (
        (arrAngAziData.shape[0] != arrAngEleData.shape[0])
        or (arrAngleListData.shape[0] != arrAngAziData.shape[0])
        or (arrAngleListData.shape[0] != arrAngEleData.shape[0])
    ):
        print("fromAngleListData:")
        print(
            "Input arrays of sizes %d azi, %d ele, %d values dont match" % (
                arrAngAziData.shape[0],
                arrAngEleData.shape[0],
                arrAngleListData.shape[0]
            )
        )
        return
    if arrPos.shape[1] != arrAngleListData.shape[3]:
        print("fromAngleListData:")
        print("Number of positions %d does not match provided data %d", (
            arrPos.shape[1], arrAngleListData.shape[3]
        ))
        return
    if arrFreqData.shape[0] != arrAngleListData.shape[2]:
        print("fromAngleListData:")
        print("Number of freqs %d does not match provided data %d", (
            arrFreqData.shape[0], arrAngleListData.shape[2]
        ))
        return
    if numAzi < 0:
        print("fromAngleListData:")
        print("numAzi must be larger than 0.")
        return
    if numEle < 0:
        print("fromAngleListData:")
        print("numEle must be larger than 0.")
        return

    # we start with SH order of 5, see below
    # as soon as we offer more interpolation methods, we should handle
    # this differently
    numInterError = np.inf
    numN = 4

    # we steadily increase the approximation base size
    while (numInterError > numErrorTol):
        numN += 1
        arrInter = interpolateDataSphere(
            arrAngAziData,
            arrAngEleData,
            arrAngleListData,
            arrAngAziData,
            arrAngEleData,
            numN=numN,
            method=method
        )

        # calculate the current interpolation error
        numInterError = np.linalg.norm(arrInter - arrAngleListData)

    # generate the regular grid, where we want to sample the array
    arrAzi, arrEle = sampleAngles(numAzi, numEle)
    grdAng, grdEle = anglesToGrid(arrAzi, arrEle)

    # now run the interpolation for the regular grid, flip the pattern
    arrInter = symmetrizePattern(interpolateDataSphere(
        arrAngAziData,
        arrAngEleData,
        arrAngleListData,
        grdAng,
        grdEle,
        numN=numN,
        method=method
    ).reshape(
        numEle,
        numAzi,
        arrAngleListData.shape[1],
        arrFreqData.shape[0],
        arrPos.shape[1]
    ))

    return EADF(
        arrInter,
        arrAzi,
        arrEle,
        arrFreqData,
        arrPos
    )


def fromFourierData(
    arrFourierData: np.ndarray,
    arrFreq: np.ndarray,
    arrPos: np.ndarray
) -> EADF:
    """Regular (in space) Spatial Fourier Data

    This format is basically the internal data format only that it is already
    Fourier transformed along azimuth and co-elevation. In some situations
    this might come in handy, the import is easy, so we provide it.

    Parameters
    ----------
    arrFourierData : np.ndarray
        2*co-ele x azi x pol x freq x elem
    arrFreq : np.ndarray
        Frequencies the array was excited with in ascending order
    arrPos : np.ndarray
        Position in 3D cartesian space of the individual elements

    Returns
    -------
    EADF
        EADF object from the respective data

    """
    if (arrFourierData.shape[0] % 2) != 0:
        print("fromFourierData:")
        print("Co-Elevation dimension must be even.")
        return
    if arrFreq.shape[0] != arrFourierData.shape[3]:
        print("fromFourierData:")
        print("freqency samples %d must equal data dimension 4 %d" % (
            arrFreq.shape[0], arrFourierData.shape[3]
        ))
        return
    if arrPos.shape[1] != arrFourierData.shape[4]:
        print("fromFourierData:")
        print("num of positions %d doesnt match elem number %d" % (
            arrPos.shape[1], arrFourierData.shape[4]
        ))
        return

    # take half of the elevation, since 2*co-ele x azi
    numEle = int(arrFourierData.shape[0] / 2)
    numAzi = arrFourierData.shape[1]

    # this does the inverse FFT on 2*co-ele x azi
    arrDataRaw, _, _ = fourierToSampled(arrFourierData)

    return EADF(
        arrDataRaw,
        *sampleAngles(numAzi, numEle),
        arrFreq,
        arrPos
    )
