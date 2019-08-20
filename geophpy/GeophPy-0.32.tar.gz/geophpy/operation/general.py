# -*- coding: utf-8 -*-
'''
   geophpy.operation.general
   -------------------------

   DataSet Object general operations routines.

   :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
   :license: GNU GPL v3.
'''

import numpy as np
import scipy
from scipy.interpolate import griddata, RectBivariateSpline, interp2d
from copy import deepcopy
from geophpy.misc.utils import *

#---------------------------------------------------------------------------#
# User defined parameters                                                   #
#---------------------------------------------------------------------------#

# list of "griddata" interpolation methods available for wumappy interface
gridding_interpolation_list = ['none', 'nearest', 'linear', 'cubic']

# List of allowed rotation angle (for z_image) for wumappy interface
rotation_angle_list = [0, 90, 180, 270]


#---------------------------------------------------------------------------#
# DataSet Basic Interpolations                                              #
#---------------------------------------------------------------------------#
def getgriddinginterpolationlist():
    '''
    cf. dataset.py
    '''
    return gridding_interpolation_list


def interpolate(dataset, interpolation="none", x_step=None, y_step=None, x_prec=2, y_prec=2, x_frame_factor=0., y_frame_factor=0.):
   ''' Dataset gridding.

   cf. :meth:`~geophpy.dataset.DataSet.interpolate`

   '''

   x, y, z = dataset.data.values.T[:3]

   # Creating a regular grid ###################################################
   # Distinct x, y values
   x_list = np.unique(x)
   y_list = np.unique(y)

   # Median step between two distinct x values
   if x_step is None:
       x_step = get_median_xstep(dataset, prec=x_prec) # add prec is None is this function
       # ...TBD... why not take the min diff value instead of the median ?
       ## Because on all parallel profiles, min can be smaller than actuall step size

   else:
       x_prec = getdecimalsnb(x_step)

   # Min and max x coordinates and number of x pixels
   xmin = x.min()
   xmax = x.max()

   xmin = (1.+x_frame_factor)*xmin - x_frame_factor*xmax
   xmax = (1.+x_frame_factor)*xmax - x_frame_factor*xmin

   xmin = round(xmin, x_prec)
   xmax = round(xmax, x_prec)

   nx = int(np.around((xmax-xmin)/x_step) + 1)

   # Median step between two distinct y values
   if y_step is None:
       y_step = get_median_ystep(dataset, prec=y_prec)
       # ...TBD... why not take the min diff value instead of the median ?

   else:
       y_prec = getdecimalsnb(y_step)

   # Determinate min and max y coordinates and number of y pixels
   ymin = y.min()
   ymax = y.max()

   ymin = (1.+y_frame_factor)*ymin - y_frame_factor*ymax
   ymax = (1.+y_frame_factor)*ymax - y_frame_factor*ymin

   ymin = round(ymin, y_prec)
   ymax = round(ymax, y_prec)

   ny = int(np.around((ymax - ymin)/y_step) + 1)

   # Regular grid
   xi = np.linspace(xmin, xmax, nx, endpoint=True)
   yi = np.linspace(ymin, ymax, ny, endpoint=True)
   X, Y = np.meshgrid(xi, yi)

   # Gridding data #############################################################
   # No interpolation
   if interpolation.lower() == "none":
      ## just project data into the grid
      ## if several data points fall into the same pixel, they are averaged
      ## don't forget to "peakfilt" the raw values beforehand to avoid averaging bad data points

      ### attempt using scipy.stats.binned_statistic_2d
      x, y, val = dataset.get_xyzvalues()
      statistic, xedges, yedges, binnumber = scipy.stats.binned_statistic_2d(
          x, y, values=val, statistic='mean',bins=[xi, yi])
      Z = statistic.T
      #Z = np.flipud(Z)
      
      #print(type(Z))
      #Z = dataset.data.z_image
      #Z[np.isnan(Z)] = 0  # replacing nan with zero, waiting for better
      #print('*** interpolate - sat', Z)
      ###

##      Z = np.zeros(X.shape)
##      Count = np.zeros(X.shape)  # nb of data points in the pixel initialization
##      #print('*** interpolate - count ', Count)
##
##      for x, y, z in dataset.data.values:
##         indx = np.where(xi+x_step/2. > x)
##         indy = np.where(yi+y_step/2. > y)
##         Z[indy[0][0], indx[0][0]] += z
##         Count[indy[0][0], indx[0][0]] += 1
##
##      idx0 = Count == 0  # index of pixel with no data
##      #print('*** interpolate - idx0', idxo)
##      Z[~idx0] = Z[~idx0]/Count[~idx0]

   # SciPy iterpolation
   elif interpolation in getgriddinginterpolationlist():
      ## perform data interpolation onto the grid
      ## the interpolation algorithm will deal with overlapping data points
      ## nevertheless don't forget to "peakfilt" the rawvalues beforehand to avoid interpolation being too much influenced by bad data points
      '''
      # Fill holes in each profiles with "nan" #######################
      ## this is to avoid filling holes with interpolated values
      nan_array = []
      for x in x_list:
         profile = np.unique(y_array[np.where(x_array == x)])
         nan_array = profile_completewithnan(x, profile, nan_array, y_step, factor=2, ymin=ymin, ymax=ymax)
      if (len(nan_array) != 0):
         completed_array = np.append(dataset.data.values, np.array(nan_array), axis=0)
         T = completed_array.T
         x_array = T[0]
         y_array = T[1]
         z_array = T[2]
      '''

      Z = griddata((x, y), z, (X, Y), method=interpolation)

      if np.all(np.isnan(Z.flatten())):  # interpolation failled
          print('griddata', Z, len(Z))
          print('griddataAllNan', np.all(np.isnan(Z)))
          return dataset

   # Other iterpolation
   else:
      # Undefined interpolation method ###############################
      # ...TBD... raise an error here !
      pass

   # Fill the DataSet Object ###################################################
   dataset.data.z_image = Z
   dataset.info.x_min = xmin
   dataset.info.x_max = xmax
   dataset.info.y_min = ymin
   dataset.info.y_max = ymax
   dataset.info.z_min = np.nanmin(Z)
   dataset.info.z_max = np.nanmax(Z)
   dataset.info.x_gridding_delta = x_step
   dataset.info.y_gridding_delta = y_step
   dataset.info.gridding_interpolation = interpolation

   return dataset


