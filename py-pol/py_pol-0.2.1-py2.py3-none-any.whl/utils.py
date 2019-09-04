#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------
# Authors:    Luis Miguel Sanchez Brea and Jesus del Hoyo
# Date:       2019/01/09 (version 1.0)
# License:    GPL
# ------------------------------------
""" Common functions to classes """

import multiprocessing
import time

import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
from numpy import array, cos, matrix, pi, sin, sqrt, tan
from scipy.optimize import leastsq

from . import degrees, eps

# Angle limit variables
limAlpha = [0, pi / 2]
limDelta = [0, 2 * pi]
limAz = [0, pi]
limEl = [-pi / 4, pi / 4]


def rotation_matrix_Jones(angle=0):
    """Jones 2x2 rotation matrix.

    Parameters:
        angle (float): angle of rotation, in radians.

    Returns:
        numpy.matrix: 2x2 matrix
    """

    return matrix(
        array([[cos(angle), sin(angle)], [-sin(angle), cos(angle)]]),
        dtype=float)


def rotation_matrix_Mueller(angle=0):
    """Mueller 4x4 matrix for rotation

    References:
        Gil, Ossikovski (4.30) - p. 131
        Handbook of Optics vol 2. 22.16 (eq.8) is with changed sign in sin

    Parameters:
        angle (float): angle of rotation with respect to 0 deg.

    Returns:
        numpy.matrix: 4x4 rotation matrix

    """

    # Definicion de la matrix
    c2b = cos(2 * angle)
    s2b = sin(2 * angle)
    return np.matrix(
        np.array([[1, 0, 0, 0], [0, c2b, s2b, 0], [0, -s2b, c2b, 0],
                  [0, 0, 0, 1]]),
        dtype=float)


def azimuth_elipt_2_carac_angles(az, el):
    """Function that converts azimuth and elipticity to caracteristic angles in Jones space.

    .. math:: cos(2 \\alpha) = cos(2 \phi) * cos(2 \chi)

    .. math:: tan(\delta) = \\frac{tan(2 \chi)}{sin(2 \phi)}


    References:
        J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016), pp 137 and 1543.


    Parameters:
        az (float) [0, pi]: Azimuth (angle of rotation).
        el (float) [-pi/4, pi/4]: Elipticity angle.


    Returns:
        alpha (float) [0, pi]: tan(alpha) is the ratio between the maximum amplitudes of the polarization elipse in X-Y coordinates.
        delta (float) [0, 2*pi]: phase difference between both components of the eigenstates in Jones formalism.
    """
    # Check that the angles belong to the correct interval. If not, fix it.
    az = put_in_limits(az, "az")
    el = put_in_limits(el, "el")
    # Check circular polarization case
    if az == np.nan and (np.abs(el + pi / 4) < eps
                         or np.abs(el - pi / 4) < eps):
        alpha = pi / 4
        delta = pi / 2 + (1 - np.sign(el) * pi / 2)
    else:
        # Calculate values using trigonometric functions
        alpha = 0.5 * np.arccos(cos(2 * az) * cos(2 * el))
        # Avoid dividing by 0
        if az == 0:
            delta = np.sign(tan(2 * el)) * pi / 2
        elif az == pi:
            delta = -np.sign(tan(2 * el)) * pi / 2
        else:
            delta = np.arctan(tan(2 * el) / sin(2 * az))
        # Use the other possible value from the arcs functions if necessary
        Qel = which_quad(el)
        Qaz = which_quad(az)
        if Qel == -1:
            if Qaz == 1 or Qaz == 2:
                delta = delta % (2 * pi)
            else:
                delta = delta + pi
        elif Qel == 0:
            if Qaz in (3, 3.5, 4):
                delta = delta + pi
        else:
            if Qaz == 3 or Qaz == 4:
                delta += pi
    # Make sure the output values are in the allowed limits
    alpha = put_in_limits(alpha, "alpha")
    delta = put_in_limits(delta, "delta")
    # End
    return alpha, delta


