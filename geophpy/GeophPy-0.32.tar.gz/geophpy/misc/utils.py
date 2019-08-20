# -*- coding: utf-8 -*-
'''
   geophpy.misc.utils
   ------------------

   :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
   :license: GNU GPL v3.

'''
from __future__ import unicode_literals
import numpy as np
from scipy.optimize import curve_fit
from scipy.spatial.distance import cdist
from scipy.stats import sem
from scipy.ndimage._ni_support import _normalize_sequence


# ...TBD... following function seems not to be used !!!
def array1D_getdeltamedian(array):
    '''
    To get the median of the deltas from a 1D-array

    Parameters:

    :array: 1D-array to treat

    Returns:

    :deltamedian:
    '''
    #deltamedian = None
    #deltalist = []
    #for i in range(0,len(array)-1):
    #   if (array[i] != np.nan):
    #      prev = array[i]
    #      break
    #for val in array[i+1:]:
    #   if ((val != np.nan) and (val != prev)):
    #      deltalist.append(val - prev)
    #      prev = val
    #deltamedian = np.median(np.array(deltalist))
    #return deltamedian
    return np.median(np.diff(array))


# ...TBD... following function seems not to be used !!!
def array1D_extractdistelementslist(array):
    '''
    To extract distinct elements of a 1D-array

    Parameters:

    :array: 1D-array to treat

    Returns:

    :distlist: list of distinct values from the array
    '''
    #distlist = []
    #for val in array:
    #   if (val != np.nan):
    #      found = False
    #      for dist in distlist:
    #         if (val == dist):
    #            found = True
    #            break
    #      if (found == False):
    #         distlist.append(val)
    #return np.array(distlist)
    return np.unique(array)


def profile_completewithnan(x, y_array, nan_array, ydeltamin, factor=10, ymin=None, ymax=None):
    ''' Completes profile x with 'nan' values
    Parameters :

    :x: x value
    :y_array: 1D array to test gaps, [1,2,4,2,6,7,3,8,11,9,15,12,...]
    :nan_array: 2D array to complete with 'nan' values, [[x1, y1, 'nan'], [x2, y2, 'nan'], ...]
    :ydeltamin: delta min to test before two consecutives points, to complete with 'nan' values
    :factor: factor to take in account to test gap
    :ymin: min y position in the profile.
    :ymax: max y position in the profile.

    Returns:
        nan_array completed
    '''

    if (ymin == None):
        yprev = y_array[0]
        indexfirst = 1
    else:
        yprev = ymin
        indexfirst = 0

    for y in y_array[indexfirst:]:
        ydelta = y - yprev
        if (ydelta > (factor*2*ydeltamin)):
            # complete with 'nan' values
            for i in range(1,int(np.around(ydelta/ydeltamin))):
                nan_array.append([x, yprev+i*ydeltamin/2, np.nan])
                nan_array.append([x, y-i*ydeltamin/2, np.nan])
        yprev = y

    if (ymax != None):
        # treats the last potential gap
        ydelta = ymax - yprev
        if (ydelta > (factor*2*ydeltamin)):
            # complete with 'nan' values
            for i in range(1,int(np.around(ydelta/ydeltamin))):
                nan_array.append([x, yprev+i*ydeltamin/2, np.nan])
                nan_array.append([x, ymax-i*ydeltamin/2, np.nan])

    return nan_array


# ...TBD... following function seems not to be used !!!
def array2D_extractyprofile(x, x_array, y_array):
    '''
    To extract the y profile at x coordinate

    Parameters:

    :x: x value at which to extract the y profile

    :x_array: 1D-array containing x values associated to each y value

    :y_array: 1D-array containing y profiles

    Note: x_array and y_array must have the same dimension, but do not need to be sorted

    Returns:

    :profile: unique y values encountered at x coordinate, in ascending order
    '''
    #profile = []
    #for i in range(0, len(x_array)-1):
    #   if (x_array[i] == x):
    #      profile.append(y_array[i])
    #return np.array(profile)
    return np.unique(y_array[np.where(x_array == x)])


def make_sequence(value):
    ''' If input is scalar, make it iterable to be used in for loops.

    Inspired by :meth:`_normalize_sequence`` from :mod:`scipy.ndimage._ni_support`

    '''

    if not(hasattr(value, "__iter__") and not isinstance(value, str)):
        return [value]
    else:
        return value


def make_normalize_sequence(value, rank):
    ''' wrapper for :meth:`scipy.ndimage._ni_support._normalize_sequence`.

    If input is a scalar, create a sequence of length equal to the
    rank by duplicating the input. If input is a sequence,
    check if its length is equal to the length of array.

    '''

    return _normalize_sequence(value, rank)


