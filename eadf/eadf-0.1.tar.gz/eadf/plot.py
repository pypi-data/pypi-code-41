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
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import mpl_toolkits.mplot3d.axes3d as axes3d


def plotBeamPattern(
    arrData: np.ndarray
):
    """Short summary.

    Parameters
    ----------
    arrData : np.array
        Description of parameter `arrData`.

    Returns
    -------
    type
        Description of returned object.

    """

    # sample in the angular domains
    arrTheta = np.linspace(0, 2 * np.pi, 40)
    arrPhi = np.linspace(0, np.pi, 20)

    # create a grid
    grdTheta, grdPhi = np.meshgrid(arrTheta, arrPhi)

    # we just take the squared absolute values
    arrR = np.abs(arrData) ** 2

    # transform everything into cartesian coordinates
    arrX = arrR * np.sin(grdPhi) * np.cos(grdTheta)
    arrY = arrR * np.sin(grdPhi) * np.sin(grdTheta)
    arrZ = arrR * np.cos(grdPhi)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection='3d')
    plot = ax.plot_surface(
        arrX,
        arrY,
        arrZ,
        rstride=1,
        cstride=1,
        facecolors=cmap(
            mcolors.Normalize(
                vmin=arrZ.min(), vmax=arrZ.max()
            )
        ),
        linewidth=0,
        antialiased=False,
        alpha=0.5
    )
    plt.show()