def carac_angles_2_azimuth_elipt(alpha, delta):
    """Function that converts azimuth and elipticity to caracteristic angles in Jones space.

    .. math:: cos(2 \\alpha) = cos(2 \phi) * cos(2 \chi)

    .. math:: tan(\delta) = \\frac{tan(2 \chi)}{sin(2 \phi)}


    References:
        J. J. Gil, "Polarized light and the Mueller Matrix approach", pp 137 and 154.

    Parameters:
        alpha (float) [0, pi]: tan(alpha) is the ratio between the maximum
        amplitudes of the polarization elipse in X-Y coordinates.
        delta (float) [0, 2*pi]: phase difference between both components of
            the eigenstates in Jones formalism.

    Returns:
        az (float) [0, pi]: Azimuth (angle of rotation).
        el (float) [-pi/4, pi/4]: Elipticity angle.
    """
    # Check that the angles belong to the correct interval. If not, fix it.
    alpha = put_in_limits(alpha, "alpha")
    delta = put_in_limits(delta, "delta")
    # Check circular polarization case
    if np.abs(alpha - pi / 4) < eps and (np.abs(delta - pi / 2) < eps
                                         or np.abs(delta - 3 * pi / 2) < eps):
        az = np.nan
        el = np.sign(delta - pi) * pi / 4
    else:
        # Calculate values using trigonometric functions
        az = 0.5 * np.arctan(tan(2 * alpha) * cos(delta))
        el = 0.5 * np.arcsin(sin(2 * alpha) * sin(delta))
        # Use the other possible value from the arcs functions if necessary
        Qalpha = which_quad(alpha)
        Mdelta = which_quad(delta, octant=False)
        if Qalpha == 2:
            az += pi / 2
        else:
            if Mdelta == 2 or Mdelta == 3:
                az += pi
        if Mdelta == 0 and Qalpha == 2.5:
            az += pi
        elif Mdelta == 1.5 or Mdelta == 2.5 or Mdelta == 3.5:
            if Qalpha == 1.5 or Qalpha == 2.5:
                az += pi
    # Check that the outpit values are in the correct interval
    az = put_in_limits(az, "az")
    el = put_in_limits(el, "el")
    return az, el


def extract_azimuth_elipt(vector):
    """Function that extracts azimuth and ellipticity from a diattenuation, polarizance or retardance vector. All of them are of the form of: TODO.

    .. math:: cos(2 \\alpha) = cos(2 \phi) * cos(2 \chi)

    .. math:: tan(\delta) = \\tan(2 \chi) / sin(2 \phi)


    References:
        J. J. Gil, "Polarized light and the Mueller Matrix approach", pp 128 and 142.

    Parameters:
        vector (np.array 1x3 or 3x1): vector to be measured

    Returns:
        az (float) [0, pi]: Azimuth (angle of rotation).
        el (float) [-pi/4, pi/4]: Elipticity angle.
    """
    # Use row vectors
    if iscolumn(vector):
        vector = matrix(vector).T
    # normalize the vector
    if np.linalg.norm(vector) > eps:
        vector = vector / np.linalg.norm(vector)
    # Start by calculating ellipticity, which is isolated
    el = 0.5 * np.arcsin(vector[0, 2])
    # Now, calculate azimuth using the first therm, as it has the cos
    az = 0.5 * np.arccos(vector[0, 0] / cos(2 * el))
    # Correct when azimuth is >= pi/2
    if vector[0, 1] < 0:
        az = pi - az
    return az, el


def extract_carac_angles(vector):
    """Function that extracts azimuth and ellipticity from a diattenuation, polarizance or retardance vector. All of them are of the form of: TODO.

    .. math:: cos(2 \\alpha) = cos(2 \phi) * cos(2 \chi)

    .. math:: tan(\delta) = \\frac{tan(2 \chi)}{sin(2 \phi)}


    References:
        J. J. Gil, "Polarized light and the Mueller Matrix approach", pp 128 and 142.

    Parameters:
        vector (np.array 1x3 or 3x1): vector to be measured

    Returns:
        alpha (float) [0, pi]: tan(alpha) is the ratio between the maximum amplitudes of the polarization elipse in X-Y coordinates.
        delta (float) [0, 2*pi]: phase difference between both components of the eigenstates in Jones formalism.
    """
    # Do it with azimuth and ellipticity and convert
    az, el = extract_azimuth_elipt(vector)
    alpha, delta = azimuth_elipt_2_carac_angles(az, el)
    return alpha, delta


