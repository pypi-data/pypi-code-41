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
Plotting Routines
-----------------

These routines are called from the EADF object to aid visualization.
They should not be used directly from outside the package,
but rather developers should implement new plotting functions here
and expose them via appropraite EADF methods.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d


def __defaultFun(
    x: np.ndarray
) -> np.ndarray:
    """Default Function to apply before plotting

    Parameters
    ----------
    x : np.ndarray
        Input

    Returns
    -------
    np.ndarray
        np.abs(Input)

    """
    return np.abs(x)


def plotBeamPattern2D(
    arrData: np.ndarray,
    arrAngAzi: np.ndarray,
    arrAngEle: np.ndarray,
    numAzi: int,
    numEle: int,
    fun=None
) -> None:
    """Plot several 2D beampatterns

    This routine plots the beam pattern of at most 9 Elements
    since we are using subplots.

    Parameters
    ----------
    arrData : np.ndarray
        Input Data in Angle x Pol x Freq x Elem
    arrAngAzi : np.ndarray
        Azimuth Angles we sampled at
    arrAngEle : np.ndarray
        Co-Elevation Angles we sampled at
    numAzi : int
        Number of Samples in Azimuth direction
    numEle : int
        Number of Samples in Elevation direction
    fun : method
        function to apply to the elements values
    """
    if (numEle * numAzi) != arrData.shape[0]:
        print("plotBeamPattern2D")
        print("Num of Elevation and Azimuth %d,%d do not fit data %d, %d" % (
            numEle, numAzi, arrData.shape[0], arrData.shape[1]
        ))
        return
    if fun is None:
        fun = __defaultFun

    numPlots = min(arrData.shape[-1], 9)

    for ii in range(numPlots):
        plt.subplot(str(100 * (numPlots) + 10 + (ii + 1)))
        # we just take the squared absolute values
        arrR = fun(arrData[..., ii])

        plt.imshow(
            arrR.reshape((numEle, numAzi))
        )
        plt.colorbar()
    plt.show()


def plotBeamPattern3D(
    arrData: np.ndarray,
    arrAngAzi: np.ndarray,
    arrAngEle: np.ndarray,
    arrPos: np.ndarray,
    numAzi: int,
    numEle: int,
    fun=None
) -> None:
    """Plot Beampatterns as spherical Gain Plots

    Each array element gets a ball around its position to display the
    respective gain.

    Parameters
    ----------
    arrData : np.ndarray
        Input Data in Angle x Pol x Freq x Elem
    arrAngAzi : np.ndarray
        Azimuth Angles we sampled at
    arrAngEle : np.ndarray
        Co-Elevation Angles we sampled at
    arrPos : np.ndarray,
        Positions of the array elements
    numAzi : int
        Number of Samples in Azimuth direction
    numEle : int
        Number of Samples in Elevation direction
    fun : method
        function to apply to the elements values
    """
    if (numEle * numAzi) != arrData.shape[0]:
        print("plotBeamPattern3D")
        print("Num of Elevation and Azimuth %d,%d do not fit data %d, %d" % (
            numEle, numAzi, arrData.shape[0], arrData.shape[1]
        ))
        return
    if arrData.shape[0] != arrAngAzi.shape[0]:
        print("plotBeamPattern3D")
        print("arrData.shape[0] %d does not fit arrAngAzi size %d" % (
            arrData.shape[0], arrAngAzi.shape[0]
        ))
        return
    if arrData.shape[0] != arrAngEle.shape[0]:
        print("plotBeamPattern3D")
        print("arrData.shape[0] %d does not fit arrAngEle size %d" % (
            arrData.shape[0], arrAngEle.shape[0]
        ))
        return
    if arrPos.shape[1] != arrData.shape[-1]:
        print("Number of pos %d does not match data dimension %d" % (
            arrPos.shape[1], arrData.shape[-1]
        ))
        return

    if fun is None:
        fun = __defaultFun

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection='3d')

    for ii in range(arrData.shape[-1]):
        # we just take the real part
        arrR = fun(arrData[..., ii])

        # transform everything into cartesian coordinates
        # obey the array element positions
        arrX = arrR * np.sin(arrAngEle) * np.sin(arrAngAzi) + arrPos[0, ii]
        arrY = arrR * np.sin(arrAngEle) * np.cos(arrAngAzi) + arrPos[1, ii]
        arrZ = arrR * np.cos(arrAngEle) + arrPos[2, ii]

        ax.plot_surface(
            (arrX).reshape((numEle, numAzi)),
            (arrY).reshape((numEle, numAzi)),
            (arrZ).reshape((numEle, numAzi)),
            rstride=2,
            cstride=2,
            linewidth=0,
            antialiased=True,
            alpha=1
        )
    plt.show()


def plotCut2D(
    arrData: np.ndarray,
    arrAngAzi: np.ndarray,
    arrPos: np.ndarray,
    fun=None
) -> None:
    """Plot the beam Pattern for a fixed Co-Elevation

    Parameters
    ----------
    arrData : np.ndarray
        Input Data in Angle x Pol x Freq x Elem
    arrAngAzi : np.ndarray
        Azimuth Angles we sampled at
    arrPos : np.ndarray
        Positions of the array elements
    fun : method
        function to apply to the elements values
    """
    if arrData.shape[0] != arrAngAzi.shape[0]:
        print("plotCut2D")
        print("arrData.shape[0] %d does not fit arrAngAzi size %d" % (
            arrData.shape[0], arrAngAzi.shape[0]
        ))
        return
    if arrPos.shape[1] != arrData.shape[-1]:
        print("plotCut2D")
        print("Number of pos %d does not match data dimension %d", (
            arrPos.shape[1], arrData.shape[-1]
        ))
        return

    if fun is None:
        fun = __defaultFun

    # iterate through the elements for one fixed polarization (the 0)
    for jj in range(arrData.shape[-1]):
        arrR = fun(arrData[:, 0, jj])
        arrXPos = arrPos[0, jj] + np.cos(arrAngAzi) * arrR
        arrYPos = arrPos[1, jj] + np.sin(arrAngAzi) * arrR
        plt.plot(arrXPos, arrYPos)
        plt.scatter(arrPos[0, jj], arrPos[1, jj])

    plt.show()
