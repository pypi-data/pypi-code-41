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
    * **from_elements**: Creates a Jones vector directly from $E_x$ and $E_y$.
    * **from_matrix**: Creates a Jones vector directly from a 2x1 matrix.
    * **from_Stokes**: Creates a Jones vector from a Stokes object. Take into account that only pure (totally polarized) Stokes vectors must be transformed to Jones vectors, and thet even for them, the global phase is unknown.
    * **linear_light**: Creates a state of linear polarization with the desired angle.
    * **circular_light**: Creates a state of circular polarization.
    * **eliptical_light**: Crea tes a state of eliptical polarization.
    * **general_azimuth_ellipticity**: Creates a Jones vector from the azimuth, ellipticity and amplitude parameters.
    * **general_carac_angles**: Creates a Jones vector from tthe caracteristic angles and amplitude parameters.

**Manipulation**
    * **rotate**: Rotates the Jones vector.
    * **check**:  Checks that the matrix stored in .M is a correct 2x1 matrix.
    * **clear**:  Removes data and name form Jones vector.
    * **normalize**: Normalize the electric field to have Intensity = 1.
    * **remove_global_phase**: Calculates the global phase of the electric field (respect to the X component) and removes it.


**Parameters**
    * **intensity**:         Calculates the intensity of the Jones vector.
    * **alpha**:             Calculates the ratio between amplitude of components Ex/Ey of electric field.
    * **delay / delta**:     Calculates the delay (phase shift) between Ex and Ey components of the electric field.
    * **carac_angles**:      Calculates both alpha and delay, the caracteristic angles of the Jones vector.
    * **azimuth**:           Calculates azimuth, that is, the orientation of major axis.
    * **ellipticity_angle**: Calculates the ellipticity angle.
    * **azimuth_ellipticity**: Calculates both azimuth and ellipticity angles.
    * **length_axes**:       Calculates the length of major and minor axis (a,b).
    * **global_phase**:      Calculates the global phase of the Jones vector (respect to the X component of the electric field).
    * **get_all**:           Returns a dictionary with all the parameters of Jones vector.