##def arraygetprecison(array):
##    '''
##    To get the (maximum) number of decimals from an array.
##    '''
##    
##    precision = []
##    for value in np.ravel(array):
##        precision.append(getdecimalsnb(value))
##
##    return max(precision)

def getdecimalsnb(value):
    ''' Return the number of decimals from a float value/array.  '''

    # Decimal number for a single value
    def get_value_decimalnb(value):
        decimalsnb = 0
        test = abs(value)
        while ((test - int(test)) > 0.):
            decimalsnb += 1
            test *= 10
        return decimalsnb

    # Applying for each input element
    value = make_sequence(value)
    decimalsnb = []
    for element in value:
        decimalsnb.append(get_value_decimalnb(element))

    # single value input
    if len(decimalsnb)==1:  
        decimalsnb = decimalsnb[0]

    return decimalsnb

##def getdecimalsnb(value):
##    '''
##    To get the number of decimals from a float value
##
##    Parameters:
##
##    :value: float number to treat
##
##    Returns:
##
##    :decimalsnb: decimal precision of the value
##    '''
##    decimalsnb = 0
##### use abs(value) in order to :
#####- avoid referencing value
#####- get the correct answer when value is negative
##    test = abs(value)
##    while ((test - int(test)) > 0.):
##        decimalsnb += 1
##        test *= 10
##    return decimalsnb

def unique_multiplets(mylist):
    ''' Find the unique multiplets of a list.

    Returns the sorted unique multiplets of a list of multiplets.

    from https://stackoverflow.com/questions/48300501/how-to-remove-duplicate-tuples-from-a-list-in-python/48300601#48300601
    '''
    seen = set()
    unique = []
    
    for lst in mylist:

        # convert to hashable type
        current = tuple(lst)

        # If element not in seen, add it to both
        if current not in seen:
            unique.append(lst)
            seen.add(current)

    return unique

def find_multiplets(mylist):
    ''' Find the multiplets in the list of tuple. 
    
    

    Returns the sorted unique multiplets of a list of multiplets.
    
    '''
    
    # Find an element in list of tuples.
    Output = [item for item in mylist
          if item[0] == 3 or item[1] == 3] 
    return

def arrayshift(arr, shift, val=None):
    '''
    Roll array element.
    
    Elements that roll beyond the last position are replaced by val
    or re-introduced as the first element (if val=None).
    '''

    # No shift
    if shift==0:
        arrshift = arr
        return arrshift

    # Allocating empy (shifted) array
    arrshift = np.empty_like(arr)

    # Circular shift
    if val is None:
        arrshift = np.roll(arr, shift, axis=None)

    # Shifting & Padding with val
    if shift >= 0:
        arrshift[:shift] = val
        arrshift[shift:] = arr[:-shift]
    else:
        arrshift[shift:] = val
        arrshift[:shift] = arr[-shift:]

    return arrshift


def array_to_level(array, nblvl=256, valmin=None, valmax=None):
    '''
    Convert an array of values to brigthess level (grayscale).
    
    Parameters:

    :array: Values to be converted to brigthess level.

    :nblvl: Number of level.

    :valmin: Minimum value to consider for level definition, if None the values minimum is used.
    
    :valmax: Maximum value to consider for level definition, if None the values mmaximum is used.

    Returns:
    
    :lvl: brigthess level image (from 0to nblvl-1).
    '''
    # No min or max values provided
    if valmin==None:
        valmin = np.nanmin(array)
    if valmax==None:
        valmax = np.nanmax(array)

   # Scaling values from 0 to nblvl-1 brightness level
    step = (valmax-valmin) / (nblvl)    # conv. factor from lvl to val
    lvl = np.around((array-valmin)/step)  # brightness level
    
    # Insuring no overlimit brightness values 
    lvl[np.where(lvl<0)] = 0
    lvl[np.where(lvl>nblvl-1)] = nblvl-1

    return lvl


def level_to_array(lvl, valmin, valmax, nblvl=256):
    '''
    Convert brigthess level (grayscale) back to values.

    Parameters:

    :lvl: brigthess level image (from 0 to nblvl-1)

    :valmin: minimum value to consider for value recovering
    
    :valmax: maximum value to consider for value recovering

    :nblvl: number of level to consider for value recovering

    Returns:
    
    :array: level converted back values.
    '''
    
    # Scaling values from valmin to valmax
    step = (valmax-valmin) / (nblvl)  # conv. factor from lvl to val
    array = lvl*step + valmin  # from brightness level to values

    # Insuring no overlimit values
    array[np.where(array<valmin)] = valmin
    array[np.where(array>valmax)] = valmax

    return array