def which_quad(angle, octant=True):
    """Auxiliary function to calculate which quadrant or octant angle belongs to.
    Half angles means that it is exactly between two quarants.

    Parameters:
        (float): Angle to determine the quadrant.

    Returns:
        (float): Quadrant
    """
    if octant:
        if angle == -pi / 4:
            q = -1.5
        elif angle < 0:
            q = -1
        elif angle == 0:
            q = 0
        elif angle < pi / 4:
            q = 1
        elif angle == pi / 4:
            q = 1.5
        elif angle < pi / 2:
            q = 2
        elif angle == pi / 2:
            q = 2.5
        elif angle < 3 / 4 * pi:
            q = 3
        elif angle == 3 / 4 * pi:
            q = 3.5
        elif angle < 2 * pi:
            q = 4
        else:
            q = 4.5
    else:
        if angle == 0:
            q = 0
        elif angle < pi / 2:
            q = 1
        elif angle == pi / 2:
            q = 1.5
        elif angle < pi:
            q = 2
        elif angle == pi:
            q = 2.5
        elif angle < 3 * pi / 2:
            q = 3
        elif angle == 3 / 2 * pi:
            q = 3.5
        else:
            q = 4
    return q


def put_in_limits(x, type):
    """When dealing with polarization elipse coordinates, make sure that they
    are in the valid limits, which are set in the declaration of this class.

    Parameters:
        x (float): Value
        type (string): Which type of variable is: alpha, delta, az or el.

    Returns:
        y (float): Corresponding angle inside the valid limits.
    """
    # Change x only if necessary
    if type in ("alpha", "Alpha"):
        if x < limAlpha[0] or x >= limAlpha[1]:
            aux = sin(x)
            x = np.arcsin(abs(aux))
    elif type in ("delta", "Delta", "delay", "Delay"):
        if x < limDelta[0] or x >= limDelta[1]:
            x = x % (2 * pi)
    elif type in ("az", "Az", 'azimuth', 'Azimuth'):

        if x < limAz[0] or x >= limAz[1]:
            aux = cos(x)
            x = np.arccos(abs(aux))
    elif type in ("el", "El", 'ellipticity', 'Ellipticity'):
        if x < limEl[0] or x >= limEl[1]:
            aux = tan(x)
            if aux > 1:
                aux = 1 / aux
            x = np.arctan(abs(aux))

    return x


def execute_multiprocessing(__function_process__,
                            dict_parameters,
                            num_processors,
                            verbose=False):
    """Executes multiprocessing reading a dictionary.

    Parameters:
        __function_process__ (func): function to process, it only accepts a dictionary
        dict_parameters (dict): dictionary / array with parameters
        num_processors (int): Number of processors. if 1 no multiprocessing is used
        verbose (bool): Prints processing time.

    Returns:
        data: results of multiprocessing
        (float): processing time

    Example:

    .. code-block:: python

        def __function_process__(xd):
            x = xd['x']
            y = xd['y']
            # grt = copy.deepcopy(grating)
            suma = x + y
            return dict(sumas=suma, ij=xd['ij'])

        def creation_dictionary_multiprocessing():
            # create parameters for multiprocessing
            t1 = time.time()
            X = sp.linspace(1, 2, 10)
            Y = sp.linspace(1, 2, 1000)
            dict_parameters = []
            ij = 0
            for i, x in enumerate(X):
                for j, y in enumerate(Y):
                    dict_parameters.append(dict(x=x, y=y, ij=[ij]))
                    ij += 1
            t2 = time.time()
            print "time creation dictionary = {}".format(t2 - t1)
            return dict_parameters
    """
    t1 = time.time()
    if num_processors == 1 or len(dict_parameters) < 2:
        data_pool = [__function_process__(xd) for xd in dict_parameters]
    else:
        pool = multiprocessing.Pool(processes=num_processors)
        data_pool = pool.map(__function_process__, dict_parameters)
        pool.close()
        pool.join()
    t2 = time.time()
    if verbose is True:
        print("num_proc: {}, time={}".format(num_processors, t2 - t1))
    return data_pool, t2 - t1