"""

import warnings
from cmath import exp as cexp
from functools import wraps

from scipy import cos, exp, matrix, sin, sqrt

from . import degrees, np, num_decimals
from .drawings import draw_ellipse_jones
from .utils import (carac_angles_2_azimuth_elipt, put_in_limits, repair_name,
                    rotation_matrix_Jones)

warnings.filterwarnings('ignore', message='PendingDeprecationWarning')


class Jones_vector(object):
    """Class for Jones vectors

    Parameters:
        name (str): name of vector for string representation

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

    def __init__(self, name='J'):
        self.name = name
        self.M = np.matrix(np.array([[0], [0]]))
        self.parameters = Parameters_Jones_Vector(self.M, self.name)
        self.type = 'Jones_vector'

    def __add__(self, other):
        """Adds two Jones vectors.

        Parameters:
            other (Jones): 2nd Jones vector to add

        Returns:
            JOnes: `s3 = s1 + s2`
        """

        j3 = Jones_vector()
        j3.from_matrix(self.M + other.M)
        j3.name = self.name + " + " + other.name
        j3.update()

        return j3

    def __sub__(self, other):
        """Substracts two Jones vectors.

        Parameters:
            other (Jones): 2nd Jones vector to add

        Returns:
            Jones: `s3 = s1 - s2`
        """

        j3 = Jones_vector()
        j3.from_matrix(self.M - other.M)
        j3.name = self.name + " - " + other.name
        j3.update()

        return j3

    def __mul__(self, other):
        """Multiplies a Jones vectors by a number.

        Parameters:
            other (float): number to multiply

        Returns:
            Stokes: `s3 = number * s2`
        """
        M3 = Jones_vector()

        if isinstance(other, (int, float, complex)):
            M3.M = self.M * other
        else:
            raise ValueError('other is Not number')
        M3.update()
        return M3

    def __rmul__(self, other):
        """Multiplies a Jones vectors by a number.

        Parameters:
            other (float): number to multiply

        Returns:
            Stokes: `s3 =  s2 * number`
        """
        M3 = Jones_vector()

        if isinstance(other, (int, float, complex)):
            M3.M = other * self.M
        # elif isinstance(other, Jones_matrix):
        #     print("in __rmul__ jones vector")
        #     M3.M = other.M * self.M
        else:
            raise ValueError('other is Not number')
        M3.update()
        return M3

    def __truediv__(self, other):
        """Divides a Jones vector.

        Parameters:
            other (number): 2nd element to divide

        Returns:
            (Jones_vector):
        """
        # Find the class of the other object
        if isinstance(other, (int, float, complex)):
            M3 = Jones_vector()
            M3.from_matrix(self.M / other)
        else:
            raise ValueError('other is Not number')
        M3.update()
        return M3

    def __repr__(self):
        """
        represents jones vector with print()
        """
        M = np.array(self.M).squeeze()
        M = np.round(M, num_decimals)
        l_name = "{} = ".format(self.name)
        difference = abs(M.round() - M).sum()

        l0 = "[{}; {}]'".format(M[0], M[1])
        # if M[0] > 0 and M[1] > 0:
        #     if difference > eps:
        #         l0 = "[{:1.3f}; {:1.3f}]'".format(M[0], M[1])
        #     else:
        #         l0 = "[{:1.0f}; {:1.0f}]'".format(M[0], M[1])
        #
        #     if difference > eps:
        #         l0 = "[{:+1.3f}; {:+1.3f}]'".format(M[0], M[1])
        #     else:
        #         l0 = "[{:+1.0f}; {:+1.0f}]'".format(M[0], M[1])
        # else:
        #     if difference > eps:
        #         l0 = "[{:+1.3f}; {:+1.3f}]'".format(M[0], M[1])
        #     else:
        #         l0 = "[{:+1.0f}; {:+1.0f}]'".format(M[0], M[1])
        #
        #     if difference > eps:
        #         l0 = "[{:+1.3f}; {:+1.3f}]'".format(M[0], M[1])
        #     else:
        #         l0 = "[{:+1.0f}; {:+1.0f}]'".format(M[0], M[1])

        return l_name + l0

    def update(self):
        """Internal function. Updates self.parameters with values of self.
        """
        self.parameters.M = self.M
        self.parameters.name = self.name
        self.parameters.get_all()

    def get(self):
        """Returns the Jones vector.

        Returns:
            (numpy.matrix) 2x1 matrix.
        """
        return self.M

    # @_actualize_
    def simplify(self, kind=1, verbose=False):
        """Condition the Jones vector to be more understable. We use three ways:

        1. Only global phase is removed in order to use the jones vector as it is.

        2. Divides the Jones vector in vector with norm ==1, amplitude and global phase.

        3. Divides the Jones vector in vector with first element = 1, amplitude factor and global phase.

        Parameters:
            kind (int): (1, 2, 3). Select the conditioning method.
            verbose (bool): shows information about conditioning.

        Returns:
            (numpy.matrix, float, float):

                Method 1: Jones_vector + 1 + global phase.

                Method 2: Jones_vector + amplitude + global phase.

                Method 3: Jones_vector + amp_factor + global phase.
        """

        j0_M = np.array(self.M).squeeze()

        global_phase = np.angle(j0_M[0])
        amplitude = np.linalg.norm(j0_M)

        if kind not in (1, 2, 3):
            print("no proper kind selection.")
            return self.M, 1, 0  # matrix, amplitude, phase
        elif kind == 1:
            j0_conditioned = j0_M / (np.exp(1j * global_phase))
            amplitude = 1
        elif kind == 2:
            j0_conditioned = j0_M / (np.exp(1j * global_phase))
            j0_conditioned = j0_conditioned / amplitude
        elif kind == 3:
            if j0_M[0] != 0:
                j0_conditioned = j0_M / j0_M[0]
                amplitude = np.abs(j0_M[0])
                global_phase = np.angle(j0_M[0])

            else:
                j0_conditioned = j0_M / j0_M[1]
                amplitude = j0_M[1]
                global_phase = np.angle(j0_M[1])

        if verbose is True:
            l0 = "[{:2.3f}; {:2.3f}]'".format(j0_conditioned[0],
                                              j0_conditioned[1])

            print(
                "{}_cond: {}, amplitude: {:2.3f}, angle: {:2.2f} deg\n".format(
                    self.name, l0, amplitude, global_phase))

        return j0_conditioned, amplitude, global_phase

    @_actualize_
    def rotate(self,
               angle=0 * degrees,
               keep=True,
               returns_matrix=False,
               is_repair_name=True):
        """Rotates a jones_vector a certain angle

        M_rotated = rotation_matrix_Jones(-angle) * self.M

        Parameters:
            angle (float): angle of rotation in radians.
            keep (bool): if True self.M is updated. If False, it returns matrix and it is not updated in self.M.
            returns_matrix (bool): if True returns a matrix, else returns an instance to object.
            is_repair_name (bool): if True tries to repair name with @ rot @ rot -> @ 2*rot.

        Returns:
            (Jones_matrix): When returns_matrix == True.
            (numpy.matrix): 2x2 matrix when returns_matrix == False.
        """

        if angle != 0:
            M_rotated = rotation_matrix_Jones(-angle) * self.M
        else:
            M_rotated = self.M

        if keep is True:
            if angle != 0:
                self.name = self.name + " @{:1.2f} deg".format(angle / degrees)
                if is_repair_name is True:
                    self.name = repair_name(self.name)
            self.M = M_rotated
            # return ?

        if returns_matrix is True:
            return M_rotated
        else:
            j3 = Jones_vector()
            j3.M = M_rotated
            j3.name = self.name
            if angle != 0:
                j3.name = j3.name + " @{:1.2f} deg".format(angle / degrees)
                if is_repair_name is True:
                    j3.name = repair_name(j3.name)
            j3.update()
            return j3

    def draw_ellipse(self, filename='', limit='', draw_arrow=False):
        """Draws polarization ellipse of Jones vector.

        Parameters:
            filename (str): name of filename to save the figure.
            limit (float): limit for drawing. If empty it is obtained from amplitudes.


        Returns:
            ax (handle): handle to axis.
            fig (handle): handle to figure.
        """

        ax, fig = draw_ellipse_jones(
            self, filename=filename, limit=limit, draw_arrow=draw_arrow)
        return ax, fig

    @_actualize_
    def clear(self):
        """Removes data and name form Jones vector.
        """
        self.from_elements(0, 0)
        self.name = ''
        return self.M

    @_actualize_
    def normalize(self, keep=True):
        """Function that transforms the Jones vector to have Intensity = 1.

        Returns:
            E (2x1 numpy matrix): Jones vector."""

        E = self.M / self.parameters.intensity()
        if keep is True:
            self.M = E
        return E

    @_actualize_
    def remove_global_phase(self, keep=True):
        """Function that transforms the Jones vector removing the global phase, so the first component of the elcric field is real and positive.

        Returns:
            E (2x1 numpy matrix): Jones vector."""
        phase = self.parameters.global_phase()
        E = self.M * cexp(-1j * phase)
        if keep is True:
            self.M = E
        return E.M

    @_actualize_
    def from_elements(self, v0, v1):
        """2x1 Custom Jones vector (v0, v1)

        Parameters:
            v0 (float): first element v[0]
            v1 (float): first element v[1]

        Returns:
            (numpy.matrix) 2x1 matrix.
        """

        self.M = matrix([[v0], [v1]])
        return self.M

    @_actualize_
    def from_matrix(self, M):
        """Create a Jones vector from an external matrix.

        Parameters:
            M (2x1 numpy matrix): New matrix

        Returns:
            (numpy.matrix) 2x1 matrix.
        """
        self.M = M
        return self.M

    @_actualize_
    def from_E(self, E):
        """Determine Jones vector from an electric field [(Ex(t), Ey(t)].

        Parameters:
            E (numpy.array): [Ex(t), Ey(t)]

        Returns:
            (numpy.matrix) 2x1 matrix.

        Todo:
            Better fitting to sinusoidal functions, and correlation between Ex-Ey
        """

        E_sum = E.sum(axis=0)

        Ex, Ey = E_sum[0], E_sum[1]

        Ax = E[:, 0].max()
        Ay = E[:, 0].max()
        delta = np.arctan2(Ey, Ex)
        print(Ax, Ay, delta)

        self.M = np.matrix(np.array([[Ax], [Ay * np.exp(1j * delta)]]))

        return self.M

    @_actualize_
    def from_Stokes(self, S, disable_warning=False):
        """Create a Jones vector from a Stokes vector. This operation is
        ambiguous, as many Jones vectors corresponds to a single pure Stokes
        vector (all of them with a global phase difference up to 2*pi). Also,
        this operation is only meaningful for pure (totally polarized) Stokes
        vectors. For the rest of them, only the polarized part is transformed,
        and a warning is printed.

        Parameters:
            S (Stokes object): Stokes vector
            disable_warning (bool): When a partial-polarized beam is used, the
                method prints a warning. If this parameter is set to False, no
                warnings are printed.

        Returns:
            (numpy.matrix) 2x1 matrix..
        """
        # If the vector is not a pure vector, show a # WARNING.
        DOP = S.parameters.degree_polarization()
        if DOP < 1 and not disable_warning:
            warnings.warn(
                'Non-pure Stokes vector transformed into a Jones vector')
        # Extract the matrix from the polarized part of the vector
        if DOP < 1:
            Smat, _ = S.parameters.polarized_unpolarized()
            S.from_matrix(Smat)
        # Calculate amplitude, azimuth and ellipticity of the vector
        amplitude = sqrt(S.parameters.intensity())
        az = S.parameters.azimuth()
        el = S.parameters.ellipticity_angle()
        # Generate a Jones vector from those parameters
        self.general_azimuth_ellipticity(az, el, amplitude)

        return self.M

    # @_actualize_
    # def to_Stokes(self, p=1):
    #     """Function that converts Jones light states to Stokes states.
    #     Parameters:
    #         p (float or 1x2 float): Degree of polarization, or
    #             [linear, circular] degrees of polarization.
    #     Returns:
    #         S (Stokes object): Stokes state."""
    #     # Check if we are using linear/circular or global polarization degree
    #
    #     if np.size(p) T 1:
    #         (p1, p2) = (p, p)
    #     else:
    #         (p1, p2) = (p[0], p[1])
    #
    #     E = self.M
    #     # Calculate the vector
    #     (Ex, Ey) = (E[0], E[1])
    #     S = np.zeros([1, 4])
    #     s0 = abs(Ex)**2 + abs(Ey)**2
    #     s1 = (abs(Ex)**2 - abs(Ey)**2) * p1
    #     s2 = 2 * np.real(Ex * np.conj(Ey)) * p1
    #     s3 = -2 * np.imag(Ex * np.conj(Ey)) * p2
    #
    #     S1 = Stokes(self.name)
    #     S1.from_elements(s0, s1, s2, s3)
    #     return S1

    @_actualize_
    def linear_light(self, amplitude=1, angle=0 * degrees):
        """Jones vector for polarizer linear light.

        Parameters:
            angle (float): angle of polarization (azimuth).

        Returns:
            (numpy.matrix) 2x1 matrix.
        """

        self.M = amplitude * matrix([[cos(angle)], [sin(angle)]])
        return self.M

    @_actualize_
    def circular_light(self, amplitude=1, kind='d'):
        """Jones vector for polarizer circular light

        Parameters:
            kind (str): 'd','r' - right, dextro, derecha.
                        'l', 'i' - left, levo, izquierda.

        Returns:
            (numpy.matrix) 2x1 matrix.
        """
        # Definicion del vector de Jones a dextrogiro o levogiro
        a0 = amplitude / sqrt(2)
        if kind in 'dr':  # derecha, right
            self.M = np.matrix([[a0], [a0 * 1j]])
        elif kind in 'il':  # izquierda, left
            self.M = np.matrix([[a0], [-a0 * 1j]])
        return self.M

    @_actualize_
    def elliptical_light(self, a=1, b=1, phase=0, angle=0):
        """Jones vector for polarizer elliptical light

        Parameters:
            a (float): amplitude of x axis
            b (float): amplitude of y axis
            phase (float): phase shift between axis
            angle (float): rotation_matrix_Jones angle respect to x axis

        Returns:
            (numpy.matrix) 2x1 matrix.
        """

        # Definicion del vector de Jones
        M = matrix([[a], [b * exp(1j * phase)]], dtype=complex)
        self.M = rotation_matrix_Jones(angle) * M
        return self.M

    @_actualize_
    def general_azimuth_ellipticity(self, az=0, el=0, amplitude=1):
        """Jones vector from azimuth, ellipticity angle and amplitude parameters.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016),     pp 6.

        Parameters:
            az (float): [0, pi]: azimuth.
            el (float): [-pi/4, pi/4]: ellipticity angle.
            amplitude (float): field amplitude

        Returns:
            (numpy.matrix) 2x1 matrix.
        """

        if az is np.nan and el is np.nan:
            raise ValueError(
                "general_azimuth_ellipticity: need total polarized light ")
        elif az is np.nan:
            j1 = 1 / np.sqrt(2)
            j2 = 1j * np.sign(el) / np.sqrt(2)
        else:
            j1 = cos(el) * cos(az) - 1j * sin(el) * sin(az)
            j2 = cos(el) * sin(az) + 1j * sin(el) * cos(az)
        self.M = amplitude * np.matrix(np.array([[j1], [j2]]))
        return self.M

    @_actualize_
    def general_carac_angles(self, alpha=0, delay=0, amplitude=1):
        """Jones vector from caracteristic angles and amplitude parameters.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016), pp 137.

        Parameters:
            alpha (float): Ratio between amplitude of components Ex/Ey of electric field.
            delay (float): Phase shift between Ex and Ey components of the electric field.
            amplitude (float): Field amplitude.

        Returns:
            numpy.matrix: 2x1 matrix
        """
        j1 = cos(alpha) * cexp(-1j * delay / 2)
        j2 = sin(alpha) * cexp(1j * delay / 2)
        self.M = amplitude * np.matrix(np.array([[j1], [j2]]))
        return self.M


