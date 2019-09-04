# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------
# Authors:    Luis Miguel Sanchez Brea and Jesus del Hoyo
# Date:       2019/01/09 (version 1.0)
# License:    GPL
# -------------------------------------
"""
We present a number of functions for polarization using Jones framework:

**Generation**
    * **from_elements**: Creates a Jones matrix directly from the 4 elements (m00, m01, m10, m11).
    * **from_matrix**: Creates a Jones matrix directly from a 2x2 matrix.
    * **from_Mueller**: Takes a non-depolarizing Mueller Matrix and converts into Jones matrix.
    * **vacuum**:  Creates the matrix for vacuum.
    * **mirror**: Creates the matrix for a mirror. NOTE: Don't rotate this matrix.
    * **filter_amplifier**: Creates the matrix for a neutral filter or amplifier element
    * **diattenuator_perfect**: Creates a perfect linear diattenuator.
    * **diattenuator_linear**: Creates a real polarizer with perpendicular axes.
    * **quarter_waveplate**: Creates a quarter-waveplate.
    * **half_waveplate**: Creates a half-waveplate.
    * **retarder_linear**: Creates a retarder using delay.
    * **retarder_material**: Creates a retarder using physical properties of a anisotropic material.
    * **diattenuator_retarder_linear**: Creates a linear diattenuator retarder with the same axes for diattenuation and retardance.
    * **diattenuator_carac_angles**: Creates the most general diattenuator with orthogonal eigenstates from the caracteristic angles of the main eigenstate.
    * **diattenuator_azimuth_ellipticity**: Creates the general diattenuator with orthogonal eigenstates from the caracteristic angles of the main eigenstate.

**Manipulation**
    * **rotate**: Rotates the Jones vector.
    * **check**: Checks that the matrix stored in .M is a correct 2x2 matrix.
    * **clear**: Removes data and name from Jones matrix.
    * **remove_global_phase**: Removes the phase introduced by the optical element (respect to m00).
    * **reciprocal**: The optical element is fliped so the light transverses it in the opposite direction.


**Parameters**
    * **is_homogeneous**:   Determines if matrix is homogeneous or inhomogeneous.
    * **diattenuation**:   Calculates the diattenuation of the matrix.
    * **retardance**:     Calculates the retardance (or delay) introduced between the fast and slow axes.
"""
import copy as copy

import cmath
from cmath import exp as cexp
from functools import wraps

from numpy import arctan2, array, cos, exp, matrix, pi, sin, sqrt

from . import degrees, eps, np, num_decimals, um
from .jones_vector import Jones_vector
from .utils import (azimuth_elipt_2_carac_angles, put_in_limits, repair_name,
                    rotation_matrix_Jones)

X_jones = np.matrix(np.diag([1, -1]))