def sample(dataset):
    ''' Re-sample data at ungridded sample position from gridded Z_image.

    cf. :meth:`~geophpy.dataset.DataSet.sample`

    '''

    # Current gridded values
    X, Y = get_xygrid(dataset)
    Z = dataset.data.z_image

    idx_nan = np.isnan(Z)
    xy = np.stack((X[~idx_nan].flatten(),Y[~idx_nan].flatten())).T
    z = Z[~idx_nan].flatten()

    # ungridded values coordinates at which resample
    xiyi = dataset.data.values.T[:2].T  # [[x0, y0], [x1, y1], ...]
    zi = dataset.data.values.T[2]

    # Re-sampling
    z_interp = griddata(xy, z, xiyi, method='cubic')
    zi *= 0.
    zi += z_interp

    return dataset


def regrid(dataset, x_step=None, y_step=None, method='cubic'):
    ''' Re-grid dataset grid.

    cf. :meth:`~geophpy.dataset.DataSet.regrid`

    '''

    datasetOld = dataset.copy()
    dataset.sample()

##    # New grid step, resample the old grid by a factor 2.
##    if x_step is None:
##        x_step_old = dataset.info.x_gridding_delta
##        prec = getdecimalsnb(x_step_old)
##        x_step = np.around(x_step_old, prec)
##
##    if y_step is None:
##        y_step_old = dataset.info.y_gridding_delta
##        prec = getdecimalsnb(y_step_old)
##        y_step = np.around(y_step_old, prec)

    # Re-gridding dataset
    dataset.interpolate(x_step=x_step, y_step=y_step, interpolation=method)

    # Filling DataSet Object
    dataset.data.values = datasetOld.data.values

    return dataset


def histo_fit(dataset, valfilt=False):
    ''' Fit dataset histogram distribution. '''

    # Fit on ungridded dataset values
    if valfilt or dataset.data.z_image is None:
        data = dataset.get_values()

    # Fit on gridded dataset values
    else:
        data = dataset.get_grid_values()

    # Normal (gaussian) fit
    #    data = scipy.stats.norm.fit(ser)
    m, s = scipy.stats.norm.fit(ser) # get mean and standard deviation
    #pdf_g = scipy.stats.norm.pdf(lnspc, m, s)
    return m, s


#---------------------------------------------------------------------------#
# DataSet Grid manipulation                                                 #
#---------------------------------------------------------------------------#
def get_xvect(dataset):
    ''' Return dataset x-coordinate grid vector. '''

    is_grid = (dataset.info is not None
               and dataset.data.z_image is not None)

    if not is_grid:
        return None

    xmin = dataset.info.x_min
    xmax = dataset.info.x_max
    nx = dataset.data.z_image.shape[1]

    return np.array([np.linspace(xmin, xmax, nx)])


def get_yvect(dataset):
    ''' Return dataset y-coordinate grid vector. '''

    is_grid = (dataset.info is not None
               and dataset.data.z_image is not None)

    if not is_grid:
        return None

    ymin = dataset.info.y_min
    ymax = dataset.info.y_max
    ny = dataset.data.z_image.shape[0]

    return np.array([np.linspace(ymin, ymax, ny)])


def get_xyvect(dataset):
    ''' Return dataset x- and y-coordinate grid vectors. '''

    x = get_xvect(dataset)
    y = get_yvect(dataset)

    return x, y

##def zimage_xcoord(dataset):
##    '''
##    Return dataset x-coordinate array of a Z_image.
##    '''
##    return np.array([np.linspace(dataset.info.x_min, dataset.info.x_max, dataset.data.z_image.shape[1])])
##
##
##def zimage_ycoord(dataset):
##    '''
##    Return dataset y-coordinate array of a Z_image.
##    '''
##    return np.array([np.linspace(dataset.info.y_min, dataset.info.y_max, dataset.data.z_image.shape[0])])


def get_xygrid(dataset):
    ''' Return dataset x and y-coordinate  grid. '''

    is_grid = (dataset.info is not None
               and dataset.data.z_image is not None)

    if not is_grid:
        return None, None

    x, y = get_xyvect(dataset)
    X, Y = np.meshgrid(x, y)

    return X, Y


def get_xgrid(dataset):
    ''' Return dataset x-coordinate  grid. '''

    return get_xygrid(dataset)[0]


def get_ygrid(dataset):
    ''' Return dataset y-coordinate  grid. '''

    return get_xygrid(dataset)[1]


def get_gridextent(dataset):
    ''' Return dataset grid extent. '''

    is_grid = (dataset.info is not None
               and dataset.data.z_image is not None)

    if not is_grid:
        return None, None, None, None

    xmin = dataset.info.x_min
    xmax = dataset.info.x_max
    ymin = dataset.info.y_min
    ymax = dataset.info.y_max

    return  xmin, xmax, ymin, ymax


def get_gridcorners(dataset):
    ''' Return dataset grid corners coordinates (BL, BR, TL, TR). '''

    is_grid = (dataset.info is not None
               and dataset.data.z_image is not None)

    if not is_grid:
        return None

    xmin = dataset.info.x_min
    xmax = dataset.info.x_max
    ymin = dataset.info.y_min
    ymax = dataset.info.y_max

    return np.array([[xmin, xmax, xmin, xmax], [ymin, ymin, ymax, ymax]])

def get_xvalues(dataset):
    ''' Return the x-coordinates from the dataset values. '''

    return dataset.data.values.T[0]


def get_yvalues(dataset):
    ''' Return the y-coordinates from the dataset values. '''

    return np.asarray(dataset.data.values.T[1])


def get_xyvalues(dataset):
    ''' Return the x- and y-coordinates from the dataset values. '''

    x = get_xvalues(dataset)
    y = get_yvalues(dataset)

    return x, y


def get_values(dataset):
    ''' Return the dataset values. '''

    return np.asarray(dataset.data.values.T[2])


def get_xyzvalues(dataset):
    ''' Return both the x, y-coordinates and dataset values. '''

    x = get_xvalues(dataset)
    y = get_yvalues(dataset)
    values = get_values(dataset)

    return x, y, values


def get_boundingbox(dataset):
    ''' Return the coordinates (BL, BR, TL, TR) of the box bounding the data values. '''

    x, y = get_xyvalues(dataset)

    xmin = x.min()
    xmax = x.max()
    ymin = y.min()
    ymax = y.max()

    return np.array([[xmin, ymin], [xmax, ymin], [xmin, ymax], [xmax, ymax]])