class Parameters_Jones_Vector(object):
    """Class for Jones vector Parameters

    Parameters:
        jones_vector (Jones_vector): Jones Vector

    Attributes:
        self.M (Jones_vector)
    """

    def __init__(self, Jones_vector, name=''):
        self.M = Jones_vector
        self.name = name
        self.dict_params = {}
        self.dict_params['E0x'] = float(np.abs(self.M[0]))
        self.dict_params['E0y'] = float(np.abs(self.M[1]))
        self.dict_params['delay'] = float(np.angle(self.M[1])) - float(
            np.angle(self.M[0]))

    def __repr__(self):
        """Prints all the parameters"""
        self.get_all()
        a, b = self.length_axes()
        text = "parameters of {}:\n".format(self.name)
        text = text + "    intensity        : {:2.3f} arb.u\n".format(
            self.dict_params['intensity'])
        text = text + "    alpha            : {:2.3f} deg\n".format(
            self.dict_params['alpha'] / degrees)
        text = text + "    delay            : {:2.3f} deg\n".format(
            self.dict_params['delay'] / degrees)
        text = text + "    azimuth          : {:2.3f} deg\n".format(
            self.dict_params['azimuth'] / degrees)
        text = text + "    ellipticity angle: {:2.3f} deg\n".format(
            self.dict_params['ellipticity_angle'] / degrees)
        text = text + "    a, b             : {:2.3f}  {:2.3f}\n".format(a, b)
        text = text + "    phase            : {:2.3f} deg\n".format(
            self.dict_params['phase'] / degrees)
        return text

    def get_all(self):
        """Returns a dictionary with all the parameters of Jones vector.

        Returns:
            (dict): Dictionary with parameters of Jones vector.
        """
        self.dict_params['E0x'] = float(np.abs(self.M[0]))
        self.dict_params['E0y'] = float(np.abs(self.M[1]))
        self.dict_params['intensity'] = self.intensity()
        self.dict_params['alpha'] = self.alpha()
        self.dict_params['delay'] = self.delay()
        self.dict_params['azimuth'] = self.azimuth()
        self.dict_params['ellipticity_angle'] = self.ellipticity_angle()
        self.dict_params['phase'] = self.global_phase()
        self.dict_params['length_axes'] = self.length_axes()

        return self.dict_params

    def intensity(self, verbose=False):
        """Calculates the intensity of the Jones vector.

        Parameters:
            verbose (bool): if True prints the intensity

        Returns:
            (float): intensity
        """
        E0x = float(np.abs(self.M[0]))
        E0y = float(np.abs(self.M[1]))
        i1 = float(E0x**2 + E0y**2)

        if verbose:
            print("Intensity: {} arb. u.".format(i1))

        return i1

    # def irradiance_proposal(self):
    #     # TODO: (Jesus) Futuro.
    #     pass

    def alpha(self):
        """Calculates the angle ratio between amplitude of components Ex/Ey of electric field.

        References:
            D. Golstein "Polarized light" 2nd ed Marcel Dekker (2003), 3.4 eq.3-35

        Returns:
            alpha (float): [0, pi/2]: tan(alpha) is the ratio angle between amplitudes of the electric field.

        """
        E0x = float(np.abs(self.M[0]))
        E0y = float(np.abs(self.M[1]))
        alpha = np.arctan2(E0y, E0x)
        alpha = put_in_limits(alpha, 'alpha')
        return alpha

    def delay(self):
        """Calculates the delay (phase shift) between Ex and Ey components of the electric field.

        References:
            D. Golstein "Polarized light" 2nd ed Marcel Dekker (2003), 3.4 eq.3-33b

        Returns:
            delay (float): [0, 2*pi]: phase difference between both components of the electric field.
        """
        delta = float(np.angle(self.M[1])) - float(np.angle(self.M[0]))
        delta = put_in_limits(delta, 'delta')
        return delta

    def delta(self):
        """Calculates the delay (phase shift) between Ex and Ey components of the electric field. It is the same method as delay.

        References:
            D. Golstein "Polarized light" 2nd ed Marcel Dekker (2003), 3.4 eq.3-33b

        Returns:
            delay (float): [0, 2*pi]: phase difference between both components of the electric field.
        """
        return self.delay()

    def carac_angles(self):
        """Calculates the caracteristic angles of a Jones vector.

        Returns:
            alpha (float): [0, pi/2]: tan(alpha) is the ratio angle between amplitudes of the electric field.
            delay (float): [0, 2*pi]: phase difference between both components of the electric field.
        """
        alpha = self.alpha()
        delta = self.delta()
        return alpha, delta

    def azimuth(self):
        """Calculates azimuth, that is, the orientation of major axis.

        References:
            D. Golstein "Polarized light" 2nd ed Marcel Dekker (2003), 3.4 eq.3-33b

        Returns:
            az (float): [0, pi]: Azimuth.
        """

        E0x = float(np.abs(self.M[0]))
        E0y = float(np.abs(self.M[1]))
        delay = self.delay()

        az = np.arctan2(2 * E0x * E0y * cos(delay), E0x**2 - E0y**2) / 2
        az = put_in_limits(az, 'azimuth')

        return az

    def ellipticity_angle(self):
        """Calculates the ellipticity angle.

        References:
            J. J. Gil, "Polarized light and the Mueller Matrix approach", pp 137 and 154.

        Returns:
            el (float): [-pi/4, pi/4]: Ellipticity angle.
        """
        alpha = self.alpha()
        delta = self.delay()
        az, el = carac_angles_2_azimuth_elipt(alpha, delta)
        el = put_in_limits(el, 'ellipticity')
        return el

    def azimuth_ellipticity(self):
        """Calculates the azimuth and ellipticity of a Jones vector.

        References:

        Returns:
            az (float): [0, pi]: Azimuth.
            el (float): [-pi/4, pi/4]: Ellipticity angle.
        """
        az = self.azimuth()
        el = self.ellipticity_angle()
        return az, el

    def global_phase(self):
        """Calculates the phase of the first component of the electric field (which is the reference for global phase in the model of py_pol).

        Returns:
            (float): phase
        """
        phase = float(np.angle(self.M[0]))
        phase = phase % (2 * np.pi)
        return phase

    def length_axes(self):
        """Calculates the length of major and minor axis (a,b)

        References:
            D. Golstein "Polarized light" 2nd ed Marcel Dekker (2003), 3.4 eq.3-30a and 3-30b

        Returns:
            (float, float): (a,b) length of major and minor axis
        """
        E0x = float(np.abs(self.M[0]))
        E0y = float(np.abs(self.M[1]))
        delay = self.delay()
        az = self.azimuth()

        a2 = E0x**2 * cos(az)**2 + E0y**2 * sin(az)**2 + 2 * E0x * E0y * cos(
            az) * sin(az) * cos(delay)
        b2 = E0x**2 * sin(az)**2 + E0y**2 * cos(az)**2 - 2 * E0x * E0y * cos(
            az) * sin(az) * cos(delay)

        # only for testings, since a2, b2 might be slightly negative
        # print('a2, b2:', a2, b2)
        a2 = max(a2, 0)
        b2 = max(b2, 0)
        a = np.sqrt(a2)
        b = np.sqrt(b2)

        return a, b