def divide_in_blocks(M):
    """Function that creates a mueller matrix from their block components.

    References: J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016)

    Parameters:
        M (4x4 matrix): Mueller matrix of the diattenuator.

    Returns:
        D (1x3 or 3x1 float): Diattenuation vector.
        P (1x3 or 3x1 float): Diattenuation vector.
        m (3x3 matrix): Small m matrix.
        m00 (float, default 1): [0, 1] Parameter of average intensity.
    """
    m00 = M[0, 0]
    if m00 > 0:
        M = M / m00
    D = matrix(M[0, 1:4])
    P = matrix(M[1:4, 0])
    m = matrix(M[1:4, 1:4])
    return D, P, m, m00


def list_of_objects_depercated(size, type_object):
    """Creates a list of objects."""
    try:
        N = len(size)
    except:
        N = 1
    dim0 = []
    if N == 1:
        for ind in range(size):
            dim0.append(type_object(' '))
    elif N == 2:
        for ind in range(size[0]):
            dim1 = []
            for ind in range(size[1]):
                dim1.append(type_object(' '))
            dim0.append(dim1)
    elif N == 3:
        for ind in range(size[0]):
            dim1 = []
            for ind in range(size[1]):
                dim2 = []
                for ind in range(size[2]):
                    dim2.append(type_object(' '))
                dim1.append(dim2)
            dim0.append(dim1)
    elif N == 4:
        for ind in range(size[0]):
            dim1 = []
            for ind in range(size[1]):
                dim2 = []
                for ind in range(size[2]):
                    dim3 = []
                    for ind in range(size[3]):
                        dim3.append(type_object(' '))
                    dim2.append(dim3)
                dim1.append(dim2)
            dim0.append(dim1)
    return dim0


def list_of_objects(size, type_object):
    """Creates a list of objects."""
    if isinstance(size, (int, float)):
        size = [size]
    Ndims = len(size)
    list = []
    for ind in range(size[0]):
        if Ndims > 1:
            list.append(list_of_objects(size[1:Ndims + 1], type_object))
        else:
            list.append(type_object(' '))

    return list


def _pickle_method(method):
    """
    function for multiprocessing in class
    """
    func_name = method.__func__.__name__
    obj = method.__self__
    cls = method.__self__.__class__
    # deal with mangled names
    if func_name.startswith('__') and not func_name.endswith('__'):
        cls_name = cls.__name__.lstrip('_')
        func_name = '_' + cls_name + func_name
    return _unpickle_method, (func_name, obj, cls)


def _unpickle_method(func_name, obj, cls):
    """
    function for multiprocessing in class
    """
    for cls in cls.__mro__:
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)


def iscolumn(v):
    """Checks if the array v is a column array or not.

    Parameters:
        v (array): Array to be tested.

    Returns:
        cond (bool): True if v is a column array."""

    cond = False
    s = v.shape
    if len(s) == 2:
        if s[1] == 1 and s[1] > 1:
            cond = True
    return cond


def isrow(v):
    """Checks if the array v is a row array or not.

    Parameters:
        v (array): Array to be tested.

    Returns:
        cond (bool): True if v is a row array."""

    cond = False
    s = v.shape
    if len(s) == 1:
        cond = True
    elif len(s) == 2:
        if s[0] == 1:
            cond = True
    return cond


def delta_kron(a, b):
    """Computes the Kronecker delta.

    Parameters:
        a, b (int): Numbers.

    Returns:
        d (int): Result."""

    if a == b:
        d = 1
    else:
        d = 0
    return d