def arraygetstats(array):
    '''
    Computes the basic statistics of an array.

    Parameters:

    :array:

    Returns:

    :mean: array arithmetic mean.

    :std: array standard deviation

    :median: array median (Q2, 2nd quartile, 50th percentile).

    :Q1, Q3: array 1st and 3rd quartiles (25th and 75th percentiles).
    
    :IQR: array interquartile range.
    '''

    mean = np.nanmean(array)
    std = np.nanstd(array)
    median = np.nanmedian(array)
    Q1, Q3 = np.nanpercentile(array,[25,75])
    IQR =  Q3 - Q1

    return mean, std, median, Q1, Q3, IQR


def arraygetmidXpercentinterval(array, percent=0.80):
    '''
    get the mi X perncent interval
    '''
    
    lb = (1-percent)/2  # Lower bound in percentage
    ub = percent + lb  # Upper bound in percentage

    return np.nanpercentile(array,[lb,ub])


def arraysetmedian(array, val=0, method='additive'):
    '''
    Set an array median to a given value.

    Parameters:

    :array: array of values.

    :val: value to set the array median to.
    
    :method: method used to set the median ('additive' or 'multiplicative').
    '''

    arraymedian = np.nanmedian(array)

    # Using additive offset
    if method.lower() == 'additive':
        offset = val - arraymedian
        return array + offset

    # Using multiplicative offset (scaling)
    elif method.lower() == 'multiplicative':
        offset = val / arraymedian
        return array*offset


def arraysetmean(array, val=0, method='additive'):
    '''
    Set an array mean to a given value.

    Parameters:

    :array: array of values.

    :val: value to set the array mean to.
    
    :method: method used to set the mean ('additive' or 'multiplicative').
    '''
    arraymean = np.nanmean(array)

    # Using additive offset
    if method.lower() == 'additive':
        offset = val - arraymean
        return array + offset

    # Using multiplicative offset (scaling)
    elif method.lower() == 'multiplicative':
        offset = val / arraymean
        return array*offset

def array1D_getoverlap(arr1, arr2, tol=0.1):
    '''
    Return the overlapping elements of two arrays.

    a list of x and y coordinates and an additional z value.

    x, y and z must be on separate lineswise
    array([x1, x2, x3, ...], [y1, y2, y3, ...], [z1, z2, z3, ...]])

    Parameters:

    :array1, array2: 2D-arrays containing x and y coordinates with
        an additional z value:
        array([x1, x2, x3, ...], [y1, y2, y3, ...], [z1, z2, z3, ...]])

    :tol: tolerance (same unit as x,y) at which two points are considered
        at the same location.

    Returns:

    :arr: Overlapping coordinates and corresponding distance:
            [[x,y,val]_1, idx_1,[x,y,val]_2, idx_2, dist_1-2]
            where idx_ is the index of the overlapping value
            in the original array.
    '''

    # Pairwise distance matrix (cdist takes column array)
    arr1 = arr1.T
    arr2 = arr2.T
    xy1 = arr1[:,0:2]
    xy2 = arr2[:,0:2]
    dist = cdist(xy1,xy2)  # dist[ij] = dist(arr1[i], arr2[j])
        
    # Overlapping array
    idx = np.where(dist <= tol)
    arr = np.column_stack((arr1[idx[0]],idx[0],
                           arr2[idx[1]], idx[1],
                           np.reshape(dist[idx],(-1,1))))

    return arr

def arraymismatch(arr1, arr2, weighted=True, discardspurious=True):
    '''
    Return the mean (weighted) mismatch between arrays of the same dimensions.
    '''

    # Initial mismatch #########################################################
    # Mismatch going from arr1 to arr2
    dk = arr1-arr2
    dy = np.nanmean(dk)  
    M = dk.size
    wy = 1  # default weighting factor

    # Array 1 an 2 are equals
    if all(val==0 for val in dk):
        return 0

    # Weighting factor (Haigh 1992)
    if weighted:
        ## In Haigh (1992) : "the weighting factor is effectively
        ## the inverse square of the standard error". It is defined as
        ## wy = M**2 / np.sum((dy - dk)**2) which truly is M * (1/stde)**2.
        ## [is it a mistake in the article ?].
        ## The standard error is used here.
        #wy = M**2 / np.sum((dy - dk)**2)  # weighting factor (Haigh 1992)
        std = np.nanstd(dk)
        wy = (1/std)**2  # M / np.sum((dy - dk)**2) ?

    # Discarding spurious data #################################################
    ## data out of the range [dy - 2.5*std, dy + 2.5*std]
    ## are discarded (Haigh 1992)
    if discardspurious:
        # Non spurious data
        valmin = dy - 2.5*std
        valmax = dy + 2.5*std
        idx = (dk >= valmin) & (dk <= valmax)
        dk = dk[idx]

        # New mismatch value
        dy = np.nanmean(dk)  
        M = dk.size
        if weighted:
            std = np.nanstd(dk)
            wy = (1/std)**2

    return wy*dy