def get_median_xstep(dataset, prec=None):
    ''' Return the median step between two distinct x values rounded to the given precision.

    Profiless are considered parallel to the y-axis. '''

    x = get_xvalues(dataset)

    if prec is None:
        prec = max(getdecimalsnb(x))

    x_list = np.unique(x)
    x_step = np.median(np.around(np.diff(x_list), prec))

    return x_step


def get_median_ystep(dataset, prec=None):
    ''' Return the median step between two distinct y values rounded to the given precision.

    Profiles are considered parallel to the y-axis. '''

    y = get_yvalues(dataset)

    if prec is None:
        prec = max(getdecimalsnb(y))

    #y_list = np.unique(y)
    #y_step = np.median(np.around(np.diff(y_list), prec))
    # Profiles are considered parallel to the y-axis, so y values have more variations than x values.
    ## using np.unique() can result in an underestimation off the median y_step.
    y_step = np.median(np.around(np.abs(np.diff(y)), prec))

    return y_step


def get_median_xystep(dataset, x_prec=None, y_prec=None):
    ''' Return the median steps between two distinct x and y values rounded to the given precisions. '''

    x_step = get_median_xstep(dataset, prec=x_prec)
    y_step = get_median_ystep(dataset, prec=y_prec)

    return x_step, y_step
##
#####
##def get_min_xstep(dataset, prec=None):
##    ''' Return the min step between two distinct x values rounded to the given precision. '''
##
##    x = get_xvalues(dataset)
##
##    if prec is None:
##        prec = max(getdecimalsnb(x))
##
##    x_list = np.unique(x)
##    x_step = np.min(np.around(np.diff(x_list), prec))
##
##    return x_step
##
##
##def get_min_ystep(dataset, prec=None):
##    ''' Return the min step between two distinct y values rounded to the given precision. '''
##
##    y = get_yvalues(dataset)
##
##    if prec is None:
##        prec = max(getdecimalsnb(y))
##
##    y_list = np.unique(y)
##    y_step = np.min(np.around(np.diff(y_list), prec))
##
##    return y_step
##
##
##def get_min_xystep(dataset, x_prec=None, y_prec=None):
##    ''' Return the min steps between two distinct x and y values rounded to the given precisions. '''
##
##    x_step = get_min_xstep(dataset, prec=x_prec)
##    y_step = get_min_ystep(dataset, prec=y_prec)
##
##    return x_step, y_step
#####

#def apodisation2d(val, apodisation_factor):
##   '''
##   2D apodisation, to reduce side effects
##
##   Parameters :
##
##   :val: 2-Dimension array
##
##   :apodisation_factor: apodisation factor in percent (0-25)
##
##   '''
#   if (apodisation_factor > 0):
#      # apodisation in the x direction
#      for profile in val.T:
#         _apoisation1d(profile, apodisation_factor)

      # apodisation in the y direction
#      for profile in val:
#         _apodisation1d(profile, apodisation_factor)



#def _apodisation1d(array1D, apodisation_factor):
##   '''
##   1D apodisation, to reduce side effects
##
##   Parameters :
##
##   :array1D: 1-Dimension array
##
##   :apodisation_factor: apodisation factor in percent (0-25)
##
##   '''
#   na = len(array1D)                                  # n is the number of array elements
#   napod = int(np.around((na * apodisation_factor)/100))     # napod is the number of array elements to treat
#   if (napod <= 1):                                   # one element at least must be treated
#      napod = 1
#   pi2 = np.pi/2.
#   for n in range(napod):                             # for napod first data
#      array1D[n] = array1D[n]*np.cos((napod-n)*pi2/napod)

#   for n in range(na-napod, na):                      # for napod last data
#      array1D[n] = array1D[n]*np.cos((n+1-na+napod)*pi2/napod)

###
##
# In the Future, MOVE TO operation.spectral
##
###
#---------------------------------------------------------------------------#
# Fourier Transform tools                                                   #
#---------------------------------------------------------------------------#
def fillnanvalues(val, indexout=False):
    '''
    Fill 'nan' values of each profile (row) using simple linear interpolation.

    Parameters
    ----------
    val: array_like
        Array where to replace the NaNs.

    indexout: bool,
        Flag to return the index (boolean indexing) of the NaNs in the original array.

    Returns
    -------
    The completed array (and the index of the NaNs in the original array).

    '''

    val_valid = np.copy(val)

    # Index of NaNs in the array
    nan_idx = np.isnan(val)

    # Data interpolation
    ## if there are NaNs in the profile, the value at the NaNs locations
    ## will be estimated using linear interpolation.
    if nan_idx.any():
        nprof = 0
        for profile in val_valid:
            nprof += 1

            # All-nan profile
            if np.isnan(profile).all():
                nan_idx = np.isnan(profile)
                profile[nan_idx] = 1  # -999

            # Missing data in the profile
            elif np.isnan(profile).any():
                nan_idx = np.isnan(profile)
                val_idx = ~nan_idx
                valid_data = profile[val_idx]
                val_interp = np.interp(nan_idx.nonzero()[0], val_idx.nonzero()[0], valid_data)
                profile[nan_idx] = val_interp

    # Return both data and nan index
    if indexout:
        return val_valid, nan_idx

    # Return data alone
    return val_valid

