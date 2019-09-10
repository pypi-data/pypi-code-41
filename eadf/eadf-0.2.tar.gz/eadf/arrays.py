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
Routines to Create Synthetic Arrays
-----------------------------------

Here we provide a convenient way to generate EADF objects from
synthetic arrays. We assume the arrays elements to be uniformly sensitive
in all directions.
"""

import numpy as np
from scipy.spatial.distance import cdist
from .eadf import EADF
from .core import *


def generateURA(
    numElementsX: int,
    numElementsY: int,
    numSpacingX: float,
    numSpacingY: float
) -> EADF:
    """Uniform Rectangular Array

    Parameters
    ----------
    numElementsX : int
        number of array elements in x-direction
    numElementsY : int
        number of array elements in y-direction
    numSpacingX : float
        spacing between the first and last element in electrical size
    numSpacingY : float
        spacing between the first and last element in electrical size

    Returns
    -------
    EADF
        URA
    """

    if numElementsX <= 0:
        print("generateULA: numElementsX <= 0 is not allowed.")
        return
    if numSpacingX <= 0:
        print("generateULA: numSpacingX <= 0 is not allowed.")
        return
    if numElementsY <= 0:
        print("generateULA: numElementsY <= 0 is not allowed.")
        return
    if numSpacingY <= 0:
        print("generateULA: numSpacingY <= 0 is not allowed.")
        return

    arrX = np.linspace(-numSpacingX / 2, +numSpacingX / 2, numElementsX)
    arrY = np.linspace(-numSpacingY / 2, +numSpacingY / 2, numElementsY)

    grdX, grdY = anglesToGrid(arrX, arrY)

    # we align the elements along the x-coordinate
    arrPos = np.block([
        [grdX],
        [grdY],
        [np.zeros(numElementsX * numElementsY)]
    ])

    return(generateUniformArbitrary(arrPos))


def generateULA(
    numElements: int,
    numSpacing: float
) -> EADF:
    """Uniform Linear Array

    Parameters
    ----------
    numElements : int
        number of array elements
    numSpacing : float
        spacing between the first and last element in electrical size

    Returns
    -------
    EADF
        ULA
    """

    if numElements <= 0:
        print("generateULA: numElements <= 0 is not allowed.")
        return
    if numSpacing <= 0:
        print("generateULA: numSpacing <= 0 is not allowed.")
        return

    # we align the elements along the x-coordinate
    arrPos = np.block([
        [np.linspace(-numSpacing / 2, +numSpacing / 2, numElements)],
        [np.zeros(numElements)],
        [np.zeros(numElements)]
    ])

    return(generateUniformArbitrary(arrPos))


def generateUCA(
    numElements: int,
    numRadius: float
) -> EADF:
    """Non-Polarized Narrowband Uniform Circular Array

    Example
    -------

    >>> import eadf
    >>> A = eadf.arrays.generateUCA(11, 1.5)
    >>> A.visualize3D(60, 30, 0, 0, list(range(11)))

    Parameters
    ----------
    numElements : int
        Number of Elements
    numRadius : float
        Electrical size > 0

    Returns
    -------
    EADF
        EADF object

    """
    if numElements <= 0:
        print("generateUCA: numElements <= 0 is not allowed.")
        return
    if numRadius <= 0:
        print("generateUCA: numRadius <= 0 is not allowed.")
        return

    # create regular grid of angle positions for the elements
    arrElemAngle = np.linspace(
        0,
        2 * np.pi,
        numElements,
        endpoint=False
    )

    # calculate the positions of the elements in 2D cartesian coordinates
    arrPos = np.block([
        [numRadius * np.cos(arrElemAngle)],
        [numRadius * np.sin(arrElemAngle)],
        [np.zeros(numElements)]
    ])

    # call the routine for the arbitrary arrays
    return(generateUniformArbitrary(arrPos))


def generateStackedUCA(
    numElements: int,
    numStacks: int,
    numRadius: float,
    numHeight: float
) -> EADF:
    """Non-Polarized Narrowband Stacked Uniform Circular Array

    Example
    -------

    >>> import eadf
    >>> A = eadf.arrays.generateStackedUCA(11, 3, 1.5, 0.5)
    >>> A.visualize3D(60, 30, 0, 0, list(range(33)))

    Parameters
    ----------
    numElements : int
        Number of Elements per Stack > 0
    numStacks : int
        Number of Stacks > 0
    numRadius : float
        Electrical Size > 0
    numHeight : float
        Displacement height between two adjacent stacks

    Returns
    -------
    EADF
        EADF object representing this very array

    """
    if numElements <= 0:
        print("generateStackedUCA: numElements <= 0 is not allowed.")
        return
    if numStacks <= 0:
        print("generateStackedUCA: numStacks <= 0 is not allowed.")
        return
    if numRadius <= 0:
        print("generateStackedUCA: numRadius <= 0 is not allowed.")
        return
    if numHeight <= 0:
        print("generateStackedUCA: numHeight <= 0 is not allowed.")
        return

    # regular grid of angles
    arrElemAngle = np.linspace(
        0,
        2 * np.pi,
        numElements,
        endpoint=False
    )

    # regular grid of heights
    arrHeights = np.linspace(
        0,
        numStacks * numHeight,
        numStacks,
        endpoint=False
    )

    # array of position of elements in 3D cartesian coordinates
    arrPos = np.empty((3, numElements * numStacks))

    arrPos[:2, :] = np.tile(
        np.block([
            [numRadius * np.cos(arrElemAngle)],
            [numRadius * np.sin(arrElemAngle)]
        ]),
        (1, numStacks)
    )

    # the heights repeat according to the number of elements and the
    # number of stacks
    arrPos[2, :] = np.repeat(arrHeights, numElements)

    return generateUniformArbitrary(arrPos)


def generateUniformArbitrary(
    arrPos: np.ndarray
) -> EADF:
    """Array with Uniform Elements at Arbitrary Positions

    One simply specifies a (3 x N) np.ndarray to specify the elements
    positions in 3D cartesian space. The elements themselves are assumed
    to be uniform emitters. This allows to create a vast amount of
    different antenna geometries for qucik testing.

    Example
    -------

    >>> import eadf
    >>> import numpy as np
    >>> arrPos = np.random.uniform(-1, 1, (3, 10))
    >>> A = eadf.arrays.generateUniformArbitrary(arrPos)
    >>> A.visualize3D(60, 30, 0, 0, list(range(10)))

    Parameters
    ----------
    arrPos : np.ndarray
        (3 x numElements) array of positions

    Returns
    -------
    EADF
        EADF object representing this very array

    """
    if arrPos.shape[0] != 3:
        print("generateUniformArbitrary: arrPos must have exactly 3 rows")
        return

    # upper bound for the radius enclosing sphere
    numMaxDist = 0.5 * np.max(cdist(arrPos, arrPos))
    numElements = arrPos.shape[1]

    # Now we sample in Azimuth an Elevation according to (C.2.1.1.)
    # in the dissertation of del galdo
    numL = int(np.ceil(2 * np.pi * numMaxDist) + 10)
    numAzi = 4 * numL
    numEle = 2 * numL + 1

    # now calc the anuglar grids
    arrAngAzi, arrAngEle = sampleAngles(numAzi, numEle)
    grdAngAzi, grdAngEle = anglesToGrid(arrAngAzi, arrAngEle)

    # projections of the angles on the sphere
    arrProj = np.block([
        [np.cos(grdAngAzi) * np.sin(grdAngEle)],
        [np.sin(grdAngAzi) * np.sin(grdAngEle)],
        [np.cos(grdAngEle)]
    ])

    # generate the raw data
    arrRawData = np.exp(
        1j * arrProj.T.dot(arrPos)
    ) / np.sqrt(numElements)

    # create an internal EADF data structure
    arrEADFData = np.zeros(
        (numEle, numAzi, 1, 1, numElements), dtype='complex'
    )
    arrEADFData[:, :, 0, 0, :] = arrRawData.reshape(
        (numEle, numAzi, numElements)
    )

    arrEADFData = symmetrizePattern(arrEADFData)

    return EADF(
        arrEADFData, arrAngAzi, arrAngEle, np.ones(1), arrPos
    )