def order_eig(q, m):
    """Function that orders the eigenvalues from max to min, and then orders
    the eigenvectors following the same order.

    Parameters:
        q (float array): Array of eigenvalues.
        m (numpy matrix): Matrix with the eigenvectors as columns.

    Returns:
        q (float array): Array of ordered eigenvalues.
        m (numpy matrix): Matrix with the eigenvectors ordered as columns.
        """
    # Find correct order
    order = np.flip(np.argsort(q), 0)
    # Order eigenvalues
    q = np.flip(np.sort(q), 0)
    # Order eigenvectors
    s = m.shape
    m2 = np.zeros(s, dtype=complex)
    for ind in range(s[1]):
        ind2 = order[ind]
        m2[:, ind] = np.squeeze(m[:, ind2])
    # Differentiate between real and complex cases
    Im = np.linalg.norm(np.imag(q))
    if Im < eps:
        q = np.real(q)
    Im = np.linalg.norm(np.imag(m2))
    if Im < eps:
        m2 = np.real(m2)
    # Return
    return q, np.matrix(m2, dtype=complex)


def check_eig(q, m, M):
    """Function that checks the eigenvalues and eigenvectors."""
    dif = np.zeros(len(q))
    for ind, qi in enumerate(q):
        v = m[:, ind]
        v2 = M * v
        d = v2 - qi * v
        dif[ind] = np.linalg.norm(d)
        print(("The eigenvalue {} has an eigenvector {}.".format(qi, v.T)))
    M2 = m * M * m.T
    d = M2 - M
    dif2 = sqrt(np.sum(np.square(d)))
    dif3 = (abs(d)).max()
    d = m.T - m.I
    dif4 = sqrt(np.sum(np.square(d)))
    print('The eigenvalues are:')
    print(q)
    print('The deviation respect to the eigenvectors is:')
    print(dif)
    print(
        ('The mean square difference in the decomposition is: {}.'.format(dif2)
         ))
    print(('The maximum difference in the decomposition is: {}.'.format(dif3)))
    print(('The matrix of eigenvalues is orthogonal with deviation {}'.format(
        dif4)))
    print(M)
    print(M2)


# def seq(start, stop, step=1):
#     n = int(round((stop - start) / float(step)))
#     if n > 1:
#         return ([start + step * i for i in range(n + 1)])
#     else:
#         return ([])


def distance(x1, x2):
    """
    Compute distance between two vectors.

    Arguments:
        x1 (numpy.array): vector 1
        x2 (numpy.array): vector 2

    Returns:
        (float): distance between vectors.
    """
    x1 = array(x1)
    x2 = array(x2)
    print(x1.ndim)

    dist2 = 0
    for i in range(x1.ndim):
        dist2 = dist2 + (x1[i] - x2[i])**2

    return sp.sqrt(dist2)


def nearest(vector, number):
    """Computes the nearest element in vector to number.

        Parameters:
            vector (numpy.array): array with numbers
            number (float):  number to determine position

        Returns:
            (int): index - index of vector which is closest to number.
            (float): value  - value of vector[index].
            (float): distance - difference between number and chosen element.
    """
    indexes = np.abs(vector - number).argmin()
    values = vector.flat[indexes]
    distances = values - number
    return indexes, values, distances


def nearest2(vector, numbers):
    """Computes the nearest element in vector to numbers.

        Parameters:
            vector (numpy.array): array with numbers
            number (numpy.array):  numbers to determine position

        Returns:
            (numpy.array): index - indexes of vector which is closest to number.
            (numpy.array): value  - values of vector[indexes].
            (numpy.array): distance - difference between numbers and chosen elements.

    """
    indexes = np.abs(np.subtract.outer(vector, numbers)).argmin(0)
    values = vector[indexes]
    distances = values - numbers
    return indexes, values, distances


def repair_name(name_initial):
    """
    Repairs name when several angles are included.

    Example:
        M1 @45.00deg @45.00deg @45.00deg @45.00deg @45.00deg @45.00deg @45.00deg

        passes to:

        M1 @135.00deg

    Parameters:
        name_initial (str): String with the name.

    Returns:
        (str): Repaired name

    """

    num_angles = name_initial.count('@')
    if num_angles == 0:
        return name_initial
    try:
        text = "{} ".format(name_initial)

        text = text.split("@")
        name_original = text[0][0:-1]
        angle_number = 0
        for i, ti in enumerate(text[1:]):
            angle = float(ti[:-3])
            angle_number = angle_number + angle
        angle_number = np.remainder(angle_number, 360)
        name_final = "{} @{:2.2f} deg".format(name_original, angle_number)
    except:
        name_final = name_initial
    return name_final


