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
Mathematical Core Routines
--------------------------

In this submodule we place all the mathematical and general core routines
which are used throughout the package. These are not intended for
direct use, but are still documented in order to allow new developers who
are unfamiliar with the code base to get used to the internal structure.
"""

import numpy as np
from scipy.special import sph_harm


def fourierToSampled(
    arrData: np.ndarray
) -> tuple:
    """Transform the Regularly Sampled Fourier Data in Spatial Domain

    We assume that the provided data was discretely Fourier transformed in both
    angular directions, so we have Fourier samples on a regular 2D grid.
    Moreover in this format all spatial freqencies are obtained for all
    the same wave-freqency samples. This routines then gives back the
    beampattern on a regular angular grid together with the right
    angular frequency bins.

    Parameters
    ----------
    arrData : np.ndarray
        Fourier data in the form
        2 * co-ele x azi x pol x freq x elem

    Returns
    -------
    tuple
        Inverse Fourier Transform and the respective sample frequencies

    """
    if (arrData.shape[0] % 2) != 0:
        print("fourierToSampled: 1st dim of arrData must have even size.")
        return
    if len(arrData.shape) != 5:
        print("fourierToSampled: arrData has wrong number of dimensions")
        return
    if arrData.shape[2] > 2:
        print("There must be at most 2 polarisations")
        return

    # the sample frequencies are generated according to (5) in the EADF paper
    return (
        np.fft.ifft2(
            arrData, axes=(0, 1)
        ) * (arrData.shape[0] * arrData.shape[1]),
        arrData.shape[1] * np.fft.fftfreq(arrData.shape[1]),  # azimuth
        arrData.shape[0] * np.fft.fftfreq(arrData.shape[0])   # elevation
    )


def sampledToFourier(
    arrData: np.ndarray
) -> tuple:
    """Transform the regularly sampled data in frequency domain

    Here we assume that the data is already flipped along co-elevation and
    rotated along azimuth as described in such that we can just calculate the
    respective 2D FFT from this along the first two axes.

    Parameters
    ----------
    data : np.ndarray
        Raw sampled and preprocessed data in the form
        2 * co-ele x azi x pol x freq x elem

    Returns
    -------
    (np.ndarray, np.ndarray, np.ndarray)
        Fourier Transform and the respective sample frequencies

    """
    if (arrData.shape[0] % 2) != 0:
        print("sampledToFourier: 1st dim of arrData must have even size.")
        return
    if len(arrData.shape) != 5:
        print("sampledToFourier: arrData has wrong number of dimensions")
        return
    if arrData.shape[2] > 2:
        print("sampledToFourier: There must be at most 2 polarisations")
        return

    # the sample frequencies are generated according to (5) in the EADF paper
    return (
        np.fft.fft2(
            arrData, axes=(0, 1)
        ) / (arrData.shape[0] * arrData.shape[1]),
        arrData.shape[1] * np.fft.fftfreq(arrData.shape[1]),  # azimuth
        arrData.shape[0] * np.fft.fftfreq(arrData.shape[0])   # elevation
    )


def _inversePatternTransform(
    arrAzi: np.ndarray,
    arrEle: np.ndarray,
    indFreq: np.ndarray,
    arrData: np.ndarray
) -> np.ndarray:
    """Samples the Pattern by using the Fourier Coefficients

    This function does the heavy lifting in the EADF evaluation process.
    It is used to sample the beampattern and the derivative itself, by
    evaluating d_phi * Gamma * d_theta^t as stated in (6) in the EADF
    paper by Landmann and delGaldo. It broadcasts this product over
    the last three coordinates of the fourier data, so across all
    polarisations, wave frequency bins and array elements.

    By changing d_phi (arrAzi) and d_theta(arRele) acordingly in the arguments
    one can calculate either the derivative or the pattern itself.

    Parameters
    ----------
    arrAzi : np.ndarray
        array of azimuth angles
    arrEle : np.ndarray
        array of co-elevation angles
    indFreq : np.ndarray
        wave frequency bin to sample at
    arrData : np.ndarray
        the Fourier coefficients to use

    Returns
    -------
    np.ndarray
        beam pattern values at arrAzi, arrEle
    """
    # allocate memory for the sampled data in form of
    # angle x pol x freq x element
    arrRes = np.empty(
        (
            arrAzi.shape[1],
            arrData.shape[2],
            indFreq.shape[0],
            arrData.shape[4]
        ),
        dtype='complex64'
    )

    # iterate over both polarisations, all desired frequencies
    # and all array elements
    for ii in range(arrData.shape[2]):
        for jj in indFreq:
            for kk in range(arrData.shape[4]):
                # equation (6) in the EADF paper
                arrRes[:, ii, jj, kk] = np.sum(
                    arrEle
                    * arrData[:, :, ii, jj, kk].dot(
                        arrAzi
                    ),
                    axis=0
                )

    return(arrRes)


def evaluatePattern(
    arrAngAzi: np.ndarray,
    arrAngEle: np.ndarray,
    muAzi: np.ndarray,
    muEle: np.ndarray,
    indFreq: np.ndarray,
    arrData: np.ndarray
) -> np.ndarray:
    """Sample the Beampattern at Dedicated Angles

    Parameters
    ----------
    arrAngAzi : np.ndarray
        azimuth angles to sample at
    arrAngEle : np.ndarray
        co-elevation angles to sample at
    muAzi : np.ndarray
        spatial frequency bins in azimuth direction
    muEle : np.ndarray
        spatial frequency bins in co-elevation direction
    indFreq : np.ndarray
        subset of wave frequencies
    arrData : np.ndarray
        fourier coefficients

    Returns
    -------
    np.ndarray
        sampled values
    """
    # equation (7) in the EADF Paper
    arrMultAzi = np.exp(
        1j * np.outer(muAzi, arrAngAzi)
    )
    arrMultEle = np.exp(
        1j * np.outer(muEle, arrAngEle)
    )

    return(
        _inversePatternTransform(
            arrMultAzi, arrMultEle, indFreq, arrData
        )
    )


def evaluatePatternDerivative(
    arrAngAzi: np.ndarray,
    arrAngEle: np.ndarray,
    muAzi: np.ndarray,
    muEle: np.ndarray,
    indFreq: np.ndarray,
    arrData: np.ndarray
) -> tuple:
    """Sample the Beampattern Derivatives at Dedicated Angles

    Parameters
    ----------
    arrAngAzi : np.ndarray
        azimuth angles to sample at
    arrAngEle : np.ndarray
        co-elevation angles to sample at
    muAzi : np.ndarray
        spatial frequency bins in azimuth direction
    muEle : np.ndarray
        spatial frequency bins in co-elevation direction
    indFreq : np.ndarray
        subset of wave frequencies
    arrData : np.ndarray
        fourier coefficients

    Returns
    -------
    (np.ndarray, np.ndarray)
        (derivAzi, derivCoEle)
    """
    # equation (7) in the EADF Paper
    arrMultAzi = np.exp(
        1j * np.outer(muAzi, arrAngAzi)
    )
    arrMultEle = np.exp(
        1j * np.outer(muEle, arrAngEle)
    )

    # equation (8) in the EADF Paper
    arrMultAziDeriv = np.multiply(1j * muAzi, arrMultAzi.T).T
    arrMultEleDeriv = np.multiply(1j * muEle, arrMultEle.T).T

    return((
        _inversePatternTransform(
            arrMultAziDeriv, arrMultEle, indFreq, arrData
        ),
        _inversePatternTransform(
            arrMultAzi, arrMultEleDeriv, indFreq, arrData
        )
    ))


def interpolateDataSphere(
    arrAngAziSample: np.ndarray,
    arrAngEleSample: np.ndarray,
    arrValues: np.ndarray,
    arrAngAziInter: np.ndarray,
    arrAngEleInter: np.ndarray,
    method='SH',
    **kwargs
) -> np.ndarray:
    """Interpolate Data located on a Sphere

    This method can be used for interpolating a function of the form
    f : S^2 -> C which is sampled on N arbitrary positions on the sphere.
    The input data is assumed to be in the format N x M1 x ... and the
    interpolation is broadcasted along M1 x ...
    The interpolation is always done using least squares, so for noisy data
    or overdetermined data with respect to the basis you should not encounter
    any problems.

    *Methods*
     - *SH* (Spherical Harmonics), see dissertation delGaldo,
       For these you have to supply *numN*
       as a kwarg, which determines the order of the SH basis. The number
       of total basis functions is then calculated via
       *numN x (numN + 1) + 1*. default=6


    Examples
    --------

    >>> # Interpolating a Stacked UCA using SH
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> import eadf
    >>> A = eadf.arrays.generateStackedUCA(11, 3, 1.5, 0.5)
    >>> numSamples = 100
    >>> arrEleSm = np.random.uniform(0, np.pi, numSamples)
    >>> arrAziSm = np.random.uniform(0, 2 * np.pi, numSamples)
    >>> arrY = A.sample(arrAziSm, arrEleSm)
    >>> intEle = 40
    >>> intAzi = 80
    >>> arrAzi, arrEle = eadf.core.sampleAngles(intEle, intAzi)
    >>> grdAzi, grdEle = eadf.core.anglesToGrid(arrAzi, arrEle)
    >>> arrZ = eadf.core.interpolateDataSphere(
    >>>     arrAziSm,
    >>>     arrEleSm,
    >>>     arrY,
    >>>     grdAzi,
    >>>     grdEle,
    >>>     method='SH',
    >>>     numN=6
    >>> )
    >>> plt.subplot(211)
    >>> plt.imshow(np.real(arrZ[:, 0].reshape(intEle, intAzi)))
    >>> plt.subplot(212)
    >>> plt.imshow(np.real(
    >>>     A.sample(grdAzi, grdEle)[:, 0, 0, 0].reshape((intEle, intAzi))
    >>> ))
    >>> plt.show()

    Parameters
    ----------
    arrAngAziSample : np.ndarray
        Sampled Azimuth positions
    arrAngEleSample : np.ndarray
        Sampled Co-Elevation positions
    arrValues : np.ndarray
        Sampled values
    arrAngAziInter : np.ndarray
        Azimuth Positions we want the function to be evaluated
    arrAngEleInter : np.ndarray
        Elevation positions we want the function to be evaluated
    method : type
        'SH' for spherical harmonics
    **kwargs : type
        Depends on method, see above

    Returns
    -------
    np.ndarray
        Description of returned object.

    """
    if (
        (arrAngAziSample.shape[0] != arrAngEleSample.shape[0])
        or (arrValues.shape[0] != arrAngAziSample.shape[0])
        or (arrValues.shape[0] != arrAngEleSample.shape[0])
    ):
        print("interpolateDataSphere:")
        print(
            "Input arrays of sizes %d azi, %d ele, %d values dont match" % (
                arrAngAziSample.shape[0],
                arrAngEleSample.shape[0],
                arrValues.shape[0]
            )
        )
        return
    if (arrAngAziInter.shape[0] != arrAngEleInter.shape[0]):
        print("interpolateDataSphere:")
        print(
            "Output arrays of sizes %d azi, %d ele dont match" % (
                arrAngAziInter.shape[0],
                arrAngEleInter.shape[0]
            )
        )
        return

    if method == 'SH':
        #
        kwargs.get('numN', 6)
        if kwargs['numN'] <= 0:
            print("interpolateDataSphere:")
            print("_genSHMatrix: numN must be greater than 0.")
            return
        else:
            return(
                _interpolateSH(
                    arrAngAziSample,
                    arrAngEleSample,
                    arrValues,
                    arrAngAziInter,
                    arrAngEleInter,
                    kwargs['numN']
                )
            )
    else:
        print('interpolateDataSphere: Method not implemented.')


def _interpolateSH(
    arrAngAziSample: np.ndarray,
    arrAngEleSample: np.ndarray,
    arrValues: np.ndarray,
    arrAngAziInter: np.ndarray,
    arrAngEleInter: np.ndarray,
    numN: int
) -> np.ndarray:
    """Interpolate function on Sphere using Spherical Harmonics

    See Dissertation of delGaldo for details.

    Parameters
    ----------
    arrAngAziSample : np.ndarray
        Sampled Azimuth positions
    arrAngEleSample : np.ndarray
        Sampled Co-Elevation positions
    arrValues : np.ndarray
        Sampled values
    arrAngAziInter : np.ndarray
        Azimuth Positions we want the function to be evaluated
    arrAngEleInter : np.ndarray
        Elevation positions we want the function to be evaluated
    numN : int
        Order of the SH

    Returns
    -------
    np.ndarray
        Description of returned object.

    """

    # number of sampling points of the function
    numSamples = arrAngAziSample.shape[0]

    # matrix containing the basis functions evaluated at the
    # sampling positions. this one is used during the fitting of
    # the interpolation coefficients:
    # min || matSample * X - arrValues||_2^2
    matSample = _genSHMatrix(arrAngAziSample, arrAngEleSample, numN)

    # this matrix is used to generate the interpolated values, so it
    # contains the basis functions evaluated at the interpolation
    # points and we use the least squares fit to get the right linear
    # combinations
    matInter = _genSHMatrix(arrAngAziInter, arrAngEleInter, numN)

    # import matplotlib.pyplot as plt
    # plt.subplot(211)
    # plt.imshow(np.real(matSample))
    # plt.colorbar()
    # plt.subplot(212)
    # plt.imshow(np.real(matInter))
    # plt.colorbar()
    # plt.show()

    tplOrigShape = arrValues.shape
    # print("inshape", tplOrigShape)

    # do the least squares fit
    arrLstSq = np.linalg.lstsq(
        matSample,
        arrValues.reshape((numSamples, -1)),
        rcond=-1
    )

    # extract the coefficients from the least squares fit
    arrCoeffs = arrLstSq[0]

    # calculate the interpolated values and return the same shape as
    # the input, but with different size in the interpolated first coordinate
    arrRes = matInter.dot(arrCoeffs).reshape((-1, *tplOrigShape[1:]))
    # print("outshape", arrRes.shape)
    return(arrRes)


def _genSHMatrix(
    arrAngAzi: np.ndarray,
    arrAngEle: np.ndarray,
    numN: int
) -> np.ndarray:
    """Create a Matrix containing sampled Spherical harmonics

    Parameters
    ----------
    arrAngAzi : np.ndarray
        Azimuth angles to evaluate at
    arrAngEle : np.ndarray
        Elevation angles to evaluate at
    numN : int
        Order of the SH basis > 0

    Returns
    -------
    np.ndarray
        Matrix containing sampled SH as its columns
    """

    # the spherical harmonics are always complex except in trivial
    # cases
    matR = np.zeros(
        (arrAngEle.shape[0], numN * (numN + 1) + 1), dtype='complex128'
    )

    # count the current basis element we are in
    numInd = 0

    # SH have two indices Y_LM with |L| <= M, see the scipy docu
    # on them
    for ii1 in range(numN + 1):
        for ii2 in range(ii1 + 1):
            # except for ii1 == 0, we always can generate two basis elements
            matR[:, numInd] = sph_harm(ii2, ii1, arrAngAzi, arrAngEle)
            if ii1 > 0:
                # note that matR[:, -numInd] = matR[:, numInd].conj()
                # would also work
                matR[:, -numInd] = sph_harm(-ii2, ii1, arrAngAzi, arrAngEle)
            numInd += 1
    return matR


def anglesToGrid(
    arrAngAzi: np.ndarray,
    arrAngEle: np.ndarray
) -> tuple:
    """Build up all pairwise combinations of angles

    For two given arrays of possibly unequal lengths N1 and N2 we generate
    two new arrays, that contain at the

    Parameters
    ----------
    arrAngAzi : np.ndarray
        Azimuth angles to be used `arrAngAzi`.
    arrAngEle : np.ndarray
        Co-Elevation angles to be used `arrAngEle`.

    Returns
    -------
    tuple
        (azimuth angles, co-elevation angles)

    """

    grdAngAzi, grdAngEle = np.meshgrid(arrAngAzi, arrAngEle)
    return (grdAngAzi.flatten(), grdAngEle.flatten())


def symmetrizePattern(
    arrA: np.ndarray
) -> np.ndarray:
    """Generate a symmetrized version of a regularly sampled array pattern

    This function assumes that we are given the beam pattern sampled in
    co-elevation and azimuth on a regular grid, as well as for at most 2
    polarizations and all the same wave-frequency bins. Then this function
    applies (2) in the original EADF paper. So the resulting array has
    the same dimensions but twice the size in co-elevation direction.

    Parameters
    ----------
    arrA : np.ndarray
        Input data (co-elevation x azimuth x pol x freq x elem).

    Returns
    -------
    np.ndarray
        Output data (2*co-elevation x azimuth x pol x freq x elem).

    """
    if len(arrA.shape) != 5:
        print(
            "symmetrizePattern: got %d dimensions instead of 5" % (
                len(arrA.shape)
            )
        )
        return

    arrRes = np.tile(arrA, (2, 1, 1, 1, 1))

    indBack = arrA.shape[2:]
    for bb in np.ndindex(indBack):
        # Equation (2) in EADF Paper by Landmann and DGO
        arrRes[arrA.shape[0]:, ..., bb] = np.roll(
            np.flip(
                arrRes[arrA.shape[0]:, ..., bb],
                axis=0
            ),
            shift=int(arrA.shape[1]/2),
            axis=1
        )

    return arrRes


def sampleAngles(
    numAzi: int,
    numEle: int,
    **kwargs
) -> tuple:
    """Generate regular samplings in azimuth and co-elevation

    By default we generate angles in azimuth and *co-elevation*. This is due
    to the fact that the EADF works best in this case. Both directions
    are sampled regularly.

    Parameters
    ----------
    numAzi : int
        Number of samples in azimuth direction. > 0
    numEle : int
        Number of samples in co-elevation direction. > 0
    lstEndpoints : [0, 0], optional
        If endpoints should be generated in the respective dimensions

    Returns
    -------
    tuple
        (anglesAzi, anglesEle)

    """
    if numAzi < 1:
        print("sampleAngles: numAzi is %d, must be > 0" % (numAzi))
        return
    if numEle < 1:
        print("sampleAngles: numEle is %d, must be > 0" % (numEle))
        return

    lstEndpoints = kwargs.get('lstEndpoints', [0, 0])

    if len(lstEndpoints) != 2:
        print("sampleAngles: lstEndpoints has length %d instead of 2." % (
            len(lstEndpoints)
        ))
        return

    arrAngAzi = np.linspace(0, 2 * np.pi, numAzi, endpoint=lstEndpoints[0])
    arrAngEle = np.linspace(0, +np.pi, numEle, endpoint=lstEndpoints[1])
    return (arrAngAzi, arrAngEle)


def regularSamplingToGrid(
    arrA: np.ndarray,
    numAzi: int,
    numEle: int
) -> np.ndarray:
    """Reshape an array sampled on a 2D grid to actual 2D data

    Parameters
    ----------
    arrA : np.ndarray
        Input data `arrA` (2D angle x pol x freq x elem).
    numAzi : int
        Number of samples in azimuth direction.
    numEle : int
        Number of samples in co-elevation direction.

    Returns
    -------
    np.ndarray
        Output data (co-elevation x azimuth x pol x freq x elem).

    """
    if arrA.shape[0] != (numAzi * numEle):
        print("regularSamplingToGrid:")
        print("numAzi %d, numEle %d and arrA.shape[0] %d dont match" % (
            numAzi, numEle, arrA.shape[0]
        ))
        return
    if len(arrA.shape) != 4:
        print("regularSamplingToGrid:")
        print("Input arrA has %d dimensions instead of 4" % (
            len(arrA.shape)
        ))
        return

    arrRes = np.empty((numEle, numAzi, *arrA.shape[1:]), dtype=arrA.dtype)

    # TODO: How can we speed this up?
    for ii in range(arrA.shape[1]):
        for jj in range(arrA.shape[2]):
            for kk in range(arrA.shape[3]):
                arrRes[:, :, ii, jj, kk] = arrA[:, ii, jj, kk].reshape(
                    (numEle, numAzi)
                )

    return arrRes


def columnwiseKron(
    arrA: np.ndarray,
    arrB: np.ndarray
) -> np.ndarray:
    """Calculate column-wise Kronecker-Product

    Parameters
    ----------
    arrA : np.ndarray
        First input `arrA`.
    arrB : np.ndarray
        Second input `arrB`.

    Returns
    -------
    np.ndarray
        kron(arrA, arrB)

    """

    if arrA.shape[1] != arrB.shape[1]:
        print('Matrices cannot be multiplied')
        return

    # the first matrix needs its rows repeated as many times as the
    # other one has rows. the second one needs to be placed repeated
    # as a whole so many times as the first one has rows.
    # the we just do an elementwise multiplication and are done.
    return(
        np.multiply(
            np.repeat(
                arrA, arrB.shape[0], axis=0
            ),
            np.tile(
                arrB, (arrA.shape[0], 1)
            )
        )
    )