##def wavenumber(nx, ny, dx, dy):
##    '''
##    Computes the grid wavenumber coordinates.
##
##    Parameters
##    ----------
##    nx, ny : int
##        Dimension of grid in x (col) and y (line) directions.
##
##    dx, dy : float
##        Sample intervals in the x and y directions.
##
##    Returns
##    -------
##    kx, ky : array_like
##        The wavenumbers coordinate in the kx and ky directions.
##
##    Examples
##    --------
##    >>> ny, nx = grid.shape
##    >>> dy, dx = 0.1, 1  # grid spatial interval in m
##    >>> fourier = np.fft.fft2(grid)
##    >>> kx, ky = wavenumber(nx, ny, dx, dy)
##    >>> kx
##    array([[ 0.  ,  0.01694915,  0.03389831,  ..., -0.05084746, -0.03389831, -0.01694915]
##    [ 0.  ,  0.01694915,  0.03389831,  ..., -0.05084746, -0.03389831, -0.01694915]
##    ...
##    [ 0.  ,  0.01694915,  0.03389831,  ..., -0.05084746, -0.03389831, -0.01694915]
##    [ 0.  ,  0.01694915,  0.03389831,  ..., -0.05084746, -0.03389831, -0.01694915]])
##    >>> ky
##    array([[   0.    ,    0.    ,    0.     ,    ... ,   0.      ,   0.    ,   0.    ]
##    [ 0.02003606,  0.02003606,  0.02003606,  ..., 0.02003606, 0.02003606, 0.02003606]
##    [ 0.04007213,  0.04007213,  0.04007213,  ..., 0.04007213, 0.04007213, 0.04007213]
##    ...
##    [ -0.04007213,  -0.04007213,  -0.04007213,  ..., -0.04007213, -0.04007213, -0.04007213]
##    [ -0.02003606,  -0.02003606,  -0.02003606,  ..., -0.02003606, -0.02003606, -0.02003606]])
##
##    '''
##
##    # x-directed wavenumber
##    kx = np.fft.fftfreq(nx, d=dx)  # x-directed wavenumber vector
##    kx.shape = [-1,nx]  # ensuring line vector
##    kx = np.matlib.repmat(kx, ny, 1)  # x-directed wavenumber matrix
##
##    # y-directed wavenumber
##    ky = np.fft.fftfreq(ny, d=dy)  # y-directed wavenumber vector
##    ky.shape = [ny,-1]  # ensuring column vector
##    ky = np.matlib.repmat(ky, 1, nx)  # y-directed wavenumber matrix
##
##    return 2*np.pi*kx, 2*np.pi*ky


def wavenumber(nx, ny, dx, dy, indx=None, indy=None):
    '''
    Computes the grid wavenumber coordinates.

    Parameters
    ----------

    nx, ny : int
        Dimension of grid in x (col) and y (line) directions.

    dx, dy : float
        Sample intervals in the x and y directions.

    indx, indy : int, optional
        Index in the kx and ky directions.
        If ix or iy are None, the whole matrix is returned.

    Returns
    -------
    kx, ky : array_like
        The wavenumbers coordinate in the kx and ky directions.

    Notes
    -----
    This function is a direct adaptation from the Subroutine B.20.
    "Subroutine to calculate the wavenumber coordinates of elements
    of grids" in (Blakely, 96)[#]_.

    References
    ----------
     .. [#] Blakely R. J. 1996.
         Potential Theory in Gravity and Magnetic Applications.
         Appendix B, p396.
         Cambridge University Press.

    '''

    # Nyquist frequencies in the kx and ky directions
    nyqx = nx/2 + 1
    nyqy = ny/2 + 1

    # Index determination
    if indx is None or indy is None:
        indx = range(nx)
        indy = range(ny)

    # Wavenumbers computation
    #kx = np.empty([len(indy), len(indx)])
    #ky = np.empty([len(indy), len(indx)])
    kx = np.zeros([len(indy), len(indx)])
    ky = np.zeros([len(indy), len(indx)])
    for ix in indx:
        for iy in indy:

            # kx direction
            if ix <= nyqx:
                kx[iy][ix] = float(ix) / ((nx-1)*dx)
            else:
                kx[iy][ix] = float(ix-nx) / ((nx-1)*dx)

            # ky direction
            if iy <= nyqy:
                ky[iy][ix] = float(iy) / ((ny-1)*dy)
            else:
                ky[iy][ix] = float(iy-ny) / ((ny-1)*dy)

    return 2*np.pi*kx, 2*np.pi*ky


def apodisation2d(val, apodisation_factor):
   '''
   2D apodisation, to reduce side effects

   Parameters :

   :val: 2-Dimension array

   :apodisation_factor: apodisation factor in percent (0-25)

   Returns :
      - apodisation pixels number in x direction
      - apodisation pixels number in y direction
      - enlarged array after apodisation
   '''

   array2DTemp = []
   array2D = []

   if apodisation_factor > 0:
      # apodisation in the x direction
      nx = len(val.T[0])                                       # n is the number of array elements
      napodx = int(np.around((nx * apodisation_factor)/100))   # napod is the number of array elements to treat
      if napodx <= 1:                                        # one element at least must be treated
         napodx = 1
      for profile in val.T:
         array2DTemp.append(_apodisation1d(profile, napodx))
      array2DTemp = (np.array(array2DTemp)).T

      # apodisation in the y direction
      ny = len(array2DTemp[0])                                 # n is the number of array elements
      napody = int(np.around((ny * apodisation_factor)/100))   # napod is the number of array elements to treat
      if napody <= 1:                                        # one element at least must be treated
         napody = 1
      for profile in array2DTemp:
         array2D.append(_apodisation1d(profile, napody))
   else:                                                       # apodisation factor = 0
      array2D = val

#   return napodx, napody, np.array(array2D)
   return np.array(array2D)



def _apodisation1d(array1D, napod):
   '''
   1D apodisation, to reduce side effects

   Parameters :

   :array1D: 1-Dimension array

   :napod: apodisation pixels number

   Returns : 1-Dimension array of len(array1D) + napod elements

   '''

   pi2 = np.pi/2.

   na = len(array1D)                                 # n is the number of array elements
   nresult = na + 2*napod
   array1Dresult = []
   for n in range(napod):
      array1Dresult.append(array1D[n]*np.cos((napod-n)*pi2/napod))
   for n in range(na):
      array1Dresult.append(array1D[n])
   for n in range(na-napod, na):                      # for napod last data
      array1Dresult.append(array1D[n]*np.cos((n+1-na+napod)*pi2/napod))

   return array1Dresult


def apodisation2Dreverse(val, valwithapod, napodx, napody):
   '''
   To do the reverse apodisation
   '''
   na = len(val)
   nb = len(val[0])
   for n in range(na):
      for m in range(nb):
         val[n][m] = valwithapod[n+napody][m+napodx]

#---------------------------------------------------------------------------#
# DataSet Basic Math Operations                                             #
#---------------------------------------------------------------------------#
def stats(dataset, valfilt=False, valmin=None, valmax=None):
    '''
    cf. dataset.py
    '''

    # Statistics on dataset values or Z_images #################################
    if valfilt:
        val = dataset.data.values[:, 2]

    else:
        val = dataset.data.z_image

    # Limiting data range ######################################################
    if valmin is None:
        valmin = np.nanmin(val)

    if valmax is None:
        valmax = np.nanmax(val)

    idx = (val >= valmin) & (val <= valmax)
    val = val[idx]

    # Dataset statistics #######################################################
    return arraygetstats(val)