#------------------------------------------------------------------------------#
# Spatial transformations                                                      #
#------------------------------------------------------------------------------#
def array1D_centroid(array):
    '''
    Returns the centroid of an array containing
    x, y and z coordinates.

    x, y and z must be on separate lineswise
    array([x1, x2, x3, ...], [y1, y2, y3, ...], [z1, z2, z3, ...]])

    Examples:
    --------
    >>> x = np.random.rand(1,10)*100
    >>> y = np.random.rand(1,10)*100
    >>> z = np.random.rand(1,10)*100
    >>> xyz = np.array(x, y, z)
    >>> center = arraycentroid(xyz)
    '''

    return np.nanmean(array, axis=1)


def array1D_translate(array, vect):
    '''
    Translation of an array containing x, y and eventually z coordinates. 

    Array must be ?line-wise? [[x1, x2, x3, ..., xn],
                                [y1, y2, y3, ..., xn],
                                [z1, z2, z3, ..., zn]]

    Parameters:

    :array:

    :vect: vector containing the shift for each dimension.

    Returns translated array.     
    '''

    xyz_flag = array.shape[0] == 3 # True if array contains x, y and z

    # Checking z-dimension shift
    shiftx = vect[0]
    shifty = vect[1]
    if vect.size==3:
       shiftz = vect[2]
    else:
        shiftz = 0

    # Adding 'false' z=0 value to the xy-array type
    xyz = array
    if not xyz_flag:
        z = np.zeros(xyz.shape[1])
        xyz = np.vstack((xyz, z))

    # Homogeneous coordinates matrix
    idvect = np.ones(xyz.shape[1])
    xyz = np.vstack((xyz, idvect))

    # Homogeneous translation matrix
    M = np.eye(4)
    M[:,-1] = np.stack((shiftx, shifty, shiftz, 1))

    # Translating data.values
    xyz = M.dot(xyz)

    # Getting rid of homogeneous coordinates
    xyz = np.delete(xyz, -1, 0)
    if not xyz_flag:
        xyz = np.delete(xyz, -1, 0)  # 'false' z=0

    return xyz


def array1D_rotate(array, angle=90, center=None):
    '''
    Clockwise rotation about the z-axis of an array containing
    x, y and eventually z coordinates.

    Array must be ?line-wise? [[x1, x2, x3, ..., xn],
                                [y1, y2, y3, ..., xn],
                                [z1, z2, z3, ..., zn]]

    Parameters:

    :array:

    :angle:

    :center:

    Returns a rotated array trough an angle 'angle' about the point 'center'.
    '''
    angle = np.mod(angle,360)  # positive angle (-90->270)
    xyz_flag = array.shape[0] == 3 # True if array contains x, y and z

    # Center of rotation #######################################################
    # array centroid 
    if center is None:
        if xyz_flag:
            center = array1D_centroid(array[:-1,:])
        else:
            center = array1D_centroid(array[:,:])
        
    # Bottom Left as center of rotation 
    elif center.upper() in ['BL']:
        center = np.append(np.nanmin(array[0,:]), np.nanmin(array[1,:]))
        
    # Bottom Right as center of rotation 
    elif center.upper() in ['BR']:
        center = np.append(np.nanmax(array[0,:]), np.nanmin(array[1,:]))
        
    # Top Left as center of rotation 
    elif center.upper() in ['TL']:
        center = np.append(np.nanmin(array[0,:]), np.nanmax(array[1,:]))
        
    # Top Right as center of rotation 
    elif center.upper() in ['TR']:
        center = np.append(np.nanmmax(array[0,:]), np.nanmax(array[1,:]))

    # Given center vector of coordinates
    else:
        pass

    # Homogeneous coordinates matrix ###########################################
    # Rotation center homogeneous coordinates
    if center.size == 2:
        center = np.append(center,0) # adding false 0 z value
    elif center.size == 3:
        center[-1] = 0 # ensuring false 0 z value

    # Adding 'false' z=0 value to the xy-array type
    xyz = array
    if not xyz_flag:
        z = np.zeros(xyz.shape[1])
        xyz = np.vstack((xyz, z))

    # Adding homogeneous coordinates to the xyz-array type
    idvect = np.ones(xyz.shape[1])
    xyz = np.vstack((xyz, idvect))

    
    # Homogeneous matrix of rotation (clockwise)
    A = np.radians(angle)  # from degrees to radians
    cosA = np.cos(A)
    sinA = np.sin(A)
    M = np.array([[cosA, sinA, 0, 0],
                  [-sinA, cosA, 0, 0],
                  [0, 0, 1, 0],
                  [0, 0, 0, 1]])
    
    # Array rotation ###########################################################
    # Moving the center of rotation at the array centroid
    Mc = np.eye(4)
    Mc[:,-1] = np.append(-center, 1)
    xyz = Mc.dot(xyz)

    # Rotating array
    xyz = M.dot(xyz)

    # Translation to origin back to data centroid
    Mc[:,-1] = np.append(center, 1)
    xyz = Mc.dot(xyz)

    # Getting rid of homogeneous coordinates
    xyz = np.delete(xyz, -1, 0)
    if not xyz_flag:
        xyz = np.delete(xyz, -1, 0)  # 'false' z=0

    return xyz