def comparison(proposal, solution, maximum_diff=eps):
    """This functions is mainly for testing. It compares compares proposal to solution.

    Parameters:
        proposal (numpy.matrix): proposal of result.
        solution (numpy.matrix): results of the test.
        maximum_diff (float): maximum difference allowed.

    Returns:
        (bool): True if comparison is possitive, else False.
    """

    comparison1 = np.linalg.norm(proposal - solution) < maximum_diff
    comparison2 = np.linalg.norm(proposal + solution) < maximum_diff

    return comparison1 or comparison2


def params_to_list(J, verbose=False):
    """Makes a list from data provided at parameters.dict_params

        Parameters:
            J (object): Object Jones_vector, Jones_matrix, Stokes or Mueller.
            verbose (bool): If True prints the parameters

        Returns:
            (list): List with parameters from dict_params.
    """

    if J.type == 'Jones_vector':
        params = J.parameters.dict_params

        intensity = params['intensity']
        alpha = params['alpha']
        delay = params['delay']
        azimuth = params['azimuth']
        ellipticity_angle = params['ellipticity_angle']
        a, b = params['length_axes'][0], params['length_axes'][1]

        if verbose is True:
            print("({}, {}, {}, {}, {}, {}, {})".format(
                intensity, alpha, delay, azimuth, ellipticity_angle, a, b))

        return intensity, alpha, delay, azimuth, ellipticity_angle, a, b

    elif J.type == 'Stokes':
        params = J.parameters.dict_params

        intensity = params['intensity']
        amplitudes = params['amplitudes']
        degree_pol = params['degree_pol']
        degree_linear_pol = params['degree_linear_pol']
        degree_circular_pol = params['degree_circular_pol']
        alpha = params['alpha']
        delay = params['delay']
        azimuth = params['azimuth']
        ellipticity_angle = params['ellipticity_angle']
        ellipticity_param = params['ellipticity_param']
        polarized = params['polarized']
        unpolarized = params['unpolarized']

        if verbose is True:
            print("({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})".format(
                intensity, amplitudes, degree_pol, degree_linear_pol,
                degree_circular_pol, alpha, delay, azimuth, ellipticity_angle,
                ellipticity_param, polarized, unpolarized))

        return intensity, amplitudes, degree_pol, degree_linear_pol, degree_circular_pol, alpha, delay, azimuth, ellipticity_angle, ellipticity_param, polarized, unpolarized

    elif J.type == 'Jones_matrix':
        params = J.parameters.dict_params

        delay = params['delay']
        diattenuation = params['diattenuation']
        is_homogeneous = params['is_homogeneous']

        if verbose is True:
            print("({}, {}, {})".format(delay, diattenuation, is_homogeneous))

        return delay, diattenuation, is_homogeneous

    elif J.type == 'Mueller':
        pass


def fit_sine(t, data, has_draw=True):
    """fit a sine function
    """

    def optimize_func(x):
        return x[0] * np.sin(x[1] * t + x[2]) + x[3] - data

    guess_mean = np.mean(data)
    guess_std = 3 * np.std(data) / (2**0.5) / (2**0.5)
    guess_phase = 0
    guess_freq = 1
    guess_amp = 1

    # This might already be good enough for you
    data_first_guess = guess_std * np.sin(t + guess_phase) + guess_mean

    # Define the function to optimize, in this case, we want to minimize
    # the difference between the actual data and our "guessed" parameters

    est_amp, est_freq, est_phase, est_mean = leastsq(
        optimize_func, [guess_amp, guess_freq, guess_phase, guess_mean])[0]

    # recreate the fitted curve using the optimized parameters

    if has_draw is True:
        fine_t = np.arange(0, max(t), 0.1)
        data_fit = est_amp * np.sin(est_freq * fine_t + est_phase) + est_mean

        plt.figure()
        plt.plot(t, data, '.')
        plt.plot(t, data_first_guess, label='first guess')
        plt.plot(fine_t, data_fit, label='after fitting')
        plt.legend()
        plt.show()

    return est_amp, est_freq, est_phase, est_mean


# recreate the fitted curve using the optimized parameters