def multidatasetstats(datasets, valfilt=True, valmin=None, valmax=None):
    '''
    Returns basic statistics for each dataset in the Sequence of DataSet Objects
    '''

    mean, std, median, Q1, Q3, IQR = [], [], [], [], [], []

    for dataset in datasets:
        datasetstats = stats(dataset, valfilt=valfilt, valmin=valmin, valmax=valmax)
        mean.append(datasetstats[0])
        std.append(datasetstats[1])
        median.append(datasetstats[2])
        Q1.append(datasetstats[3])
        Q3.append(datasetstats[4])
        IQR.append(datasetstats[5])

    return mean, std, median, Q1, Q3, IQR


def add_constant(dataset, constant=0, valfilt=True, zimfilt=True):
    '''
    cf. dataset.py
    '''
    # Data values ##############################################################
    if valfilt:
        x, y, z = dataset.data.values.T
        z += constant

    # Z_image ##################################################################
    if zimfilt and dataset.data.z_image is not None:
        dataset.data.z_image += constant
        dataset.info.z_min += constant
        dataset.info.z_max += constant

    return dataset


def times_constant(dataset, constant=1, valfilt=True, zimfilt=True):
    '''
    cf. dataset.py
    '''

    # Data values ##############################################################
    if valfilt:
        x, y, z = dataset.data.values.T
        z *= constant

    # Z_image ##################################################################
    if zimfilt and dataset.data.z_image is not None:
        dataset.data.z_image *= constant
        dataset.info.z_min *= constant
        dataset.info.z_max *= constant

    return dataset


#---------------------------------------------------------------------------#
# DataSet Basic Manipulations                                               #
#---------------------------------------------------------------------------#
def copy(dataset):
    '''
    cf. dataset.py
    '''
    return deepcopy(dataset)


def setmedian(dataset, median=None, profilefilt=False, valfilt=False, setmethod='additive'):
    '''
    cf. dataset.py
    '''

    # No value provided for the median #########################################
    if median is None:
        return dataset

    # Set each profile's median ################################################
    if profilefilt:
        # Setting data values
        if valfilt:
            # ...TBD...
            pass

        # Setting data Z_image (if any)
        elif dataset.data.z_image is not None:
            zimage = dataset.data.z_image
            Zfilt = np.empty(zimage.shape)
            colnum = 0
            for col in zimage.T:
                Zfilt[:, colnum] = arraysetmedian(col, val=median, method=setmethod)
                colnum += 1

            dataset.data.z_image = Zfilt

    # Set global dataset median ################################################
    else:
        # Setting median  for data values
        x, y, z = dataset.data.values.T
        z = arraysetmedian(z, val=median, method=setmethod)
        xyz = np.vstack((x, y, z))
        dataset.data.values = xyz.T

        # Setting median for data Z_image if any
        if dataset.data.z_image is not None:
            zimage = dataset.data.z_image
            zimage = arraysetmedian(zimage, val=median, method=setmethod)
            dataset.data.z_image = zimage

    return dataset


def setmean(dataset, mean=None, profilefilt=False, valfilt=False, setmethod='additive'):
    '''
    cf. dataset.py
    '''
    # No value provided for the median #########################################
    if mean is None:
        return dataset

    # Set each profile's mean ##################################################
    if profilefilt:
        # Setting data values
        if valfilt:
            # ...TBD...
            pass

        # Setting data Z_image (if any)
        elif dataset.data.z_image is not None:
            zimage = dataset.data.z_image
            Zfilt = np.empty(zimage.shape)
            colnum = 0
            for col in zimage.T:
                Zfilt[:, colnum] = arraysetmean(col, val=mean, method=setmethod)
                colnum += 1

            dataset.data.z_image = Zfilt

    # Set global dataset mean ##################################################
    else:

        # Setting mean  for data values
        x, y, z = dataset.data.values.T
        z = arraysetmean(z, val=mean, method=setmethod)
        xyz = np.vstack((x, y, z))
        dataset.data.values = xyz.T

        # Setting mean  for data Z_image if any
        if dataset.data.z_image is not None:
            zimage = dataset.data.z_image
            zimage = arraysetmean(zimage, val=mean, method=setmethod)
            dataset.data.z_image = zimage

    return dataset


#---------------------------------------------------------------------------#
# DataSet Compatibility checks                                              #
#---------------------------------------------------------------------------#
def check_georef_compat(dataset_list):
    '''
    Check the coordinates system compatibility of a list of datasets before merging.

    Prameters
    ---------

    dataset_list: sequence of DataSet Objects.
    '''

    active, refsystem, utm_letter, utm_number = [], [], [], []

    for dataset in dataset_list:
        active.append(dataset.georef.active)
        refsystem.append(dataset.georef.refsystem)
        utm_letter.append(dataset.georef.utm_zoneletter)
        utm_number.append(dataset.georef.utm_zonenumber)

    compat = [isidentical(active), isidentical(refsystem),
              isidentical(utm_letter), isidentical(utm_number)]

    return all(compat)


def check_gridstep_compat(dataset_list):
    '''
    Check the grid step compatibility of a list of datasets before merging.

    Prameters
    ---------
    dataset_list: tuple or list
        Sequence of DataSet Objects.

    '''

    dx, dy = [], []

    for dataset in dataset_list:
        dx.append(dataset.info.x_gridding_delta)
        dy.append(dataset.info.y_gridding_delta)

    compat = [isidentical(dx), isidentical(dy)]

    return all(compat)


def check_zimage_compat(dataset_list):
    '''
    Check the Z_image compatibility (i.e presence of) of a list of datasets before merging.

    Prameters
    ---------
    dataset_list: tuple or list
        Sequence of DataSet Objects.

    '''

    iszimage = []

    for dataset in dataset_list:
        iszimage.append(dataset.data.z_image is not None)

    return isidentical(iszimage)

#---------------------------------------------------------------------------#
# DataSet Merging Tools                                                     #
#---------------------------------------------------------------------------#
def overlapmatching(datasets, tol=0.1, valfilt=True):
    '''
    '''

    # Mismatch symetrical matrix ###############################################
    ## The mismatch matrix is symetrical, only the upper-triangle is computed
    n = len(datasets)
    misma = np.zeros((n, n))  # dataset mismatch matrix
    triu = np.triu_indices(n, k=1)  # index matrix upper-triangle with (diagonal offset of 1)
    idxi, idxj = triu[0], triu[1]
    for k in range(len(idxi)):
        misma[idxi[k], idxj[k]] = dataset_mismatch(datasets[idxi[k]], datasets[idxj[k]], tol=tol, valfilt=True)

    tril = np.tril_indices(n, k=-1)
    misma[tril] = -misma[triu]
    print(misma)