class Jones_matrix(object):
    """Class for Jones matrices

    Parameters:
        name (str): name of matrix for string representation

    Attributes:
        self.M (numpy.matrix): 4x1 array
        self.parameters (class): parameters of stokes
    """

    def _actualize_(f):
        @wraps(f)
        def wrapped(inst, *args, **kwargs):
            result = f(inst, *args, **kwargs)
            inst.update()
            return result

        return wrapped

    def __init__(self, name='M'):
        self.name = name
        self.type = 'Jones_matrix'

        self.M = np.matrix(np.zeros((2, 2), dtype=complex))
        self.parameters = Parameters_Jones_Matrix(self.M, self.name)

    def update(self):
        """Internal function. Updates self.parameters with values of self.
        """
        self.parameters.M = self.M
        self.parameters.name = self.name

    def __add__(self, other):
        """Adds two Jones matrices.

        Parameters:
            other (Jones): 2nd Jones matrix to add

        Returns:
            Jones Matrix: `s3 = s1 + s2`
        """

        j3 = Jones_matrix()
        j3.M = self.M + other.M
        j3.name = self.name + " + " + other.name
        j3.update()

        return j3

    def __sub__(self, other):
        """Substracts two Jones matrices.

        Parameters:
            other (Jones): 2nd Jones matrix to add

        Returns:
            Jones: `s3 = s1 - s2`
        """

        j3 = Jones_matrix()
        j3.M = self.M - other.M
        j3.name = self.name + " - " + other.name
        j3.update()

        return j3

    def __mul__(self, other):
        """
        TODO: check that other is a matrix (or a Jones_matrix) or a constant
        multiplies two Jones matrices.

        Parameters:
            other (Jones): 2nd Jones multiply

        Returns:
            Jones: `s3 = s1*s2`
        """

        if isinstance(other, (int, float, complex, np.matrix)):
            M3 = Jones_matrix()
            M3.M = self.M * other
        elif isinstance(other, (self.__class__)):
            M3 = Jones_matrix()
            M3.M = self.M * other.M
            M3.name = self.name + " * " + other.name
        elif isinstance(other, Jones_vector):
            M3 = Jones_vector()
            M3.M = self.M * other.M
            M3.name = self.name + " * " + other.name
            # M3.parameters.M = M3.M
            # M3.parameters.name=M3.name
        else:
            raise ValueError(
                'other is Not number, Jones_vector or Jones_matrix')
        M3.update()
        return M3

    def __rmul__(self, other):
        """Multiplies two Jones matrices.

        Parameters:
            other (Jones): 2nd Jones multiply

        Returns:
            Jones: `s3 = s2*s1`
        """

        M3 = Jones_matrix()

        if isinstance(other, (int, float, complex, np.matrix)):
            M3.M = self.M * other
        elif isinstance(other, self.__class__):
            M3.M = other.M * self.M
            M3.name = other.name + " * " + self.name
        else:
            raise ValueError('other is Not number or Jones_matrix')

        M3.update()
        return M3

    def __truediv__(self, other):
        """Divides a Jones matrix.

        Parameters:
            other (number): 2nd element to divide

        Returns:
            (Jones_matrix):
        """
        # Find the class of the other object
        if isinstance(other, (int, float, complex)):
            M3 = Jones_matrix()
            M3.from_matrix(self.M / other)
        else:
            raise ValueError('other is Not number')
        M3.update()
        return M3

    def __repr__(self):

        M = np.array(self.M).squeeze()
        M = np.round(M, num_decimals)

        l_name = "{} = \n".format(self.name)

        if abs(M.real - M).sum() < eps:
            M = M.real
            M.dtype = float

        difference = abs(M.round() - M).sum()
        if difference > eps:
            l0 = "      [{:+1.3f}, {:+1.3f}]\n".format(M[0, 0], M[0, 1])
            l1 = "      [{:+1.3f}, {:+1.3f}]".format(M[1, 0], M[1, 1])
        else:
            l0 = "      [{:+1.0f}, {:+1.0f}]\n".format(M[0, 0], M[0, 1])
            l1 = "      [{:+1.0f}, {:+1.0f}]".format(M[1, 0], M[1, 1])

        return l_name + l0 + l1

    def get(self):
        """Get the Jones Matrix

        Returns:
            (numpy.matrix): self.M, Jones matrixS
        """

        return self.M

    @_actualize_
    def check(self, verbose=False):
        """
        Verifies that is a Jones matrix is properly defined.

        References:
            R. Martinez-Herrero, P.M. Mejias, G.Piquero "Characterization of partially polarized light fields" Springer series in Optical sciences (2009) ISBN 978-3-642-01326-3, page 3, eqs. 1.4a and 1.4b.

        Parameters:
            verbose (Bool): Prints information.

        Returns:
            (bool): True if check is positive.
        """
        det1 = np.linalg.det(self.M)
        trace1 = np.trace(self.M * self.M.H)
        condition1 = np.abs(det1)**2 <= 1  # eq. 1.4a
        condition2 = trace1 >= 0 and trace1 <= 2

        if verbose is True:
            print("condition 1 = {0}".format(condition1))
            print("condition 2 = {0}".format(condition2))

        return condition1 * condition2

    @_actualize_
    def rotate(self,
               angle=0 * degrees,
               keep=False,
               returns_matrix=False,
               is_repair_name=True):
        """Rotates a jones_matrix a certain angle

        M_rotated = R(-angle) * self.M * R(angle)

        Parameters:
            angle (float): angle of rotation_matrix_Jones in radians.
            keep (bool): if True, the original element is not updated. Default: False.
            returns_matrix (bool): if True returns a matrix, else returns an instance to object.
            is_repair_name (bool): if True tries to repair name with @ rot @ rot -> @ 2*rot.

        Returns:
            (Jones_matrix): When returns_matrix == True.
            (numpy.matrix): 2x2 matrix when returns_matrix == False.
        """
        if angle != 0:
            name = repair_name(self.name +
                               " @{:1.2f} deg".format(angle / degrees))
            # Calculate the rotated matrix
            M_rotated = rotation_matrix_Jones(
                -angle) * self.M * rotation_matrix_Jones(angle)
            # Update original object if required
            if not keep:
                self.M = M_rotated
                self.name = name
        else:
            M_rotated = self.M
            name = self.name
        # Return
        if returns_matrix is True:
            return M_rotated
        else:
            j3 = Jones_matrix(name)
            j3.from_matrix(M_rotated)
            return j3

    @_actualize_
    def reciprocal(self, keep=True, returns_matrix=False):
        """Calculates the recirpocal of the optical element, so the light tranverses it in the opposite direction. In Mueller, the new matrix is the traspose of the old one.

        Parameters:
            keep (bool): if True self.M is updated. If False, it returns matrix and it is not updated in self.M.
            returns_matrix (bool): if True returns a matrix, else returns an instance to object.

        Returns:
            (Jones_matrix): When returns_matrix == True.
            (numpy.matrix): 2x2 matrix when returns_matrix == False.
        """
        M2 = Jones_matrix()
        M2.from_matrix(X_jones * self.M.T * X_jones)
        if not keep:
            self.M = M2.M
        if returns_matrix:
            return M2.M
        else:
            return M2

    @_actualize_
    def remove_global_phase(self, keep=True):
        """Function that transforms the Jones vector removing the global phase, so the first component of the elcric field is real and positive.

        Returns:
            J (2x2 numpy matrix): Jones matrix."""
        phase = self.parameters.global_phase()
        J = self.M * cexp(-1j * phase)
        if keep is True:
            self.M = E
        return J.M

    @_actualize_
    def clear(self):
        """Removes data and name from Jones matrix.
        """
        self.from_elements(0, 0, 0, 0)
        self.name = ''

    @_actualize_
    def from_elements(self, m00, m01, m10, m11):
        """2x2 Jones matrix [m00, m01, m10, m11]

        Parameters:
            m00 (float): first element m00
            m01 (float): first element m01
            m10 (float): first element m10
            m11 (float): first element m11

        Returns:
            (numpy.matrix): 2x2 matrix
        """

        self.M = matrix(array([[m00, m01], [m10, m11]]), dtype=complex)
        return self.M

    @_actualize_
    def from_matrix(self, M):
        """Create a Jones matrix from an external matrix.

        Parameters:
            M (2x2 numpy matrix): New matrix

        Returns:
            (numpy.matrix): 2x2 matrix
        """

        self.M = M
        return self.M

    @_actualize_
    def from_Mueller(self, Mueller, global_phase=0):
        """Takes a non-depolarizing Mueller Matrix and converts into Jones matrix

        .. math:: M = U^* (J \otimes J^*) * U^{-1}

        .. math:: T(M * M_t)=4*m_{00}

        References:
            Handbook of Optics vol 2. 22.36 (52-54)

        Parameters:
            Mueller (mumpy.matrix): Mueller matrix
            global_phase (float): Global phase introduced by the optical element. Default: 0.

        Returns:
            (numpy.matrix): 2x2 matrix
        """
        M = Mueller.M

        pxx = sqrt((M[0, 0] + M[0, 1] + M[1, 0] + M[1, 1]) / 2)
        pxy = sqrt((M[0, 0] - M[0, 1] + M[1, 0] - M[1, 1]) / 2)
        pyx = sqrt((M[0, 0] + M[0, 1] - M[1, 0] - M[1, 1]) / 2)
        pyy = sqrt((M[0, 0] - M[0, 1] - M[1, 0] + M[1, 1]) / 2)

        fxy = arctan2((-M[0, 3] - M[1, 3]), (M[0, 2] + M[1, 2]))
        fyx = arctan2((M[3, 0] + M[3, 1]), (M[2, 0] + M[2, 1]))
        fyy = arctan2((M[3, 2] - M[2, 3]), (M[2, 2] + M[3, 3]))

        self.M[0, 0] = pxx
        self.M[0, 1] = pxy * exp(1j * fxy)
        self.M[1, 0] = pyx * exp(1j * fyx)
        self.M[1, 1] = pyy * exp(1j * fyy)

        if global_phase % (2 * pi) != 0:
            C_phase = cexp(1j * global_phase)
            self.M = self.M * C_phase

        return self.M

    @_actualize_
    def vacuum(self, global_phase=0):
        """Creates the matrix for vacuum.

        Parameters:
            global_phase (float): Global phase introduced by the optical element. Default: 0.

        Returns:
            (numpy.matrix): 2x2 matrix
        """
        self.M = matrix(array([[1, 0], [0, 1]]), dtype=complex)

        if global_phase % (2 * pi) != 0:
            C_phase = cexp(1j * global_phase)
            self.M = self.M * C_phase

        return self.M

    @_actualize_
    def filter_amplifier(self, D=1, global_phase=0):
        """Creates the matrix for a neutral filter or amplifier element.

        Parameters:
            D (float): Attenuation (gain if > 1).
            global_phase (float): Global phase introduced by the optical element. Default: 0.

        Returns:
            (numpy.matrix): 2x2 matrix
        """
        self.M = matrix(array([[D, 0], [0, D]]), dtype=complex)

        if global_phase % (2 * pi) != 0:
            C_phase = cexp(1j * global_phase)
            self.M = self.M * C_phase

        return self.M

    @_actualize_
    def mirror(self, global_phase=0):
        """Jones matrix of a mirror.
        Warning: This matrix must not be rotated.

        Parameters:
            angle (float): angle of plate fast axis, in radians.
            global_phase (float): Global phase introduced by the optical element. Default: 0.

        Returns:
            (numpy.matrix): 2x2 matrix
        """
        self.M = matrix(array([[1, 0], [0, -1]]), dtype=complex)

        if global_phase % (2 * pi) != 0:
            C_phase = cexp(1j * global_phase)
            self.M = self.M * C_phase

        return self.M

    @_actualize_
    def diattenuator_perfect(self, angle=0, global_phase=0):
        """2x2 perfect linear diattenuator.

        Parameters:
            angle (float): angle of polarizer axis, in radians.
            global_phase (float): Global phase introduced by the optical element. Default: 0.

        Returns:
            (numpy.matrix): 2x2 matrix
        """

        # Metodo directo
        # return matrix(array([[cos(angle) ** 2, sin(angle) * cos(angle)],
        #         [sin(angle) * cos(angle), sin(angle) ** 2]]), dtype = float)
        self.M = matrix(array([[1, 0], [0, 0]]), dtype=float)
        self.rotate(angle)

        if global_phase % (2 * pi) != 0:
            C_phase = cexp(1j * global_phase)
            self.M = self.M * C_phase

        return self.M

    @_actualize_
    def diattenuator_linear(self, p1=1, p2=0, angle=0, global_phase=0):
        """Creates a real polarizer with perpendicular axes:

        .. math:: J = [p_1, 0; 0, p_2]'.


        Parameters:
            p1 (float): Field transmission of the fast axis (default 1).
            p2 (float): Field transmission of the slow angle (default 0).
            angle (float): rotation angle.
            global_phase (float): Global phase introduced by the optical element. Default: 0.

        Returns:
            (numpy.matrix): 2x2 matrix
        """
        self.M = matrix(array([[p1, 0], [0, p2]]), dtype=complex)
        self.rotate(angle)

        if global_phase % (2 * pi) != 0:
            C_phase = cexp(1j * global_phase)
            self.M = self.M * C_phase

        return self.M

    @_actualize_
    def diattenuator_retarder_linear(self,
                                     delay,
                                     p1=1,
                                     p2=1,
                                     angle=0,
                                     global_phase=0):
        """Creates a linear diattenuator retarder with the same
        axes for diattenuation and retardance. At 0 degrees, the matrix is of
        the form:

        .. math:: J = [p_1, 0; 0, p_2 e^{i \delta}]

        Parameters:
            delay (float): Retarding angle.
            p1 (float): Field transmission of the fast axis (default 1).
            p2 (float): Field transmission of the slow angle (default 1).
            angle (float): Element rotation angle (default 0).
            global_phase (float): Global phase introduced by the optical element. Default: 0.

        Returns:
            (numpy.matrix): 2x2 matrix
        """
        self.M = matrix(
            array([[p1, 0], [0, p2 * exp(1j * delay)]], dtype=complex))
        name = self.name
        self.rotate(angle)
        self.name = name

        if global_phase % (2 * pi) != 0:
            C_phase = cexp(1j * global_phase)
            self.M = self.M * C_phase

        return self.M

    @_actualize_
    def diattenuator_carac_angles(self, p1, p2, alpha, delta, global_phase=0):
        """Creates the most general diattenuator with orthogonal
        eigenstates from the caracteristic angles of the main eigenstate.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016) pp 137.

        Parameters:
            p1 (float): [0, 1] Square root of the higher transmission for one eigenstate.
            p2 (float): [0, 1] Square root of the lower transmission for the other eigenstate.
            alpha (float): [0, pi/2]: tan(alpha) is the ratio between field amplitudes of X and Y components.
            delta (float): [0, 2*pi]: phase difference between X and Y field components.
            carac (bool): [Default: True] If false, assumes alpha is azimuth and delta is elipticity.
            global_phase (float): Global phase introduced by the optical element. Default: 0.

        Returns:
            (numpy.matrix): 2x2 matrix
        """
        # Restrict measured values to the correct interval
        alpha = put_in_limits(alpha, "alpha")
        delta = put_in_limits(delta, "delta")
        # Compute the common operations
        sa, ca = (sin(alpha), cos(alpha))
        ed, edm = (cmath.exp(1j * delta), cmath.exp(-1j * delta))
        # Calculate the Jones matrix
        self.M = matrix(
            array([[p1 * ca**2 + p2 * sa**2, sa * ca * (p1 - p2) * edm],
                   [sa * ca * (p1 - p2) * ed, p2 * ca**2 + p1 * sa**2]]))

        if global_phase % (2 * pi) != 0:
            C_phase = cexp(1j * global_phase)
            self.M = self.M * C_phase

        return self.M

    @_actualize_
    def diattenuator_azimuth_ellipticity(self, p1, p2, az, el, global_phase=0):
        """Creates the general diattenuator with orthogonal eigenstates from the caracteristic angles of the main eigenstate.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016) pp 137.

        Parameters:
            p1 (float): [0, 1] Square root of the higher transmission for one
                eigenstate.
            p2 (float): [0, 1] Square root of the lower transmission for the other
                eigenstate.
            az (float): [0, pi]: Azimuth.
            el (float): [-pi/4, pi/]: Ellipticity.
            carac (bool): [Default: True] If false, assumes alpha is azimuth and delta is elipticity.
            global_phase (float): Global phase introduced by the optical element. Default: 0.

        Returns:
            (numpy.matrix): 2x2 matrix
        """
        # If we are not working tith the caracteristic angles, but with azimuth and
        # elipticity, convert them
        alpha, delta = azimuth_elipt_2_carac_angles(az=az, el=el)
        self.diattenuator_carac_angles(p1, p2, alpha, delta)

        if global_phase % (2 * pi) != 0:
            C_phase = cexp(1j * global_phase)
            self.M = self.M * C_phase

        return self.M

    @_actualize_
    def retarder_linear(self, D=0 * degrees, angle=0 * degrees,
                        global_phase=0):
        """Creates a linear retarder.

        Parameters:
            D (float): delay produced by retarder.
            angle (float): angle of polarizer axis, in radians.
            global_phase (float): Global phase introduced by the optical element. Default: 0.

        Returns:
            (numpy.matrix): 2x2 matrix
        """

        self.M = matrix(array([[1, 0], [0, exp(1j * D)]]), dtype=complex)
        self.rotate(angle)

        if global_phase % (2 * pi) != 0:
            C_phase = cexp(1j * global_phase)
            self.M = self.M * C_phase

        return self.M

    @_actualize_
    def retarder_material(self,
                          ne=1,
                          no=1,
                          d=1 * um,
                          wavelength=0.6328 * um,
                          angle=0 * degrees,
                          global_phase=0):
        """Creates a 2x2 retarder using delay or physical properties of an anisotropic material.

        .. math::  \phi  = 2 \pi (n_e-n_o) d / \lambda.

        Parameters:
            ne (float): extraordinary index.
            n0 (float): ordinary index.
            d (float): thickness of the sheet in microns.
            wavelength (float): wavelength of the illumination.
            angle (float): angle of polarizer axis, in radians.
            global_phase (float): Global phase introduced by the optical element. Default: 0.

        Returns:
            (numpy.matrix): 2x2 matrix
        """

        phase = 2 * pi * (ne - no) * d / wavelength

        self.M = matrix(array([[1, 0], [0, exp(1j * phase)]]), dtype=complex)
        self.rotate(angle)

        if global_phase % (2 * pi) != 0:
            C_phase = cexp(1j * global_phase)
            self.M = self.M * C_phase

        return self.M

    @_actualize_
    def retarder_carac_angles(self, D, alpha, delta, global_phase=0):
        """Function that calculates the most general homogeneous diattenuator from the characteristic angles of the fast eigenstate.

        References:
            "Polarized light and the Mueller Matrix approach", J. J. Gil, pp 125.

        Parameters:
            D (float): [0, pi] Delay.
            alpha (float): [0, pi/2]: tan(alpha) is the ratio between amplitudes of the eigenstates  in Jones formalism.
            delta (float): [0, 2*pi]: phase difference between both components of the eigenstates in Jones formalism.
            global_phase (float): Global phase introduced by the optical element. Default: 0.

        Returns:
            (numpy.matrix): 2x2 matrix
        """
        # Restrict measured values to the correct interval
        alpha = put_in_limits(alpha, "alpha")
        delta = put_in_limits(delta, "delta")
        # Compute the common operations
        sa, ca = (sin(alpha), cos(alpha))
        s2a, sD = (sin(2 * alpha), sin(D / 2))
        ed, edm = (cmath.exp(1j * delta), cmath.exp(-1j * delta))
        eD, eDm = (cmath.exp(1j * D / 2), cmath.exp(-1j * D / 2))
        # Calculate the Jones matrix
        self.M = matrix(
            array([[ca**2 * eD + sa**2 * eDm, 1j * s2a * sD * edm],
                   [1j * s2a * sD * ed, ca**2 * eDm + sa**2 * eD]]))

        if global_phase % (2 * pi) != 0:
            C_phase = cexp(1j * global_phase)
            self.M = self.M * C_phase

        return self.M

    @_actualize_
    def retarder_azimuth_ellipticity(self, D, az, el, global_phase=0):
        """Function that calculates the most general homogeneous diattenuator from the characteristic angles of the fast eigenstate.

        References:
            "Polarized light and the Mueller Matrix approach", J. J. Gil, pp 125.

        Parameters:
            D (float): [0, pi] Delay.
            az (float): [0, pi]: Azimuth.
            el (float): [-pi/4, pi/4]: Ellipticity.
            global_phase (float): Global phase introduced by the optical element. Default: 0.

        Returns:
            (numpy.matrix): 2x2 matrix
        """
        # Transform az and el to carac angles
        alpha, delta = azimuth_elipt_2_carac_angles(az, el)
        # Use that method
        self.retarder_carac_angles(D=D, alpha=alpha, delta=delta)

        if global_phase % (2 * pi) != 0:
            C_phase = cexp(1j * global_phase)
            self.M = self.M * C_phase

        return self.M

    @_actualize_
    def quarter_waveplate(self, angle=0 * degrees, global_phase=0):
        """Jones matrix of an ideal quarter-waveplate :math:`\lambda/4`..

        Parameters:
            angle (float): angle of plate fast axis, in radians.
            global_phase (float): Global phase introduced by the optical element. Default: 0.

        Returns:
            (numpy.matrix): 2x2 matrix
        """
        self.retarder_linear(D=pi / 2, angle=angle)

        if global_phase % (2 * pi) != 0:
            C_phase = cexp(1j * global_phase)
            self.M = self.M * C_phase

        return self.M

    @_actualize_
    def half_waveplate(self, angle=0, global_phase=0):
        """Jones matrix of an ideal half-waveplate :math:`\lambda/2`.

        Parameters:
            angle (float): angle of plate fast axis, in radians.
            global_phase (float): Global phase introduced by the optical element. Default: 0.

        Returns:
            (numpy.matrix): 2x2 matrix
        """
        self.retarder_linear(D=pi, angle=angle)

        if global_phase % (2 * pi) != 0:
            C_phase = cexp(1j * global_phase)
            self.M = self.M * C_phase

        return self.M

    def inverse(self, returns_matrix=True, keep=True):
        """Calculates the inverse matrix of the Mueller matrix.

        Parameters:
            keep (bool): if True, the original element is not updated. Default: False.
            returns_matrix (bool): if True returns a matrix, else returns an instance to object. Default: True.

        Returns:
            (numpy.matrix or Mueller object): 4x4 matrix.
        """
        # Caluclate inverse
        if keep:
            M2 = Jones_matrix(self.name + '_inv')
            M2.from_matrix((self.M).I)
        else:
            self.from_matrix((self.M).I)
        if returns_matrix:
            return M2.M
        else:
            return M2