####
# Not used yet
####
def sliding_window_1D(array, n):
    '''
    Creates a sliding windows of size n for 1D-array.
    
    This function uses stride_tricks to creates a sliding windows
    without using explicit loops. Each of the windows is return in an
    extra dimension of the array.

    n = 3

    0 |    0      0     0     0     0     0     0
    1 |    1 |    1     1     1     1     1     1
    2 |    2 |    2|    2     2     2     2     2
    3      3 |    3|    3|    3     3     3     3
    4      4      4|    4|    4|    4     4     4
    5      5      5     5|    5|    5|    5     5
    6      6      6     6     6|    6|    6|    6
    7      7      7     7     7     7|    7|    7|
    8      8      8     8     8     8     8|    8|
    9      9      9     9     9     9     9     9|
    -->
    
        - - - - - - - - > arr.size - n + 1
      | 0 1 2 3 4 5 6 7
    n | 1 2 3 4 5 6 7 8
      | 2 3 4 5 6 7 8 9
      v   
    '''

    shape = array.shape[:-1] + (array.shape[-1] - n + 1, n)  #
    strides = array.strides + (array.strides[-1],)           #

    return np.lib.stride_tricks.as_strided(array, shape=shape, strides=strides)
####
####


def isidentical(iterator):
    '''
    Check if all element of an iterable are identical
    '''
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True

    return all(first == rest for rest in iterator)




#------------------------------------------------------------------------------#
# Basic curve fitting                                                          #
#------------------------------------------------------------------------------#
def gauss_func(x, a, x0, sigma):
    r''' Gaussian function (or bell curve).

    .. math::

       f(x) = a e^{ -\frac{1}{2}\left(\frac{x-x_0}{\sigma}\right)^2 }

    Parameters
    ----------
    x : array_like
        Abscisse at which compute the fucntion.

    a : scalar
        Peak amplitude of the curve.

    x0 : scalar
        Peak position (mean of a normal ditribution).

    sigma : scalar
        Controls the curve with (standard deviation of a normal ditribution). 

    Returns
    -------

    gaussian curve

    '''

    return a*np.exp(-(x-x0)**2/(2*sigma**2)) # a*np.exp(-0.5*( (x-x0)/sigma )**2)


def gauss_fit(xdata, ydata):
    ''' Non-linear least squares fit of a gausian function to the data.

    This is a convenience wrapper of scipy.optimize.curve_fit for a gaussian function.

    Parameters
    ----------
    xdata : array_like
        The independent variable where the data is measured.
        Must be an M-length sequence or an (k,M)-shaped array for functions with k predictors.

    ydata : array_like
        The dependent data, a length M array - nominally f(xdata, ...).

    Returns
    -------
    popt : array
        Optimal values for the parameters of the gaussian fuction (a, x0 and sigma) so that the sum of the squared residuals of f(xdata, *popt) - ydata is minimized.

    pcov2d : array
        The estimated covariance of popt. The diagonals provide the variance of the parameter estimate.
        To compute one standard deviation errors on the parameters use perr = np.sqrt(np.diag(pcov)).

    '''

    popt, pcov = curve_fit(gauss_func, xdata, ydata)
    #yfit = gauss(xdata, popt[0], popt[1], popt[2])

    return popt, pcov