def dataset_mismatch(dataset1, dataset2, tol=0.1, valfilt=True):
    '''
    Return the mismatch between overlapping element the two dataset.
    '''

    xyz1, xyz2, dist = dataset_overlap(dataset1, dataset2, tol=tol, valfilt=True)
    mismatch = arraymismatch(xyz1[:, 2], xyz2[:, 2], weighted=True, discardspurious=True)

    return mismatch


def dataset_overlap(dataset1, dataset2, tol=0.1, valfilt=True):
    '''
    Return overlapping element of the two dataset.
    '''

    if valfilt:
        xyz1 = dataset1.data.values.T
        xyz2 = dataset2.data.values.T
    #...TBD...
    else:
        return [], [], []

    arr = array1D_getoverlap(xyz1, xyz2, tol=tol)

    arr1 = arr[:, 0:3]  # x,y,z from array 1
    arr2 = arr[:, 4:7]  # x,y,z from array 2
    dist = arr[:, 8]  # actual distance between ovelapping points

    return arr1, arr2, dist


def matchedges(datasets, matchmethod='equalmedian', setval=None, valfilt=True, setmethod='additive', meanrange=None, tol=0.1):
    '''
    Match the different datasets egdes (used before datasets merging).

    Parameters
    ----------

    :datasets: tuple or list
        Sequence of DataSet Objects. Each DataSet Object must have the same coordinates system.

    Reference
    ---------
    Eder-Hinterleitner A., Neubauer W. and Melichar P., 1996.
        Restoring magnetic anomalies.
        Archaeological Prospection, vol.3, no. 4, p185-197.

    '''

    # Ensuring datasets is a list of dataset ###################################
    datasets = list(datasets)

    # Median equalization for all the sub-datasets #############################
    if matchmethod.lower() == 'equalmedian':

        # Using the mean of the sub-datasets medians
        if setval is None:
            # Basic statistics for all sub-datasets
            datasets_stat = multidatasetstats(datasets)
            medians = datasets_stat[2]
            setvalue = np.mean(medians)  # mean of the sub-datasets medians

            ###
            ###...TDB... Should we propose the
            ## Value that gives minimum variation in every subgrid ?
            ###

        # Setting all sub-datasets to a common median value
        for dataset in datasets:
            setmedian(dataset, median=setval, profilefilt=False, valfilt=False, setmethod=setmethod)

    # Mean equalization for all the sub-datasets ###############################
    elif matchmethod.lower() == 'equalmean':

        # Using the mean of the sub-datasets means
        if setval is None:

            # 'Selective mean'
            ## Mean calculated over a specific range
            ## (see Eder-Hinterleitner et al., 1996)
            if meanrange is not None:

                # Concatenation of all sub-datasets values
                valglobal = np.array([]).reshape(-1,)

                if valfilt:
                    for dataset in datasets:
                        val = dataset.data.values[:, 2]
                        valglobal = np.hstack([valglobal, val])

                else:
                    for dataset in datasets:
                        val = dataset.data.z_image.reshape(-1,)
                        valglobal = np.vstack([valglobal, val])

                # Mid XX percent data range
                valmin, valmax = arraygetmidXpercentinterval(valglobal, percent=meanrange)
                datasets_stat = multidatasetstats(datasets, valmin=valmin, valmax=valmax)

            # Classic mean of all sub-datasets
            else:
                datasets_stat = multidatasetstats(datasets)

            # mean of the sub-datasets means
            means = np.asarray(datasets_stat[0])
            setval = np.mean(means)
            ###
            ###...TDB... Should we propose the
            ## Value that gives minimum variation in every subgrid ?
            ###

        # Setting all sub-datasets to a common mean
        for dataset in datasets:
            #setmean(dataset, mean=setval, profilefilt=False, valfilt=False, setmethod=setmethod)
            ##...TDB...
            ## Is the selective mean compared to the global mean on the global medians ?
            ## In the latter case, setmedian() should be used for the offeset calculation.
            setmedian(dataset, median=setval, profilefilt=False, valfilt=False, setmethod=setmethod)


    # Edge mismatch adjustment #################################################
    ## Edge mismatch is computed between each of the sub-dataset and minimized
    ## following (Haigh J.G.B., 1992).
    else:
        pass

###...TBD...
## ??? Separate into
## MergeValues / MergeZimage / MergeHeaderso ????
###
def merge(datasetout, datasets, matchmethod=None, setval=None, setmethod='additive', meanrange=None, commonprofile=False, valfilt=False):
    ''' Merge datasets together.

    cf. :meth:`~geophpy.dataset.DataSet.merge`

    '''

    # Filter ungridded values ##################################################
##    if valfilt or dataset.data.z_image is None:
##        datasets_to_merge = []
##
##        for dataset in datasets:
##            datasets_to_merge.append(dataset.copy())
##
##            # Matching dataset edges
##
##            # Merging values
##            for dataset in datasets_to_merge:
##                val = dataset.data.values
##                valmerged = np.vstack([valmerged, val])
##
##        #values = dstmp.data.values
##        #profiles = genop.arrange_to_profile(values)
##        pass

    # Filter gridded values ####################################################