class Parameters_Jones_Matrix(object):
    """Class for Jones Matrix Parameters

    Parameters:
        jones_matrix (Jones_matrix): Jones Matrix

    Attributes:
        self.M (Jones_matrix)
        self.dict_params (dict): dictionary with parameters
    """

    def __init__(self, Jones_matrix, name=''):
        self.M = Jones_matrix
        self.name = name
        self.dict_params = {}

    def __repr__(self):
        """Print all parameters."""
        self.get_all()
        text = "parameters of {}:\n".format(self.name)
        text = text + "    is_homogeneous: {0:}\n".format(
            self.dict_params['is_homogeneous'])
        text = text + "    delay:          {:2.3f}ª\n".format(
            self.dict_params['retardance'] / degrees)
        text = text + "    diattenuation:  {:2.3f}\n".format(
            self.dict_params['diattenuation'])

        return text

    def get_all(self):
        """Stores in self.dict_params a dictionary with all the parameters of Jones Matrix.

        Returns:
            (dict): Dictionary with parameters of Jones Matrix.
        """
        self.dict_params['retardance'] = self.retardance()
        self.dict_params['diattenuation'] = self.diattenuation()
        self.dict_params['is_homogeneous'] = self.is_homogeneous()

        return self.dict_params

    def diattenuation(self, verbose=False):
        """Calculation of the diattenuation  of a Jones Matrix.

        References:
            "Homogeneous and inhomogeneous Jones matrices", S.Y. Lu and R.A. Chipman, J. Opt. Soc. Am. A/Vol. 11, No. 2 pp. 766 (1994)

        Parameters:
            verbose (bool): if True prints data.

        Returns:
            D (float): Diattenuation."""

        J = self.M
        # Check that the matrix is homogeneous
        val, vect = np.linalg.eig(J)
        (v1, v2) = (vect[0, :], vect[1, :])
        prod = (v1 * v2.H)[0, 0]
        if abs(prod) < eps:
            # Homogeneous case
            a1, a2 = (abs(val[0]), abs(val[1]))
            D = abs(a1**2 - a2**2) / (a1**2 + a2**2)
        else:
            # Inhomogeneous case (unknown source)
            num = (2 * (1 - prod**2) * abs(val[0]) * abs(val[1]))**2
            den = (abs(val[0])**2 + abs(val[1])**2 - prod**2 *
                   (val[0] * np.conj(val[1]) + val[1] * np.conj(val[0])))**2
            D = sqrt(1 - num / den)
        if verbose is True:
            print("{} - diattenuation: {:2.3f}\n".format(self.name, D))
        return D

    def is_homogeneous(self, verbose=False):
        """Determines if matrix is homogeneous or not

        References:
            "Homogeneous and inhomogeneous Jones matrices", S.Y. Lu and R.A. Chipman, J. Opt. Soc. Am. A/Vol. 11, No. 2 pp. 766 (1994)

        Parameters:
            verbose (bool): if True prints data

        Returns:
            (bool): True if matrix is homongeneus."""

        J = self.M

        # Check that the matrix is homogeneous
        val, vect = np.linalg.eig(J)
        (v1, v2) = (vect[0, :], vect[1, :])
        prod = (v1 * v2.H)[0, 0]
        if abs(prod) < eps:
            is_hom = True
        else:
            is_hom = False

        if verbose is True:
            print("{0:} - is_homogeneous: {1:}\n".format(self.name, is_hom))

        return is_hom

    def retardance(self, verbose=False):
        """Calculation of the delay (or retardance) of a Jones element.

        References:
            "Homogeneous and inhomogeneous Jones matrices", Shih-Yau Lu and  Russell A. Chipman, J. Opt. Soc. Am. A/Vol. 11, No. 2 pp. 766 (1994)

        Parameters:
            J (matrix): 2x2 Jones matrix

        Returns:
            R (float): Retardance."""

        J = self.M

        # Check that the matrix is homogeneous
        val, vect = np.linalg.eig(J)
        (v1, v2) = (vect[0, :], vect[1, :])
        prod = (v1 * v2.H)[0, 0]
        (tr1, tr2) = (np.trace(J), np.trace(J.H * J))
        det_J = np.linalg.det(J)
        if abs(prod) < eps:
            # Homogeneous case (unknown source)
            # d1, d2 = (np.angle(val[0]), np.angle(val[1]))
            # R = abs(d1 - d2)
            # Homogeneous (refered source)
            if abs(det_J) < eps:
                delay = 2 * np.arccos(np.abs(tr1) / np.sqrt(tr2))
            else:
                num = np.abs(tr1 + det_J * np.trace(J.H) / np.abs(det_J))
                den = 2 * np.sqrt(tr2 + 2 * np.abs(det_J))
                delay = np.real(2 * np.arccos(num / den))

        else:
            # Inhomogenous (unknown source)
            # val, vect = np.linalg.eig(J.H * J)
            # (v1, v2) = (vect[0, :], vect[1, :])
            # R = 2 * np.arccos(abs(v1.H * J * v1 + v2.H * J * v2) / 2)
            # Inhomogenous (refered source)
            num = (1 - prod**2) * (abs(val[0]) + abs(val[1]))**2
            den = (abs(val[0]) + abs(val[1]))**2 - prod**2 * (
                2 * val[0] * abs(val[0]) * abs(val[1]) + np.conj(
                    val[1]) + val[1] * np.conj(val[0]))
            co = cos((np.angle(val[0]) - np.angle(val[1])) / 2)
            delay = float(2 * np.arccos(sqrt(num / den) * co))

        if verbose is True:
            print("{} - delay: {:2.3f} deg\n".format(self.name,
                                                     delay / degrees))

        return delay

    def global_phase(self):
        """Calculates the phase of the first elemento of the matrix (which is the reference for global phase in the model of py_pol).

        Returns:
            (float): phase
        """
        phase = float(np.angle(self.M[0, 0]))
        phase = phase % (2 * pi)
        return phase