##    elif not (valfilt or dataset.data.z_image is None):
##        pass

    # Checking dataset compatibilty ############################################
    compatible = all([check_gridstep_compat(datasets),
                      check_georef_compat(datasets),
                      check_zimage_compat(datasets)])
    if not compatible:
        return

    iszimage = datasets[0].data.z_image is not None  # Z_image presence flag

    # copying datasets to not alter the original data if matching needed #######
    datasets_to_merge = []
    for dataset in datasets:
        datasets_to_merge.append(dataset.copy())

    # Matching datasets edges using specific method ############################
    if matchmethod is not None:
        matchedges(datasets_to_merge, matchmethod=matchmethod, setval=setval, setmethod=setmethod, meanrange=meanrange)
    else:
        pass

    # Merging dataset values ###################################################
    ## So far the values are simply stacked together
    ## All duplicate point are kept
    ## ...TDBD... average/supress/other duplicate
    nc = datasets_to_merge[0].data.values.shape[1]
    valmerged = np.array([]).reshape(0, nc)  # empty array with nc=3 columns
    for dataset in datasets_to_merge:
        val = dataset.data.values
        valmerged = np.vstack([valmerged, val])

    datasetout.data.values = valmerged

    # Merged DataSet Object Initialization #####################################
    ## The values from the 1st dataset are used for the parameters
    ## that are common to all datasets

    # Info parameters common to all datasets
    dx = datasets_to_merge[0].info.x_gridding_delta
    dy = datasets_to_merge[0].info.y_gridding_delta
    grid_interp = datasets_to_merge[0].info.gridding_interpolation
    plot_type = datasets_to_merge[0].info.plottype
    cmap_name = datasets_to_merge[0].info.cmapname

    datasetout.info.x_gridding_delta = dx
    datasetout.info.y_gridding_delta = dy
    datasetout.info.gridding_interpolation = grid_interp
    datasetout.info.plottype = plot_type
    datasetout.info.cmapname = cmap_name

    # Data & GeoRefSystem parameters common to all datasets
    datasetout.data.fields = datasets_to_merge[0].data.fields
    datasetout.georef.active = datasets_to_merge[0].georef.active

    datasetout.georef.active = datasets_to_merge[0].georef.active
    datasetout.georef.refsystem = datasets_to_merge[0].georef.refsystem
    datasetout.georef.utm_zoneletter = datasets_to_merge[0].georef.utm_zoneletter
    datasetout.georef.utm_zonenumber = datasets_to_merge[0].georef.utm_zonenumber

    # Info & GeoRefSystem parameters different for each dataset
    xmin, xmax, ymin, ymax, zmin, zmax = [], [], [], [], [], []
    points_list = []

    # Merged DataSet Object spatial limits #####################################
    # Retreiving value for data limits
    for dataset in datasets_to_merge:
        xmin.append(dataset.info.x_min)
        xmax.append(dataset.info.x_max)
        ymin.append(dataset.info.y_min)
        ymax.append(dataset.info.y_max)
        zmin.append(dataset.info.z_min)
        zmax.append(dataset.info.z_max)
        points_list.append(dataset.georef.points_list)

    # Z_image is present
    if  iszimage:
        xmin = min(xmin)
        xmax = max(xmax)
        ymin = min(ymin)
        ymax = max(ymax)
        zmin = min(zmin)
        zmax = max(zmax)

    # No Z_image, i.e. xmin = None etc.
    ## value are kept to None
    else:
        pass

    datasetout.georef.points_list = points_list
    datasetout.info.x_min = xmin
    datasetout.info.x_max = xmax
    datasetout.info.y_min = ymin
    datasetout.info.y_max = ymax
    datasetout.info.z_min = zmin
    datasetout.info.z_max = zmax

    # No Z_image in the datasets, merge is done ! ##############################
    if not iszimage:
        return

##    # Merging dataset Info etc.
##    # Different
##    ## Data:
##    easting_image = None    # easting array
##    northing_image = None   # northing array

    # Merging dataset Z_images #################################################
    ## So far, if several data points fall into the same pixel,
    ## they are averaged.
    ## ...TBD... possibility to keep, min max or ??? if overlaping point

    # Regular grid for merged dataset
    nx = np.around((xmax - xmin)/dx) + 1
    ny = np.around((ymax - ymin)/dy) + 1

    x = np.linspace(xmin, xmax, nx)
    y = np.linspace(ymin, ymax, ny)

    X, Y = np.meshgrid(x, y)

    # Initialization of the Merged grid
    Z = X * 0.
    P = Z.copy()  # number of data points in the pixel initialization

    for dataset in datasets_to_merge:
        # Current grid
        Xi, Yi = dataset.get_xygrid()
        Zi = dataset.data.z_image
        nl, nc = Zi.shape
        for i in range(nl):
            for j in range(nc):
                # Current point coordinates
                xi = Xi[i][j]
                yi = Yi[i][j]
                zi = Zi[i][j]

                # Index of the current point in the merged grid
                indx = np.where(x + dx/2. > xi)
                indy = np.where(y + dy/2. > yi)

                # Filling merged grid
                Z[indy[0][0], indx[0][0]] += zi
                P[indy[0][0], indx[0][0]] += 1

    # Averaging data points in the pixel initialization
    Z = Z/P
    datasetout.data.z_image = Z

###
##
# in the future, MOVE TO operation.spatial
##
###
#---------------------------------------------------------------------------#
# DataSet Profiles' detection Tools                                         #
#---------------------------------------------------------------------------#
def arrange_to_profile(values, constant=None):
    '''
    Re-arrange a list of points by profile based on constant coordinates.

    Only x, y values are used to re-arrange the data into profiles.
    Any additionnal values will be kept and managed properly.

    Parameters
    ----------
    values : 1-D array-like
        Array of points coordinates (and extra informations)
        >>> values = [[x1, y1, ...], [x2, y2, ...], ..., [xn, yn, ...]]

    constant : {None, 'x','y'}
        Profile's constant coordinates.
        If None, the constant coordinated id determined from the data as
        the coordinates with the less changes
        If 'x', the profile is parallel to the y-direction.
        If 'y', the profile is parallel to the x-direction.

    Return
    ------
    prof : 1-D array-like
        Array of x or y-constant profiles.
        >>> prof = [[ [x1, y1,...], [x2, y2,...] ],      # profile 1
                    [ [x21, y21,...], [x22, y22,...] ],  # profile 2
                    [ [...], ..., [xn, yn, ...] ]        # last profile
                       ]

    '''

    if constant is None:
        constant = estimate_constant_coordinate(values)

    profile_chooser = {'x' : arrange_to_xprofile,
                       'y' : arrange_to_yprofile}

    profiles = profile_chooser[constant](values)

    return profiles


def arrange_to_xprofile(values):
    ''' Re-arrange a list of values by profile based on constant x-coordinate.

    Only x values are used to re-arrange the data into profiles.
    Any additionnal values will be kept and managed properly.

    Parameters
    ----------
    values : 1-D array-like
        List of points coordinates (and extra informations)
        >>> values = [[x1, y1, ...], [x2, y2, ...], ..., [xn, yn, ...]]

    Return
    ------
    profiles : 1-D array-like
        Array of x-constant profiles.
        >>> profiles = [[ [x1, y1,...], [x2, y2,...] ],      # profile 1
                        [ [x21, y21,...], [x22, y22,...] ],  # profile 2
                        [ [...], ..., [xn, yn, ...] ]        # last profile
                       ]

    '''

    # Input as a list
    val = [list(point) for point in values]

    # Adding a fake point as last point marker
    fake_pts = [-999 for _ in range(len(val[0]))]  # [-999, ..., -999]
    val.append(fake_pts)

    # Rearranging into a profile list
    npts, profiles, profile_points = [], [], []
    xinit = val[0][0]
    for point in val:
        x, y = point[0:2]  # current point coordinates

        # Add point to the current profile point list
        if x == xinit:
            profile_points.append(point)  # coordinates + extra values

        # or create new profile
        elif x != xinit:

            # End of survey, storing last profile
            if x == -999:
                #profiles.append(point_list[:-1])
                profiles.append(profile_points)
                npts.append(len(profile_points))

            # New profile
            else:

                # Storing previous profile
                profiles.append(profile_points)
                npts.append(len(profile_points))

                # Creating a new profile
                profile_points = [] # new empty profile
                xinit = x  # new initial point
                profile_points.append(point) # adding current point to the new profile

    return profiles # np.asarray(profiles)


def arrange_to_yprofile(values):
    ''' Re-arrange points by profile based on constant y-coordinate.

    Only y values are used to re-arrange the data into profiles.
    Any additionnal values will be kept and managed properly.

    Parameters
    ----------
    values : 1-D array-like
        Array of points coordinates (and extra informations)
        >>> values = [[x1, y1, ...], [x2, y2, ...], ..., [xn, yn, ...]]

    Return
    ------
    profiles : 1-D array-like
        Array of y-constant profiles.
        >>> profiles = [[ [x1, y1,...], [x2, y2,...] ],      # profile 1
                        [ [x21, y21,...], [x22, y22,...] ],  # profile 2
                        [ [...], ..., [xn, yn, ...] ]        # last profile
                       ]
    '''
    # Input as a list
    val = [list(point) for point in values]

    # Adding a fake point as last point marker
    fake_pts = [-999 for _ in range(len(val[0]))]  # [-999, ..., -999]
    val.append(fake_pts)

    # Rearranging into a profile list
    npts, profiles, profile_points = [], [], []
    yinit = val[0][1]
    for point in val:
        x, y = point[0:2]  # current point

        # Add point to the current profile point list
        if y == yinit:
            profile_points.append(point)  # coordinates + extra values

        # or create new profile
        elif y != yinit:

            # End of survey, storing last profile
            if y == -999:
                #profiles.append(point_list[:-1])
                profiles.append(profile_points)
                npts.append(len(profile_points))

            # New profile
            else:

                # Storing previous profile
                profiles.append(profile_points)
                npts.append(len(profile_points))

                # Creating a new profile
                profile_points = [] # new empty profile
                yinit = y  # new initial point
                profile_points.append(point) # adding current point to the new profile

    return profiles # np.asarray(profiles)


def estimate_constant_coordinate(values):
    ''' Estimate the constant coordinated of a list of points based on
    the coordinates with the less unique values.

    Parameters
    ----------
    values : 1-D array-like
        List of points coordinates (and extra informations)
        >>> values = [[x1, y1, ...], [x2, y2, ...], ..., [xn, yn, ...]]

    Return
    ------
    constant : {'x','y'}
        Estimated profile's constant coordinates.

    '''

    constant = ['x', 'y']
    xlist = np.unique(values.T[0])
    ylist = np.unique(values.T[1])
    idx = np.argmin([xlist.size, ylist.size])

    return constant[idx]

###
##
# in the future, MOVE TO operation.spatial
##
###
#---------------------------------------------------------------------------#
# DataSet Basic Affine Transformations                                      #
#---------------------------------------------------------------------------#
def translate(dataset, shiftx=0, shifty=0):
    ''' Dataset translation.

    cf. :meth:`~geophpy.dataset.DataSet.translate`

    The z value here is the actual dataset values  and not the elevation.
    It is kept in the transformation (in place of the elevation) for
    convenience but unchanged by the transformations.

    '''

    # Data values translation #################################################
    xyz = dataset.data.values.T
    vect = np.stack((shiftx, shifty, 0))
    xyz = array1D_translate(xyz, vect) ### in the future us spatial.array_translate
    dataset.data.values = xyz.T


    # Updating dataset.info (if any) ##########################################
    if dataset.data.z_image is not None:
        dataset.info.x_min += shiftx
        dataset.info.x_max += shiftx
        dataset.info.y_min += shifty
        dataset.info.y_max += shifty

    return dataset


def get_rotation_angle_list():
    '''
    cf. dataset.py
    '''
    return rotation_angle_list


def rotate(dataset, angle=0, center=None):
    '''  Dataset rotation.

    cf. :meth:`~geophpy.dataset.DataSet.rotate`

    The z value here is the actual dataset values  and not the elevation.
    It is kept in the transformation (in place of the elevation) for
    convenience but unchanged by the transformations.

    '''

    # Authorized rotation angle ###############################################
    angle = np.mod(angle, 360)  # positive angle (-90->270)
    if angle not in [0, 90, 180, 270]:
       return dataset

    # Data values rotation ####################################################
    xyz = dataset.data.values.T
    xyz = array1D_rotate(xyz, angle=angle, center=center) ### in the future us spatial.array_translate
    dataset.data.values = xyz.T

    # Data zimage rotation ####################################################
    if dataset.data.z_image is not None:

        # zimage rotation
        angleClockWise = np.mod(angle, 360)
        k = angleClockWise//90  # number of 90° rotation (return int)
        dataset.data.z_image = np.rot90(dataset.data.z_image, k)
        ### ??? in the future use scipy.ndimage.rotate ???

        # updating dataset info (xmi, ymin, ...)
        xy = dataset.get_gridcorners()
        xy = array1D_rotate(xy, angle=angle, center=center)

        xmin, ymin = xy.min(axis=1)
        xmax, ymax = xy.max(axis=1)

        dataset.info.x_min = xmin
        dataset.info.x_max = xmax
        dataset.info.y_min = ymin
        dataset.info.y_max = ymax

        x, y = dataset.get_xyvect()
#        dx = np.median(np.diff(x))
#        dy = np.median(np.diff(y))
#        x_gridding_delta = dx
#        y_gridding_delta = dy

    return dataset
