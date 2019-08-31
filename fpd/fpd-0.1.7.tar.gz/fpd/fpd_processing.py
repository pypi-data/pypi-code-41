from __future__ import print_function

import numpy as np
import scipy as sp
from scipy.ndimage.filters import gaussian_filter, gaussian_filter1d
#from scipy.ndimage.measurements import center_of_mass
from scipy.signal import fftconvolve

import matplotlib as mpl
import matplotlib.pyplot as plt

from skimage.feature import canny, peak_local_max
from skimage.transform import hough_circle
from skimage import color
from skimage.draw import circle_perimeter
from skimage.feature import register_translation
#from skimage.transform import pyramid_expand
from skimage.filters import threshold_otsu
from skimage.morphology import disk, binary_closing, binary_opening

import h5py
import datetime
import os
import multiprocessing as mp
from functools import partial
import sys
import itertools
import collections
import time
import warnings
from numbers import Number
from tqdm import tqdm

from itertools import combinations
from collections import namedtuple

from . import _p3



def _check_libs():
    try:
        # check if openblas
        import ctypes
        from ctypes.util import find_library
        
        # https://stackoverflow.com/questions/29559338/set-max-number-of-threads-at-runtime-on-numpy-openblas

        #np.show_config()
        # this is hard coded so may not be always reliable
        blas_libs = np.__config__.openblas_info['libraries']
        openblas_lib = None
        if any([x.lower()=='openblas' for x in blas_libs]):
            libpath = find_library('openblas')
            openblas_lib = ctypes.cdll.LoadLibrary(libpath)
        if openblas_lib:
            ob_threads = openblas_lib.openblas_get_num_threads()
            if ob_threads !=1:
                # doesn't seem to work:
                openblas_lib.openblas_set_num_threads(1)
                print('-------------------------------------------------------------------')
                print('FPD: It looks like numpy is using OpenBLAS with %d threads.' %(ob_threads))
                print('FPD: Performance might be improved by running with 1 thread.')
                print("FPD: Try setting env variable 'OMP_NUM_THREADS=1' before importing.")
                print('-------------------------------------------------------------------\n')
    except:
        multi_thread = True
        try:
            nthreads = int(os.environ['OMP_NUM_THREADS'])
            if nthreads == 1:
                multi_thread = False
        except KeyError:
            #multi_thread = True
            pass
        
        if multi_thread:
            print('-------------------------------------------------------------------')
            print('FPD: It looks like numpy is using multiple threads.')
            print('FPD: Performance might be improved by running with 1 thread.')
            print("FPD: Try setting env variable 'OMP_NUM_THREADS=1' before importing.")
            print('-------------------------------------------------------------------\n')

_check_libs()



def cpu_thread_lib_check(n=2000):
    '''
    Check is numpy is using multiple threads by running known multithreaded code.
    
    Parameters
    ----------
    n : integer
        Size of one side of nxn test data array.
    
    Returns
    -------
    multi_thread : bool or None
        True if multithreading is detected. None if undetermined.
    
    '''
    
    import psutil
    from threading import Thread, Lock

    a = np.ones((n,)*2)
    lock = Lock()
    def mt_func():
        lock.acquire()
        _ = np.dot(a,a)
        lock.release()

    t = Thread(target=mt_func)
    t.start()
    
    cpu_use = []
    while lock.locked():
        cpu_use.append(psutil.cpu_percent())
        time.sleep(0.005)
    
    multi_thread = True
    try:
        if max(cpu_use) > 90:
            print('-------------------------------------------------------------------')
            print('FPD: It looks like numpy is using multiple threads.')
            print('FPD: Performance might be improved by running with 1 thread.')
            print("FPD: Try setting env variable 'OMP_NUM_THREADS=1' before importing.")
            print('-------------------------------------------------------------------\n')
        else:
            multi_thread = False
    except:
        multi_thread = None
    
    return multi_thread


def _int_factors(n):
    '''
    Return 1D array of factors of integer, n, in ascending order.
    
    '''
    
    nat_nums = np.arange(1, n+1)
    rems = np.remainder(n, nat_nums)
    inds = np.where(rems == 0)
    factors = nat_nums[inds]
    return factors


def _find_nearest_int_factor(n, f):
    '''
    Returns tuple of:
        nearest integer factor of n to f
        factors
    
    '''
    
    factors = _int_factors(n)
    i = np.abs(factors - f).argmin()
    factor = factors[i]
    return factor, factors



#--------------------------------------------------
def rebinA(a, *args, **kwargs):
    '''
    Return array 'a' rebinned to shape provided in args.
    
    Parameters
    ----------
    a : array-like
        Array to be rebinned.
    args : expanded tuple
        New shape.
    dtype : numpy dtype or a string representation thereof.
        For integer input, if specified as a keyword argument, this is used
        instead of the data dtype when determining the returned dtype.
    bitdepth : int
        For integer input, if specified as a keyword argument, the maximum data
        value is calculated using this bitdepth.
        
    Returns
    -------
    b : ndarray
        The rebinned array. If of integer type, the returned data dtype is
        appropriate to suit the maximum possible value. Otherwise, the output
        dtype is determined by the behaviour of np.sum. The dtype can be further
        modified by specifying `dtype` and / or `bitdepth`.
    
    Notes
    -----
    Based on http://scipy-cookbook.readthedocs.io/items/Rebinning.html
    
    

    Examples
    --------
    >>> import fpd.fpd_processing as fpdp
    >>> import numpy as np
    
    >>> a = np.random.rand(6, 4, 2).astype('u2')
    >>> print(a.shape)
    (6, 4, 2)
    
    >>> b = fpdp.rebinA(a, *[i//2 for i in a.shape])
    >>> print(b.shape)
    (3, 2, 1)
    >>> print(b.dtype)
    uint32
    
    >>> b = fpdp.rebinA(a, *[i//2 for i in a.shape], bitdepth=12)
    >>> print(b.dtype)
    uint16
    
    '''
    
    dtype = None
    
    input_dtype = kwargs.pop('dtype', None)
    if input_dtype is not None:
        input_dtype = np.dtype(input_dtype)
    else:
        input_dtype = a.dtype
        
    in_k = input_dtype.kind
    input_is_int = in_k in 'ui'
    
    if input_is_int:
        # multiple
        m = np.prod([o // n  for (o, n) in zip(a.shape, args)])
    
        signed = in_k == 'i'
        prefix = ''
        if not signed:
            prefix += 'u'
        
        bitdepth = kwargs.pop('bitdepth', None)
        if bitdepth is None:
            in_pix_max = np.iinfo(input_dtype).max
        else:
            in_pix_max = 2**(bitdepth-1*signed)-1
        out_pix_max = m * in_pix_max
        
        maxes = np.array([np.iinfo(prefix+'int%d' %(d)).max for d in 8*2**np.array([0, 1, 2, 3])])
        inds = np.where(maxes > out_pix_max)[0]
        if len(inds) != 0:
            dtype = "'" + prefix + 'int%d' %(8*2**inds[0]) + "'"

    shape = a.shape
    lenShape = len(shape)
    factor = (np.asarray(shape)/np.asarray(args)).astype(int)
    evList = ["a.reshape("] + \
             ["args[%d],factor[%d]," %(i, i) for i in range(lenShape)] + \
             [")"] + [".sum(%d, dtype=%s)" %(i+1, dtype) for i in range(lenShape)]
    #print(''.join(evList))
    return eval(''.join(evList))


#--------------------------------------------------
def _block_indices(dshape, nrnc):  
    '''
    Generate list of indices of blocks of data of shape dshape of size nrnc.
    
    Parameters
    ----------
    dshape : tuple
        Shape of data array.
    nrnc : tuple, None
        Chunk length in each axis.
        If any entry is None, indices will be for all data.
        
    Returns
    -------
    List of lists by which chunks of array may be indixed.
    
    Examples
    --------
    >>> import fpd.fpd_processing as fpdp
    >>> fpdp._block_indices(dshape=(5,8), nrnc=(None,)*2)
    [[(0, 5)], [(0, 8)]]

    >>> r_if, c_if = fpdp._block_indices(dshape=(5,8), nrnc=(3,)*2)
    >>> print(r_if, c_if)
    [(0, 3), (3, 5)] [(0, 3), (3, 6), (6, 8)]
    
    >>> for i,(ri, rf) in enumerate(r_if):
    ...     for j,(ci, cf) in enumerate(c_if):
    ...         print('\tScan [row,col] chunk [%d, %d] of [%d, %d] - %05.1f%%' %(i+1, j+1, len(r_if), len(c_if), (j+1+i*len(c_if))*100.0/(len(c_if)*len(r_if))), end='\r')
    >>>
    >>>     # data_out[ri:rf,ci:cf] = f(data[ri:rf,ci:cf])

    '''
    
    assert len(dshape) >= len(nrnc)
    
    inds = [list(range(x)) for x in dshape[:len(nrnc)]]
    ns = [n if n is not None else dshape[i] for (i, n) in enumerate(nrnc)]
    rc_ifs = [list(zip([0]+inds[i][n::n],
                  inds[i][n::n]+[inds[i][-1]+1])) for i, n in enumerate(ns)]
    return rc_ifs


#--------------------------------------------------
def sum_im(data, nr, nc, mask=None, nrnc_are_chunks=False):
    '''
    Return a real-space sum image from data. 
    
    Parameters
    ----------
    data : array_like
        Mutidimensional fpd data of shape (scanY, scanX, ..., detY, detX).
    nr : integer or None
        Number of rows to process at once (see Notes).
    nc : integer or None
        Number of columns to process at once (see Notes).
    mask : 2-D array or None
        Mask is applied to data before taking sum.
        Shape should be that of the detector.
    nrnc_are_chunks : bool
        If True, `nr` and `nc` are interpreted as the number of chunks to
        process at once. If `data` is not chunked, `nr` and `nc` are used
        directly.
        
    Returns
    -------
    Array of shape (scanY, scanX, ...).
    
    Notes
    -----
    If `nr` or `nc` are None, the entire dimension is processed at once.
    For chunked data, setting `nrnc_are_chunks` to True, and `nr` and `nc`
    to a suitable values can improve performance.
    
    
    '''
    
    if nrnc_are_chunks:
        nr, nc = _condition_nrnc_if_chunked(data, nr, nc, True)
    
    nondet = data.shape[:-2]
    nonscan = data.shape[2:]
    scanY, scanX = data.shape[:2]
    detY, detX = data.shape[-2:]
    
    r_if, c_if = _block_indices((scanY, scanX), (nr, nc))
    if mask is not None:
        for i in range(len(nondet)): 
            mask = np.expand_dims(mask, 0)
            # == mask = mask[None,None,None,...]
       
    sum_im = np.empty(nondet)
    print('Calculating real-space sum images.')
    total_ims = np.prod(nondet)
    with tqdm(total=total_ims, mininterval=0, leave=True, unit='images') as pbar:
        for i, (ri, rf) in enumerate(r_if):
            for j, (ci, cf) in enumerate(c_if):                
                if mask is None:
                    d = data[ri:rf, ci:cf, ...]
                else:
                    d = (data[ri:rf, ci:cf, ...]*mask)
                sum_im[ri:rf, ci:cf, ...] = d.sum((-2, -1))
                pbar.update(np.prod(d.shape[:-2]))
    print('\n')
    return sum_im


#--------------------------------------------------
def sum_dif(data, nr, nc, mask=None, nrnc_are_chunks=False):
    '''
    Return a summed diffraction image from data. 
    
    Parameters
    ----------
    data : array_like
        Mutidimensional fpd data of shape (scanY, scanX, ..., detY, detX).
    nr : integer or None
        Number of rows to process at once (see Notes).
    nc : integer or None
        Number of columns to process at once (see Notes).
    mask : array-like or None
        Mask applied to data before taking sum.
        Shape should be that of the scan.
    nrnc_are_chunks : bool
        If True, `nr` and `nc` are interpreted as the number of chunks to
        process at once. If `data` is not chunked, `nr` and `nc` are used
        directly.
    
    Returns
    -------
    Array of shape (..., detY, detX).
    
    Notes
    -----
    If `nr` or `nc` are None, the entire dimension is processed at once.
    For chunked data, setting `nrnc_are_chunks` to True, and `nr` and `nc`
    to a suitable values can improve performance.
    
    '''
    
    if nrnc_are_chunks:
        nr, nc = _condition_nrnc_if_chunked(data, nr, nc, True)
    
    nondet = data.shape[:-2]
    nonscan = data.shape[2:]
    scanY, scanX = data.shape[:2]
    detY, detX = data.shape[-2:]
    
    r_if, c_if = _block_indices((scanY, scanX), (nr, nc))
    if mask is not None:
        for i in range(len(nonscan)): 
            mask = np.expand_dims(mask, -1)
            # == mask = mask[..., None,None,None]
            
    sum_dif = np.zeros(nonscan)
    print('Calculating diffraction sum images.')
    total_ims = np.prod(nondet)
    with tqdm(total=total_ims, mininterval=0, leave=True, unit='images') as pbar:
        for i, (ri, rf) in enumerate(r_if):
            for j, (ci, cf) in enumerate(c_if):           
                d = data[ri:rf, ci:cf, ...]
                d = np.ascontiguousarray(d)
                if mask is not None:
                    d = d*mask
                sum_dif += d.sum((0, 1))
                pbar.update(np.prod(d.shape[:-2]))
    print('\n')
    return sum_dif


#--------------------------------------------------
def synthetic_aperture(shape, cyx, rio, sigma=1, dt=np.float, aaf=3, norm=True):
    '''
    Create circular synthetic apertures. Sub-pixel accurate with aaf>1.
    
    Parameters
    ----------
    shape : length 2 iterable
        Image data shape (y,x).
    cyx : length 2 iterable
        Centre y, x pixel cooridinates
    rio : 2d array or length n itterable
        Inner and outer radii [ri,ro) in a number of forms.
        If a length n itterable and not 2d array, n-1 apertures are returned.
        If a 2d array of shape nx2, rio are taken from rows.
    sigma : scalar
        Stdev of Gaussian filter applied to aperture.
    dt : datatype
        Numpy datatype of returned array. If integer type, data is scaled.
    aaf : integer
        Anti-aliasing factor. Use 1 for none.
    norm : bool
        Controls normalisation of actual to ideal area. 
        For apertures extending beyond the image border, the value is 
        increase to give the same 'volume'.
    
    Returns
    -------
    Array of shape (n_ap, y, x).
    
    Notes
    -----
    Some operations may be more efficient if dt is of the same type as 
    the data to which it will be applied.
    
    Examples
    --------
    >>> import fpd.fpd_processing as fpdp
    >>> import matplotlib.pyplot as plt
    >>> plt.ion()
    
    >>> aps = fpdp.synthetic_aperture((256,)*2, (128,)*2, np.linspace(32, 192, 10))
    >>> _ = plt.matshow(aps[0])
    
    '''
    
    assert type(aaf) == int
    
    if type(rio) == np.ndarray and rio.ndim == 2:
        n = rio.shape[0]
    else:
        n = len(rio)-1
        rio = list(zip(rio[:-1], rio[1:]))
    
    m = np.ones((n,)+shape, dtype=dt)
    
    # prepare boolean edge selection
    yi, xi = np.indices(shape)
    ri = ((xi-cyx[1])**2 + (yi-cyx[0])**2)**0.5
    yb = np.logical_or(yi == 0, yi == shape[0]-1)
    xb = np.logical_or(xi == 0, xi == shape[1]-1)
    bm = np.logical_or(xb, yb)    
    ri_edge = ri[bm]
    ri_min = ri_edge.min()
    
    cy, cx = [t*aaf for t in cyx]
    shape = tuple([t*aaf for t in shape])
    y, x = np.indices(shape)
    sigma *= aaf
    
    for i, rio in enumerate(rio):
        ri, ro = [t*aaf for t in rio]
        r = np.sqrt((x - cx)**2 + (y - cy)**2)
        mi = np.logical_and(r >= ri, r < ro)
        mi = gaussian_filter(mi.astype(np.float),
                             sigma, 
                             order=0,
                             mode='reflect')
        
        if np.issubdtype(dt, float):
            mi = mi.astype(dt)
        elif np.issubdtype(dt, 'uint'):
            mi = (mi/mi.max()*np.iinfo(dt).max).astype(dt)
        else:
            print("WARNING: dtype '%s' not supported!" %(dt))
            mi = np.ones(shape)*np.nan
        if aaf != 1:
            mi = sp.ndimage.interpolation.zoom(mi, 
                                               1.0/aaf, 
                                               output=None,
                                               order=1,
                                               mode='constant',
                                               cval=0.0,
                                               prefilter=True)
        # clip any values outside range coming from interpolation
        mi = mi.clip(0, 1)
        if norm:
            mi *= (np.pi*(ro**2-ri**2)/aaf**2)/mi.sum()     # normalisation
        elif rio[1] > ri_min:
            #warnings.simplefilter('always', UserWarning)
            #warnings.warn(('Apperture may extend beyond image.'
            #               +' Consider setting norm to False.')
            #               , UserWarning) 
            #warnings.filters.pop(0)
            print("WARNING: Aperture extends beyond image (max r = %0.1f). Consider setting norm to True. 'rio':" %(ri_min), rio)
        m[i, :, :] = mi
    return m


#--------------------------------------------------
def synthetic_images(data, nr, nc, apertures, rebin=None, nrnc_are_chunks=False):
    '''
    Make synthetic images from data and aperture.
    
    Parameters
    ----------
    data : array_like
        Multidimensional fpd data of shape (scanY, scanX, ..., detY, detX).
    nr : integer or None
        Number of rows to process at once (see Notes).
    nc : integer or None
        Number of columns to process at once (see Notes).
    apertures : array-like
        Mask applied to data before taking sum.
        Shape should 3-D (apN, detY, detX).
    rebin : integer or None
        Rebinning factor for detector dimensions. None or 1 for none. 
        If the value is incompatible with the cropped array shape, the
        nearest compatible value will be used instead.        
    nrnc_are_chunks : bool
        If True, `nr` and `nc` are interpreted as the number of chunks to
        process at once. If `data` is not chunked, `nr` and `nc` are used
        directly.
    
    Returns
    -------
    Array of shape (apN, scanY, scanX, ...).
    
    Notes
    -----
    If `nr` or `nc` are None, the entire dimension is processed at once.
    For chunked data, setting `nrnc_are_chunks` to True, and `nr` and `nc`
    to a suitable values can improve performance.
        
    '''
    
    if nrnc_are_chunks:
        nr, nc = _condition_nrnc_if_chunked(data, nr, nc, True)
    
    apertures = np.rollaxis(apertures, 0, 3)
    apN = apertures.shape[-1]
    # now Y, X, apN

    nondet = data.shape[:-2]
    nonscan = data.shape[2:]
    scanY, scanX = data.shape[:2]
    detY, detX = data.shape[-2:]
    
    r_if, c_if = _block_indices((scanY, scanX), (nr, nc))
    
    
    # determine limits to index array for efficiency
    aps = apertures.sum(-1)
    rii, rif = np.where(aps.sum(axis=1) != 0)[0][[0, -1]]
    cii, cif = np.where(aps.sum(axis=0) != 0)[0][[0, -1]]
    
    # rebinning
    rebinning = rebin is not None and rebin != 1
    if rebinning:
        # min dim
        min_h = rif - rii +1
        min_w = cif - cii +1
        # spare pixels
        sph = detY - min_h
        spw = detX - min_w
        # on left and top: cii and rii
        
        # possible rebins
        fy, fsy = _find_nearest_int_factor(min_h, rebin)
        fx, fsx = _find_nearest_int_factor(min_w, rebin)
        
        if fy != rebin:
            h_from_rebin = int(np.ceil(min_h / float(rebin)) * rebin)
            if h_from_rebin <= detY:
                # expand crop
                py = h_from_rebin - min_h
                if py <= rii:
                    rii -= py
                else:
                    rif += (py-rii)
                    rii -= py
                fy = rebin
            else:
                # leave crop
                pass
        if fx != rebin:
            w_from_rebin = int(np.ceil(min_w / float(rebin)) * rebin)
            if w_from_rebin <= detX:
                # expand crop
                px = w_from_rebin - min_w
                if px <= cii:
                    cii -= px
                else:
                    cif += (px-cii)
                    cii -= px
                fx = rebin
            else:
                # leave crop
                pass
    cropped_im_shape = (rif+1-rii, cif+1-cii)
    print('Image data cropped to:', cropped_im_shape)
    
    if rebinning:
        rebina = np.array([fy, fx])
        if (rebina != rebin).any():
            print('Requested rebin (%d) changed to nearest value: (%d, %d).' %(rebin, fy, fx))
            print('Possible values are:' (fsy, fsx))
        rebinned_im_shape = tuple([x//rebinf for (x, rebinf) in zip(cropped_im_shape, rebina)])
    
    
    apertures = apertures[rii:rif+1, cii:cif+1]
    if rebinning:
        ns = tuple([int(x/rebinf) for (x, rebinf) in zip(apertures.shape[:2], rebina)]) + apertures.shape[2:] 
        apertures = rebinA(apertures, *ns)    
    
    for i in range(len(nondet)): 
        apertures = np.expand_dims(apertures, 0)
        # == apertures = apertures[None,None,None,...]
    
    sim = np.empty(nondet + (apN,))
    print('Calculating synthetic aperture images.')
    total_ims = np.prod(nondet)
    with tqdm(total=total_ims, mininterval=0, leave=True, unit='images') as pbar:
        for i, (ri, rf) in enumerate(r_if):
            for j, (ci, cf) in enumerate(c_if):
                d = data[ri:rf, ci:cf, ..., rii:rif+1, cii:cif+1]
                d = np.ascontiguousarray(d)
                if rebinning:
                    ns = d.shape[:-2] + tuple([int(x/rebinf) for (x, rebinf) in zip(d.shape[-2:], rebina)])
                    d = rebinA(d, *ns)
                d = d[..., None]
                sim[ri:rf, ci:cf] = (d*apertures).sum((-3, -2))
                pbar.update(np.prod(d.shape[:-3]))
    print('\n')
    return np.rollaxis(sim, -1, 0)



#--------------------------------------------------
def find_circ_centre(im, sigma, rmms, mask=None, plot=True, spf=1, low_threshold=0.1,
                     high_threshold=0.95, pct=None, max_n=1):
    '''
    Find centre and radius of circle in image. Sub-pixel accurate with spf>1.
    
    Parameters
    ----------
    im : 2-D array
        Image data.
    sigma : scalar
        Smoothing width for canny edge detection .
    rmms : length 3 iterable
        Radius (min, max, step) in pixels.
    mask : array-like or None
        Mask for canny edge detection. False values are ignored.
        If None, no mask is applied.
    plot : bool
        Determines if best matching circle is plotted in matplotlib.
    spf : integer
        Sub-pixel factor. 1 for none. 
        If not None, step is forced to 1 and corresponds to 1/spf pixels.
    low_threshold : float
        Lower bound for hysteresis thresholding (linking edges) in [0, 1].
    high_threshold : float
        Upper bound for hysteresis thresholding (linking edges) in [0, 1].
    pct : None or scalar
        If not None, values in the image below this percentile are masked.
    max_n : int
        Maximum number of discs to find.
    
    Returns
    -------
    Tuple of arrays of (center_y, center_x), radius.
    
    Notes
    -----
    Image is first scaled to full range of dtype, then upscaled if chosen.
    Canny edge detection is performed, followed by a Hough transform.
    Linking of edges is set by thresholds. See skimage.feature.canny for
    details. The best matching circle or circles are returned depending
    on the value of `max_n`.
    
    When multiple discs are present, increasing `high_threshold` reduces the
    number of edges considered  to those which higher connectivity. For bright
    field discs in STEM, values around 0.99 often work well.
    
    Examples
    --------
    Two calls can be made to make subpixel calculations efficient by 
    reducing the range over which the Hough transform takes place.
    
    >>> import fpd.fpd_processing as fpdp
    >>> from fpd.synthetic_data import disk_image
    
    >>> im = disk_image(intensity=64, radius=32)
    >>> rmms = (10, 100, 2)
    >>> spf = 1
    >>> sigma = 2
    >>> cyx, r = fpdp.find_circ_centre(im, sigma, rmms, mask=None, plot=True, spf=spf)
    
    >>> rmms = (r-4, r+4, 1)
    >>> spf = 4
    >>> cyx, r = fpdp.find_circ_centre(im, sigma, rmms, mask=None, plot=True, spf=spf)
    
    '''
    
    #TODO
    #decision on best centre, improved?
    #subpixel by 2-d gaussian fitting to hough space?
    
    ## scale im so default thresholding works appropriately (% of range)
    #im = (im.astype(np.float)/im.max()*np.iinfo(im.dtype).max)
    #im = im.astype(im.dtype)
    im = im.astype(float)
    
    if pct is not None:
        pct = np.percentile(im, pct)
        pct_mask = (im > pct).astype(bool)
        
        if mask is None:
            mask = pct_mask
        else:
            mask = np.logical_and(pct_mask, mask)
    
    if spf > 1:
        spf = float(spf)
        im = sp.ndimage.interpolation.zoom(im,
                                           spf,
                                           output=None,
                                           order=1,
                                           mode='reflect',
                                           prefilter=True)
        if mask is not None:
            mask = sp.ndimage.interpolation.zoom(mask*1.0,
                                                 spf,
                                                 output=None,
                                                 order=1,
                                                 mode='reflect',
                                                 prefilter=True)
            mask = mask > 0.5
        rmms = [x*spf for x in rmms[:2]] + [1]
    
    if plot:
        kwd = dict(adjustable='box-forced', aspect='equal')
        
        import matplotlib as mpl
        mplv = mpl.__version__
        from distutils.version import LooseVersion
        if LooseVersion(mplv) >= LooseVersion('2.2.0'):
           _ = kwd.pop('adjustable') 
        
        f, (ax1, ax2, ax3) = plt.subplots(1, 3, sharex=True, sharey=True,
                                          subplot_kw=kwd, figsize=(8,3))
        # plot image
        ax1.imshow(im, interpolation='nearest', cmap='gray')#,
                    #norm=mpl.colors.LogNorm())
        ax1.set_title('Image')

    edges = canny(im, sigma, mask=mask, use_quantiles=True,
                  low_threshold=low_threshold,
                  high_threshold=high_threshold)
    if plot:
        ax2.imshow(edges, interpolation='nearest', cmap='gray')
        ax2.set_title('Edges')


    # hough transform
    hough_radii = np.arange(rmms[0], rmms[1], rmms[2])
    hough_res = hough_circle(edges, hough_radii)

    centers = []
    accums = []
    radii = []
    for radius, h in zip(hough_radii, hough_res):
        peaks = peak_local_max(h, num_peaks=max_n)
        centers.extend(peaks)
        accums.extend(h[peaks[:, 0], peaks[:, 1]])
        radii.extend([radius] * len(peaks))
    centers = np.array(centers)
    radii = np.array(radii)
    
    accum_order = np.argsort(accums)[::-1]
    idx = accum_order[:max_n]
    
    center_y, center_x = centers[idx].T
    radius = radii[idx].astype(int)
    
    if plot:
        # Draw the most prominent max_n circles
        imc = color.gray2rgb(im/im.max())
        for cyi, cxi, ri in zip(center_y, center_x, radius):
            cy, cx = circle_perimeter(cyi, cxi, ri)
            imc[cy, cx] = (1, 0, 0)
            imc[cyi, cxi] = (0, 1, 0)
        ax3.imshow(imc, interpolation='nearest')
        ax3.set_title('Detected Circle(s)')
        plt.draw()
    
    if spf > 1:
        center_y, center_x, radius = center_y/spf, center_x/spf, radius/spf
    
    return np.squeeze(np.array((center_y, center_x))).T, np.squeeze(radius)


#--------------------------------------------------
def radial_average(data, cyx, mask=None, r_nm_pp=None, plot=False, spf=1.0):
    '''
    Returns the radial average of one or multiple images.
    Sub-pixel accurate with spf>1.
    
    Parameters
    ----------
    data : ndarray
        Image data of shape (...,y,x).
    cyx : length 2 tuple
        Centre y, x pixel cooridinates.
    mask : None or ndarray
        If not None, True values are retained.
    r_nm_pp : scalar or None
        Value for reciprocal nm per pixel.
        If None, values are in pixels.
    spf : scalar
        Sub-pixel factor for upscaling to give sub-pixel calculations. 
        If 1, pixel level calculations.
        
    Returns
    -------
    r_pix, rms : tuple of ndarrays
        radii, mean intensity. The output dimentionality reflects the input one.
    
    Notes
    -----
    If `r_nm_pp` is not None, radii is in 1/nm, otherwise in pixels.
    This is convenient when analysing diffraction data.
    
    `r_pix` starts at zero.

    
    Examples
    --------
    >>> import numpy as np
    >>> import fpd.fpd_processing as fpdp
    
    >>> cyx = (128,)*2
    >>> im_shape = (256,)*2
    >>> y, x = np.indices(im_shape)
    >>> r = np.sqrt((y - cyx[0])**2 + (x - cyx[1])**2)
    >>> data = np.dstack((r**0.5, r, r**2))
    >>> data = np.rollaxis(data, 2, 0)

    >>> r_pix, radial_mean = fpdp.radial_average(data, cyx, plot=True, spf=2)
    
    '''
    
    if r_nm_pp is None:
        r_nm_pp = 1.0
        xlab = 'Pixel'
    else:
        xlab = '1/nm'
    
    multi_ims = True
    if len(data.shape) == 2:
        # single image, reshaped to 1 x Y x X
        data = data[None, ...]
        nr = 1
        nc = 1
        nonim_shape = (1,)
        multi_ims = False
    else:
        # fpd data with images in last 2 dims
        nonim_shape = data.shape[:-2]
    
    if spf>1:
        spf = float(spf)
        r_nm_pp /= spf
        cyx = [x*spf for x in cyx]
        data = sp.ndimage.interpolation.zoom(data, 
                                             (1,)*len(nonim_shape)+(spf,)*2, 
                                             output=None, 
                                             order=3, 
                                             mode='reflect', 
                                             prefilter=True)
    im_shape = data.shape[-2:]
    y, x = np.indices(im_shape)
    r = np.sqrt((y - cyx[0])**2 + (x - cyx[1])**2)
    r = r.astype(np.int)     # need int for bincounting

    if mask is not None:
        if spf > 1:
            mask = sp.ndimage.interpolation.zoom(mask, 
                                                 spf, 
                                                 output=None,
                                                 order=0,
                                                 mode='reflect',
                                                 prefilter=True)
        r = r[mask]

    for i in range(np.prod(nonim_shape)):
        nd_indx = np.unravel_index(i, nonim_shape)
        
        di = data[nd_indx]
        if mask is not None:
            di = di[mask]

        with np.errstate(invalid='ignore', divide='ignore'):
            tbin = np.bincount(r.ravel(), di.ravel())
            nr = np.bincount(r.ravel())
            radial_mean = tbin / nr
        if i == 0:
            rms = np.empty(nonim_shape + radial_mean.shape)
        rms[nd_indx] = radial_mean[:]
    r_pix = np.arange(radial_mean.shape[0])*r_nm_pp
    
    if plot:
        f, ax = plt.subplots()
        ax.plot(r_pix, rms.T)
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel(xlab)
        plt.ylabel('Mean Intensity')
        plt.tight_layout()
        plt.draw()
    
    if multi_ims is False:
        rms = rms[0]
    return (r_pix, rms)


def _condition_nrnc_if_chunked(data, nr, nc, print_enabled):
    '''
    Determine if data is chunked and set nr and nc as multiples if True.
    
    '''
    if nr is None or nc is None:
        return None, None
    
    isdask = str(type(data)) == "<class 'dask.array.core.Array'>"
    if isdask:
        if print_enabled:
            print('Dask chunk comprehension is not implemented. Leaving (nr, nc) as:', (nr, nc))
            print('Performance may improve with larger nr and nc.')
        return nr, nc
        
    try:
        scan_chunks = data.chunks[:2]
        nr, nc = [x*y for x,y in zip(scan_chunks, (nr, nc))]
        if print_enabled:
            print('Data is chunked, setting (nr, nc) to:', (nr, nc))
            if scan_chunks[0]==1 or scan_chunks[1]==1:
                print('One or more scan chunks are 1, performance may improve with larger nr and nc.')
    except AttributeError:
        # not chunked data
        if print_enabled:
            print('Data is not chunked, leaving (nr, nc) as:', (nr, nc))
            print('Performance may improve with larger nr and nc.')
    return nr, nc


class DummyFile(object):
    def flush(self): pass
    def write(self, x): pass


def _comf(d, use_ap, aperture, yi0, xi0, thr):
    '''
    CoM process data function that operates on single image at a time.
    
    See 'center_of_mass' for 'thr' and 'aperture' documentation.
    
    d is 2-D image.
    use_ap is boolean determining is aperture is used.
    yixi is index array, as defined in calling function.
    
    '''
    
    if _p3:
        s_obj = str
    else:
        s_obj = basestring  
    
    if thr is None:
        pass
    elif isinstance(thr, Number):
        d = (d >= thr)
    elif isinstance(thr, s_obj):
        if thr.lower() == 'otsu':
            try:
                thr_val = threshold_otsu(d)
            except TypeError:
                # TypeError: Cannot cast array data from dtype('uint64') to dtype('int64') according to the rule 'safe'
                thr_val = threshold_otsu(d.astype(float))
            d = (d >= thr_val)
        else:
            # string not understood
            pass
    elif callable(thr):
        # function
        d = thr(d)
        
    if use_ap:
        d = d*aperture
    
    ds = d.sum().astype(float) # sum_im
    comi = np.array([(d * yi0[:, None]).sum(), (d * xi0[None, :]).sum()])/ds
    
    return comi


#--------------------------------------------------
def center_of_mass(data, nr, nc, aperture=None, pre_func=None, thr=None,
                   rebin=None, parallel=True, ncores=None, print_stats=True,
                   nrnc_are_chunks=False, origin='top'):
    '''
    Calculate a centre of mass image from fpd data. The results are
    naturally sub-pixel resolution.
    
    Parameters
    ----------
    data : array_like
        Mutidimensional data of shape (scanY, scanX, ..., detY, detX).
    nr : integer or None
        Number of rows to process at once (see Notes).
    nc : integer or None
        Number of columns to process at once (see Notes).
    aperture : array_like
        Mask of shape (detY, detX), applied to diffraction data after
        `pre_func` processing. Note, the data is automatically cropped
        according to the mask for efficiency.
    pre_func : callable
        Function that operates (out-of-place) on data before processing.
        out = pre_func(in), where in is nd_array of shape (n, detY, detX).
    thr : object
        Control thresholding of difraction image.
        If None, no thresholding.
        If scalar, threshold value.
        If string, 'otsu' for otsu thresholding.
        If callable, function(2-D array) returns thresholded image.
    rebin : integer or None
        Rebinning factor for detector dimensions. None or 1 for none. 
        If the value is incompatible with the cropped array shape, the
        nearest compatible value will be used instead. 
    parallel : bool
        If True, calculations are multiprocessed.
    ncores : None or int
        Number of cores to use for mutliprocessing. If None, all cores
        are used.
    print_stats : bool
        If True, statistics on the analysis are printed.
    nrnc_are_chunks : bool
        If True, `nr` and `nc` are interpreted as the number of chunks to
        process at once. If `data` is not chunked, `nr` and `nc` are used
        directly.
    origin : str
        Controls y-origin of returned data. If origin='top', pythonic indexing 
        is used. If origin='bottom', increasing y is up.
    
    Returns
    -------
    Array of shape (yx, scanY, scanX, ...).
    Increasing Y, X CoM is disc shift up, right in image.
    
    Notes
    -----
    The order of operations is rebinning, pre_func, threshold, aperture,
    and CoM.
    
    If `nr` or `nc` are None, the entire dimension is processed at once.
    For chunked data, setting `nrnc_are_chunks` to True, and `nr` and `nc`
    to a suitable values can improve performance.
    
    The execution of pre_func is not multiprocessed, so it could employ 
    multiprocessing for cpu intensive calculations.
    
    Multiprocessing runs at a similar speed as non parallel code
    in the simplest case.
    
    Examples
    --------
    Using an aperture and rebinning:
    
    >>> import numpy as np
    >>> import fpd.fpd_processing as fpdp
    >>> from fpd.synthetic_data import disk_image, fpd_data_view
    
    >>> radius = 32
    >>> im = disk_image(intensity=1e3, radius=radius, size=256, upscale=8, dtype='u4')
    >>> data = fpd_data_view(im, (32,)*2, colours=0)
    >>> ap = fpdp.synthetic_aperture(data.shape[-2:], cyx=(128,)*2, rio=(0, 48), sigma=0, aaf=1)[0]
    >>> com_y, com_x = fpdp.center_of_mass(data, nr=9, nc=9, rebin=3, aperture=ap)
    
    
    '''
    
    # Possible alternative was not as fast in tests:
    # from scipy.ndimage.measurements import center_of_mass
    
    if nrnc_are_chunks:
        nr, nc = _condition_nrnc_if_chunked(data, nr, nc, print_stats)
        
    if ncores is None:
        ncores = mp.cpu_count()
    
    nondet = data.shape[:-2]
    nonscan = data.shape[2:]
    scanY, scanX = data.shape[:2]
    detY, detX = data.shape[-2:]
    
    use_ap = False
    if isinstance(aperture, np.ndarray):
        # determine limits to index array for efficiency
        rii, rif = np.where(aperture.sum(axis=1) > 0)[0][[0, -1]]
        cii, cif = np.where(aperture.sum(axis=0) > 0)[0][[0, -1]]
        use_ap = True
    else:
        rii, rif = 0, detY-1
        cii, cif = 0, detX-1
    data_square_len = rif-rii+1
    
    # TODO: the following is very similar to _parse_crop_rebin, except it operates
    # only on rii etc These could be refactored and combined to simplify.
    # rebinning
    rebinf = 1
    rebinning = rebin is not None and rebin != 1
    if rebinning:
        # change crop
        extra_pixels = int(np.ceil(data_square_len/float(rebin))*rebin) - data_square_len
        ext_pix_pads = extra_pixels // 2
        
        # this is where the decision on if extra pixels can be added and where 
        # they should go could be made
        if extra_pixels % 2:
            # odd
            ext_pix_pads = (-ext_pix_pads, ext_pix_pads+1)
        else:
            # even
            ext_pix_pads = (-ext_pix_pads, ext_pix_pads)
        riic, rifc = rii + ext_pix_pads[0], rif + ext_pix_pads[1]
        ciic, cifc = cii + ext_pix_pads[0], cif + ext_pix_pads[1]
        if riic < 0 or rifc > detY-1 or ciic < 0 or cifc > detX-1:
            # change rebin
            f, fs = _find_nearest_int_factor(data_square_len, rebin)
            if rebin != f:
                if print_stats:
                    print('Image data cropped to:', cropped_im_shape)
                    print('Requested rebin (%d) changed to nearest value: %d. Possible values are:' %(rebin, f), fs)
                rebin = f
        else:
            rii, rif = riic, rifc
            cii, cif = ciic, cifc
            cropped_im_shape = (rif+1-rii, cif+1-cii)
            if print_stats:
                print('Image data cropped to:', cropped_im_shape)
        rebinf = rebin
    
    if use_ap:
        aperture = aperture[rii:rif+1, cii:cif+1].astype(np.float)
        if rebinning:
            ns = tuple([int(x/rebin) for x in aperture.shape])
            aperture = rebinA(aperture, *ns)
    

    r_if, c_if = _block_indices((scanY, scanX), (nr, nc))
    com_im = np.zeros(nondet + (2,), dtype=np.float)
    yi, xi = np.indices((detY, detX))
    yi = yi[::-1, ...]   # reverse order so increasing Y is up.
    
    yixi = np.concatenate((yi[..., None], xi[..., None]), 2)
    yixi = yixi[rii:rif+1, cii:cif+1, :].astype(np.float)
    if rebinning:
        ns = tuple([int(x/rebin) for x in yixi.shape[:2]]) + yixi.shape[2:]
        yixi = rebinA(yixi, *ns)
    yi0 = yixi[:, 0, 0]
    xi0 = yixi[0, :, 1]
    
    if print_stats:
        print('Calculating centre-of-mass')
        tqdm_file = sys.stderr
    else:
        tqdm_file = DummyFile()
    total_nims = np.prod(nondet)
    with tqdm(total=total_nims, file=tqdm_file, mininterval=0, leave=True, unit='images') as pbar:
        for i, (ri, rf) in enumerate(r_if):
            for j, (ci, cf) in enumerate(c_if):               
                d = data[ri:rf, ci:cf, ..., rii:rif+1, cii:cif+1]#.astype(np.float)
                d = np.ascontiguousarray(d)
                if rebinning:
                    ns = d.shape[:-2] + tuple([int(x/rebin) for x in d.shape[-2:]])
                    d = rebinA(d, *ns)
                
                # modify with function
                if pre_func is not None:
                    d = pre_func(d)
                
                partial_comf = partial(_comf, 
                                    use_ap=use_ap, 
                                    aperture=aperture, 
                                    yi0=yi0,
                                    xi0=xi0, 
                                    thr=thr)
                
                d_shape = d.shape   # scanY, scanX, ..., detY, detX
                d.shape = (np.prod(d_shape[:-2]),) + d_shape[-2:]   
                # (scanY, scanX, ...), detY, detX
                
                if parallel:
                    pool = mp.Pool(processes=ncores)
                    rslt = pool.map(partial_comf, d)
                    pool.close()
                else:
                    rslt = list(map(partial_comf, d))
                rslt = np.asarray(rslt)
                
                #print(d_shape, com_im[ri:rf,ci:cf,...].shape, rslt.shape)
                rslt.shape = d_shape[:-2]+(2,)
                com_im[ri:rf, ci:cf, ...] = rslt
                pbar.update(np.prod(d.shape[:-2]))
    if print_stats:
        print('\n')
    com_im = (com_im)/rebinf**2 
    
    # roll: (scanY, scanX, ..., yx) to (yx, scanY, scanX, ...) 
    com_im = np.rollaxis(com_im, -1, 0)
    
    # default origin implementation is bottom
    if origin.lower() == 'top':
        com_im[0] = nonscan[0]-1 - com_im[0]
    
    # print some stats
    if print_stats:
        _print_shift_stats(com_im)
    
    return com_im


#--------------------------------------------------
def _g2d_der(sigma, truncate=4.0):
    '''
    Returns tuple (gy, gy) of first partial derivitives of Gaussian.
    Y increasing is up.
    
    '''
    
    d = int(np.ceil(sigma*truncate))
    dtot = 2*d+1
    y, x = np.indices((dtot,)*2)-d
    
    gx = -x/(2*np.pi*sigma**4)*np.exp(-(x**2+y**2)/(2*sigma**2))
    gy = -np.rollaxis(gx, 1, 0) # -ve to have y increasin upward
    #plt.matshow(gx)
    #plt.matshow(gy)
    
    return (gy, gx)


#--------------------------------------------------
def _grad(im, gxy, mode):
    '''
    Calculate gradient by colvolving 'im' with 'gxy'.
    'mode' is passed to fftconvolve.
    
    '''
    img = np.abs(fftconvolve(im, gxy, mode))
    return img



def _process_grad(d, pre_func, mode, sigma, truncate, gxy, 
                  parallel, ncores, der_clip_fraction, der_clip_max_pct,
                  post_func):
    ''' Calculate gradients. '''
    
    if pre_func is not None:
        d = pre_func(d)
    
    if mode == '1d':
        # ok for small sigma, poor at diagonals at high sigma 
        df = d.astype(float)
        gy = gaussian_filter1d(df, sigma=sigma, axis=-2, order=1,
                            mode='reflect', truncate=truncate)
        gx = gaussian_filter1d(df, sigma=sigma, axis=-1, order=1, 
                            mode='reflect', truncate=truncate)
        gm = (gy**2+gx**2)**0.5
    elif mode == '2d':        
        partial_grad = partial(_grad, gxy=gxy, mode='same')
        d_shape = d.shape
        d.shape = (np.prod(d_shape[:-2]),)+d_shape[-2:]
        
        if parallel:
            pool = mp.Pool(processes=ncores)
            rslt = pool.map(partial_grad, d)
            pool.close()
        else:
            rslt = list(map(partial_grad, d))
        gm = np.asarray(rslt)
    else:
        raise ValueError('Mode value unknown.')
    
    if der_clip_fraction != 0:
        ref = np.percentile(gm, der_clip_max_pct, axis=(-2, -1))
        clip_low = der_clip_fraction * ref
        gm[gm<clip_low[:, None, None]] = 0
    
    if post_func is not None:
        gm = post_func(gm)
    
    gm = gm.reshape((-1,) + gm.shape[-2:])
    return gm



#--------------------------------------------------
def phase_correlation(data, nr, nc, cyx=None, crop_r=None, sigma=2.0,
                      spf=100, pre_func=None, post_func=None, mode='2d',
                      ref_im=None, rebin=None, der_clip_fraction=0.0,
                      der_clip_max_pct=99.9, truncate=4.0, parallel=True,
                      ncores=None, print_stats=True, nrnc_are_chunks=False, origin='top'):
    '''
    Perform phase correlation on 4-D data using efficient upscaling to
    achieve sub-pixel resolution.
    
    Parameters
    ----------
    data : array_like
        Mutidimensional data of shape (scanY, scanX, ..., detY, detX).
    nr : integer or None
        Number of rows to process at once (see Notes).
    nc : integer or None
        Number of columns to process at once (see Notes).
    cyx : length 2 iterable or None
        Centre of disk in pixels (cy, cx).
        If None, centre is used.
    crop_r : scalar or None
        Radius of circle about cyx defining square crop limits used for
        cross-corrolation, in pixels.
        If None, the maximum square array about cyx is used.
    sigma : scalar
        Smoothing of Gaussian derivitive.
    spf : integer
        Sub-pixel factor i.e. 1/spf is resolution.
    pre_func : callable
        Function that operates (out-of-place) on data before processing.
        out = pre_func(in), where in is nd_array of shape (n, detY, detX).
    post_func : callable
        Function that operates (out-of-place) on data after derivitive.
        out = post_func(in), where in is nd_array of shape (n, detY, detX).
    mode : string
        Derivative type. 
        If '1d', 1d convolution; faster but not so good for high sigma.
        If '2d', 2d convolution; more accurate but slower.
    ref_im : None or ndarray
        2-D image used as reference. 
        If None, the first probe position is used.
    rebin : integer or None
        Rebinning factor for detector dimensions. None or 1 for none. 
        If the value is incompatible with the cropped array shape, the
        nearest compatible value will be used instead. 
        'cyx' and 'crop_r' are for the original image and need not be modified.
        'sigma' and 'spf' are scaled with rebinning factor, as are output shifts.
    der_clip_fraction : float
        Fraction of `der_clip_max_pct` in derivative images below which will be
        to zero.
    der_clip_max_pct : float
        Percentile of derivative image to serve as reference for `der_clip_fraction`.
    truncate : scalar
        Number of sigma to which Gaussians are calculated.
    parallel : bool
        If True, derivative and correlation calculations are multiprocessed.
        Note, if `mode=1d`, the derivative calculations are not multiprocessed,
        but may be multithreaded if enabled in the numpy linked BLAS lib.
    ncores : None or int
        Number of cores to use for mutliprocessing. If None, all cores
        are used.
    print_stats : bool
        If True, statistics on the analysis are printed.
    nrnc_are_chunks : bool
        If True, `nr` and `nc` are interpreted as the number of chunks to
        process at once. If `data` is not chunked, `nr` and `nc` are used
        directly.
    origin : str
        Controls y-origin of returned data. If origin='top', pythonic indexing 
        is used. If origin='bottom', increasing y is up.
        
    Returns
    -------
    Tuple of (shift_yx, shift_err, shift_difp, ref), where:
    shift_yx : array_like
        Shift array in pixels, of shape ((y,x), scanY, scanX, ...).
        Increasing Y, X is disc shift up, right in image.
    shift_err : 2-D array
        Translation invariant normalized RMS error in correlations.
        See skimage.feature.register_translation for details.
    shift_difp : 2-D array
        Global phase difference between the two images.
        (should be zero if images are non-negative).
        See skimage.feature.register_translation for details.
    ref : 2-D array
        Reference image.
    
    Notes
    -----
    The order of operations is rebinning, pre_func, derivative, 
    post_func, and correlation.
    
    If `nr` or `nc` are None, the entire dimension is processed at once.
    For chunked data, setting `nrnc_are_chunks` to True, and `nr` and `nc`
    to a suitable values can improve performance.
    
    Specifying 'crop_r' (and appropriate cyx) can speed up calculation significantly.
    
    The execution of 'pre_func' and 'post_func' are not multiprocessed, so 
    they could employ multiprocessing for cpu intensive calculations.
    
    Efficient upscaling is based on:
    http://scikit-image.org/docs/stable/auto_examples/transform/plot_register_translation.html
    http://scikit-image.org/docs/stable/api/skimage.feature.html#skimage.feature.register_translation
    
    '''
    
    # der_clip_max_pct=99.9 'ignores' (256**2)*0.001 ~ 65 pixels.
    # (256**2)*0.001 / (2*3.14) / 2 ~ 5. == ignoring of 5 pix radius, 2 pix width torus
    
    if nrnc_are_chunks:
        nr, nc = _condition_nrnc_if_chunked(data, nr, nc, print_stats)
    
    if ncores is None:
        ncores = mp.cpu_count()
    
    nondet = data.shape[:-2]
    nonscan = data.shape[2:]
    scanY, scanX = data.shape[:2]
    detY, detX = data.shape[-2:]
    
    r_if, c_if = _block_indices((scanY, scanX), (nr, nc))
    
    rtn = _parse_crop_rebin(crop_r, detY, detX, cyx, rebin, print_stats)
    cropped_im_shape, rebinf, rebinning, rii, rif, cii, cif = rtn
       
    
    # rebinning
    rebinf = 1
    rebinning = rebin is not None and rebin != 1
    if rebinning:
        f, fs = _find_nearest_int_factor(cropped_im_shape[0], rebin)
        if rebin != f:
            print('Image data cropped to:', cropped_im_shape)
            print('Requested rebin (%d) changed to nearest value: %d. Possible values are:' %(rebin, f), fs)
            rebin = f
        rebinf = rebin
        sigma = float(sigma)/rebinf
        spf = int(float(spf)*rebinf)
    rebinned_im_shape = tuple([x//rebinf for x in cropped_im_shape])
    #print('Cropped shape: ', cropped_im_shape)
    #if rebinning:
        #print('Rebinned cropped shape: ', rebinned_im_shape)
    
    
    # gradient of gaussian
    gy, gx = _g2d_der(sigma, truncate=truncate)
    gxy = gx + 1j*gy
    #gxy = (gx**2 + gy**2)**0.5
    
    
    ### ref im
    if ref_im is None:
        # use first point
        ref_im = data[0, 0, ...]
        for i in range(len(nondet)-2):
            ref_im = ref_im[0]
    else:
        # provided option
        ref_im = ref_im
    
    ref = ref_im[rii:rif+1, cii:cif+1]
    for t in range(len(nondet)): 
        ref = np.expand_dims(ref, 0)    # ref[None, None, None, ...]
    if rebinning:
        ns = ref.shape[:-2] + tuple([int(x/rebin) for x in ref.shape[-2:]])
        ref = rebinA(ref, *ns)
    ref = _process_grad(ref, pre_func, mode, sigma, truncate, gxy,
                        parallel, ncores, der_clip_fraction, der_clip_max_pct,
                        post_func)[0]
    
    
    shift_yx = np.empty(nondet + (2,))
    shift_err = np.empty(nondet)
    shift_difp = np.empty_like(shift_err)
    
    if print_stats:
        print('\nPerforming phase correlation')
        tqdm_file = sys.stderr
    else:
        tqdm_file = DummyFile()
    total_nims = np.prod(nondet)
    with tqdm(total=total_nims, file=tqdm_file, mininterval=0, leave=True, unit='images') as pbar:
        for i, (ri, rf) in enumerate(r_if):
            for j, (ci, cf) in enumerate(c_if):               
                # read selected data (into memory if hdf5)  
                d = data[ri:rf, ci:cf, ..., rii:rif+1, cii:cif+1]
                d = np.ascontiguousarray(d)
                if rebinning:
                    ns = d.shape[:-2] + tuple([int(x/rebinf) for x in d.shape[-2:]])
                    d = rebinA(d, *ns)
                
                # calc grad
                gm = _process_grad(d, pre_func, mode, sigma, truncate, gxy,
                                   parallel, ncores, der_clip_fraction, der_clip_max_pct,
                                   post_func)
                
                # Could combine grad and reg to skip ifft/fft,
                # and calc ref grad fft only once
                # For 1d mode, could try similar combinations, but using 
                # functions across ndarray axes with multithreaded blas.
                
                ## do correlation
                # gm is (n, detY, detX), with last 2 rebinned
                partial_reg = partial(register_translation, ref, upsample_factor=spf)
                
                if parallel:
                    pool = mp.Pool(processes=ncores)
                    rslt = pool.map(partial_reg, gm)
                    pool.close()
                else:
                    rslt = list(map(partial_reg, gm))
                shift, error, phasediff = np.asarray(rslt).T
                shift = np.array(shift.tolist())
                # -ve shift to swap source/ref coords to be consistent with 
                # other phase analyses
                shift *= -1.0
                
                shift_yx[ri:rf, ci:cf].flat = shift
                shift_err[ri:rf, ci:cf].flat = error
                shift_difp[ri:rf, ci:cf].flat = phasediff
                
                pbar.update(np.prod(d.shape[:-2]))
    if print_stats:
        print('')
        sys.stdout.flush()    
    shift_yx = np.rollaxis(shift_yx, -1, 0)
       
    # reverse y for shift up being positive
    flp = np.array([-1, 1])
    for i in range(len(nonscan)):
        flp = np.expand_dims(flp, -1)
    shift_yx = shift_yx*flp
    
    # default origin implementation is bottom
    if origin.lower() == 'top':
        shift_yx[0] = -shift_yx[0]
        
    # scale shifts for rebinning
    if rebinning:
        shift_yx *= rebinf
    
    # print stats
    if print_stats:
        _print_shift_stats(shift_yx)

    return shift_yx, shift_err, shift_difp, ref


def _print_shift_stats(shift_yx):
    ''' Prints statistics of 'shift_yx' array'''
    shift_yx_mag = (shift_yx**2).sum(0)**0.5
    shift_yxm = np.concatenate((shift_yx, shift_yx_mag[None, ...]), axis=0)
    
    non_yx_axes = tuple(range(1, len(shift_yxm.shape)))
    yxm_mn, yxm_std = shift_yxm.mean(non_yx_axes), shift_yxm.std(non_yx_axes)
    yxm_min, yxm_max = shift_yxm.min(non_yx_axes), shift_yxm.max(non_yx_axes)
    yxm_ptp = yxm_max - yxm_min
    
    print('{:10s}{:>8s}{:>11s}{:>11s}'.format('Statistics', 'y', 'x', 'm'))
    print('{:s}'.format('-'*40))
    print('{:6s}: {:10.3f} {:10.3f} {:10.3f}'.format(*(('Mean',)+tuple(yxm_mn))))
    print('{:6s}: {:10.3f} {:10.3f} {:10.3f}'.format(*(('Min',)+tuple(yxm_min))))
    print('{:6s}: {:10.3f} {:10.3f} {:10.3f}'.format(*(('Max',)+tuple(yxm_max))))
    print('{:6s}: {:10.3f} {:10.3f} {:10.3f}'.format(*(('Std',)+tuple(yxm_std))))
    print('{:6s}: {:10.3f} {:10.3f} {:10.3f}'.format(*(('Range',)+tuple(yxm_ptp))))
    print()
    


def disc_edge_sigma(im, sigma=2, cyx=None, r=None, use_hyperspy=False, plot=True):
    '''
    Calculates disc edge width by averaging sigmas from fitting Erfs to unwrapped disc.
    
    Parameters
    ----------
    im : 2-D array
        Image of disc.
    sigma : scalar
        Estimate of edge stdev.
    cyx : length 2 iterable or None
        Centre coordinates of disc. If None, these are calculated.
    r : scalar or None
        Disc radius in pixels. If None, the value is calculated.
    use_hyperspy : bool
        If True, HyperSpy is used for fitting and plotting. If False,
        scipy and matplotlib are used.
    plot : bool
        Determines if images are plotted.
    
    Returns
    -------
    sigma_wt_avg : scalar
        Average sigma value, weighted if possible by fit error.
    sigma_wt_std : scalar
        Average sigma standard deviation, weighted if possible by fit error.
        Nan if no weighting is posible.
    sigma_std : scalar
        Standard deviation of all sigma values.
    (sigma_vals, sigma_stds) : tuple of 1-D arrays
        Sigma values and standard deviations from fit.
    
    Notes
    -----
    `sigma` is used for initial value and for setting range of fit.
    Increasing value widens region fitted to.
    
    Examples
    --------
    >>> import fpd
    >>> import matplotlib.pylab as plt
    >>>
    >>> plt.ion()
    >>>
    >>> im = fpd.synthetic_data.disk_image(intensity=16, radius=32, sigma=5.0, size=256, noise=True)
    >>> cyx, r = fpd.fpd_processing.find_circ_centre(im, 2, (22, int(256/2.0), 1), spf=1, plot=False)
    >>>
    >>> returns = fpd.fpd_processing.disc_edge_sigma(im, sigma=6, cyx=cyx, r=r, plot=True)
    >>> sigma_wt_avg, sigma_wt_std, sigma_std, (sigma_vals, sigma_stds) = returns

    '''
    

    detY, detX = im.shape
    
    if cyx is None or r is None:
        cyx_, r_ = find_circ_centre(im, 2, (3, int(detY/2.0), 1), spf=1, plot=plot)
    if cyx is None:
        cyx = cyx_
    if r is None:
        r = r_
    cy, cx = cyx
    
    # set up coordinated
    yi, xi = np.indices((detY, detX), dtype=float)
    yi-=cy
    xi-=cx
    ri2d = (yi**2+xi**2)**0.5
    ti2d = np.arctan2(yi, xi)

    interp_pix = 0.25   # interpolation resolution
    rr, tt = np.meshgrid(np.arange(0, 2.5*r, interp_pix), 
                         np.arange(-180,180,1*4)/180.0*np.pi, 
                         indexing='ij')
    xx = rr*np.sin(tt)+cx
    yy = rr*np.cos(tt)+cy

    # MAP TO RT  
    rt_val = sp.ndimage.interpolation.map_coordinates(im.astype(float), 
                                                      np.vstack([yy.flatten(), xx.flatten()]) )
    rt_val = rt_val.reshape(rr.shape)

    if plot:
        plt.matshow(rt_val)
        plt.figure()
        plt.plot(rt_val[:,::18])
        plt.xlabel('Interp pixels')
        plt.ylabel('Intensity')
    
    
    # Fit edge
    der = -np.diff(rt_val, axis=0)
    
    # fit range
    ri2d_edge_min = np.concatenate((ri2d[[0, -1], :], ri2d[:, [0, -1]].T), axis=1).min()
    rmin = max( (r-3*sigma), 0 )
    rmax = min( (r+3*sigma), ri2d_edge_min )
    
    if use_hyperspy:
        from hyperspy.signals import EELSSpectrum
        from hyperspy.component import Component
        s = EELSSpectrum(rt_val.T)
        #s.align1D()
        #s.plot()
        
        s_av = s#.sum(0)
        #s_av.plot()
    
        s_av.metadata.set_item("Acquisition_instrument.TEM.Detector.EELS.collection_angle", 1)
        s_av.metadata.set_item("Acquisition_instrument.TEM.beam_energy ", 1)
        s_av.metadata.set_item("Acquisition_instrument.TEM.convergence_angle", 1)
    
        m = s_av.create_model(auto_background=False)
    
        # http://hyperspy.org/hyperspy-doc/v0.8/user_guide/model.html   
        class My_Component(Component):
            """
            """
            def __init__(self, origin=0, A=1, sigma=1):
                # Define the parameters
                Component.__init__(self, ('origin', 'A', 'sigma'))
                #self.name = 'Erf'

                # Optionally we can set the initial values
                self.origin.value = origin
                self.A.value = A
                self.sigma.value = sigma

            # Define the function as a function of the already defined parameters, x
            # being the independent variable value
            def function(self, x):
                p1 = self.origin.value
                p2 = self.A.value
                p3 = self.sigma.value
                #return p1 + x * p2 + p3
                return p2*( sp.special.erf( (x-p1)/(np.sqrt(2)*p3) )+1.0 ) /2.0

        g = My_Component()
        m.append(g)
        
        # set defaults
        sigma = sigma
        m.set_parameters_value('sigma',  sigma/interp_pix, component_list=[g])
        m.set_parameters_value('A', -np.percentile(rt_val, 90), component_list=[g])
        m.set_parameters_value('origin', r/interp_pix, component_list=[g])
        
        # set fit range
        m.set_signal_range(rmin/interp_pix, rmax/interp_pix)
        
        m.multifit()
        if plot:
            m.plot()

        sigma_vals = np.abs(g.sigma.map['values'])*interp_pix
        sigma_stds = np.abs(g.sigma.map['std'])*interp_pix
    else:
        # non-hyperspy
        from scipy.optimize import curve_fit
        
        def function(x, p1, p2, p3):
            #p1, p2, p3 = origin, A, sigma
            return p2*( sp.special.erf( (x-p1)/(np.sqrt(2)*p3) )+1.0 ) /2.0
        
        # fit range
        x = np.arange(len(rt_val))
        xmin, xmax = rmin/interp_pix, rmax/interp_pix
        b = np.logical_and(x >= xmin, x <= xmax) 
        
        p0 = (r/interp_pix, -np.percentile(rt_val, 90), sigma/interp_pix)
        popts = []
        perrs = []
        for rt_vali in rt_val.T:
            yi = rt_vali[b]
            xi = x[b]
            popt, pcov = curve_fit(f=function, xdata=xi, ydata=yi, p0=p0)
            perr = np.sqrt(np.diag(pcov))
            
            popts.append(popt)
            perrs.append(perr)
        popts = np.array(popts)
        perrs = np.array(perrs)
        
        sigma_vals = np.abs(popts[:, 2])*interp_pix
        sigma_stds = np.abs(perrs[:, 2])*interp_pix
        
        if plot:
            A = np.percentile(popts[:, 1], 50)
            fits = np.array([function(x, *pi) for pi in popts])
            
            inds = np.arange(len(sigma_vals))[::10]
            f, ax = plt.subplots(1, 1, figsize=(6, 8))
            pad = 0.2 * A
            for j,i in enumerate(inds):
                ax.plot(x, rt_val[:, i] + pad*j, 'x')
                ax.plot(x[b], fits[i][b] + pad*j, 'b-')
            pass
    
    # calculate averages
    sigma_std = sigma_vals.std()
    
    err_is = np.where(np.isfinite(sigma_stds))[0]
    if err_is.size > 1:
        print('Calculating weighted average...')
        vs = sigma_vals[err_is]
        ws = 1.0/sigma_stds[err_is]**2
        sigma_wt_avg = (vs*ws).sum()/ws.sum()
        sigma_wt_std = (1.0/ws.sum())**0.5
    else:
        print('Calculating unweighted average...')
        sigma_wt_avg = sigma_vals.mean()
        sigma_wt_std = np.nan
    print('Avg: %0.3f +/- %0.3f' %(sigma_wt_avg, sigma_wt_std))
    print('Std: %0.3f' %(sigma_std))
    
    
    sigma_pcts = np.percentile(sigma_vals, [10, 50, 90])
    print('Percentiles (10, 50, 90): %0.3f, %0.3f, %0.3f' %tuple(sigma_pcts))
    
    return(sigma_wt_avg, sigma_wt_std, sigma_std, (sigma_vals, sigma_stds))


def nrmse(ref_im, test_ims):
    '''
    Euclidean normalised mean square error.
    
    Parameters
    ----------
    ref_im : 2-D array
        Reference image.
    test_ims : ndarray
        Images to compare.
    
    '''
    
    im1 = ref_im.astype(float)
    im2 = test_ims.astype(float)
    n = (((im1-im2)**2).mean((-2, -1)) / ((im1**2+im2**2).mean((-2, -1))/2))**0.5
    return n


def find_matching_images(images, aperture=None, avg_nims=3, cut_len=20, plot=True):
    '''
    Finds matching images using euclidean normalised mean square error through
    all combinations of a given number of images.
    
    Parameters
    ----------
    images : ndarray
        Array of images with image axes in last 2 dimensions.
    aperture : 2D array
        An aperture to apply to the images.
    avg_nims : int
        The number of images in a combination.
    cut_len : int
        The number of combinations in which to look for common images.
    
    Returns
    -------
    named tuple 'matching' containing:
    
    yxi_combos : tuple of two 2-D arrays
        y- and x-indices of combinations, sorted by match quality.
    yxi_common :
        y- and x-indices of most common image in ``cut_len`` combinations.
    ims_common : 3-D array
        All images in in ``cut_len`` combinations matched with most common image.
    ims_best : 3-D array
        Best matching ``avg_nims`` images.
    
    Notes
    -----
    The number of combinations increases very rapidly with ``avg_nims`` and
    the number of images. Using around 100 or so images runs relatively quickly.
    
    Examples
    --------
    >>> from fpd.synthetic_data import disk_image, shift_array, shift_images
    >>> import fpd.fpd_processing as fpdp

    Generate synthetic data.
    >>> disc = disk_image(radius=32, intensity=64)
    >>> shift_array = shift_array(6, shift_min=-1, shift_max=1)

    Set shifts on diagonal to zero.
    >>> diag_inds = [np.diag(x) for x in np.indices(shift_array[0].shape)]
    >>> shift_array[0][diag_inds] = 0
    >>> shift_array[1][diag_inds] = 0
    
    Generate shifted images.
    >>> images = shift_images(shift_array, disc, noise=False)
    >>> aperture = fpdp.synthetic_aperture(images.shape[-2:], cyx=(128,)*2, rio=(0, 48), sigma=0, aaf=1)[0]
    
    Find matching images.
    >>> matching = fpdp.find_matching_images(images, aperture, plot=True)
    >>> ims_best = matching.ims_best.mean(0)
    
    '''
    
    # convert dask and other out-of-core to numpy
    ims_orig = np.ascontiguousarray(images)  

    # flatten original images
    ims_orig_shape = ims_orig.shape
    ims_orig.shape = (-1,) + ims_orig.shape[-2:]
    n_ims = ims_orig.shape[0]

    # apply aperture and crop
    if aperture is not None:
        ri, rf = np.where(aperture.sum(0))[0][[0, -1]]
        ci, cf = np.where(aperture.sum(1))[0][[0, -1]]
        sr = slice(ri, rf+1)
        sc = slice(ci, cf+1)
        aperture = aperture[sr, sc]
        ims = ims_orig[:, sr, sc]*(aperture[None, ...].astype(int))
    else:
        ims = ims_orig

    # calculate nrsme for all combinations in one half diagonal
    err = np.ones((n_ims, n_ims), dtype=float)
    err[:] = np.nan
    print('Calculating NRSME for all image combinations')
    for ri, ref_im in enumerate(tqdm(ims)):
        test_ims = ims[:ri]
        err_col = nrmse(ref_im, test_ims)
        err[:ri, ri] = err_col
    if plot:
        f, (ax1, ax2) = plt.subplots(1, 2, sharex=False, sharey=False, figsize=(8,4))
        ax1.imshow(err, interpolation="nearest")
        ax1.set_xlabel('Flattened image index')
        ax1.set_ylabel('Flattened image index')
        ax1.set_title('NRSME')

        '''
        import hyperspy.api as hs
        err_ims = np.reshape(err, (-1,) + ims_orig_shape[:2])
        hs.signals.Signal2D(err_ims).plot()
        '''
    # loop over all combinations
    print('Calculating combined NRSME for all combinations of %d images' %(avg_nims))
    combs_tot = int(np.math.factorial(n_ims)/(np.math.factorial(avg_nims)*np.math.factorial(n_ims-avg_nims)))
    comb_vals = np.empty(combs_tot, dtype=float)
    comb_inds = np.empty((combs_tot, avg_nims), dtype=int)
    for i, inds in enumerate(tqdm(combinations(range(n_ims), avg_nims), total=combs_tot)):
        # calculate rmse from values at intercepts of row and column slices
        ind_perms = np.array(list(combinations(inds, 2))).T
        intercept_vals = err[ind_perms[0], ind_perms[1]]
        comb_vals[i] = np.nansum(intercept_vals**2).sum()**0.5
        comb_inds[i] = inds

    # sort perms by rmse
    si = np.argsort(comb_vals)
    comb_vals = comb_vals[si]
    comb_inds = comb_inds[si]

    if plot:
        # Combined NRSME
        ax2.semilogx(comb_vals)
        ax2.set_xlabel('Combination index')
        ax2.set_ylabel('Combined NRSME')
        ax2.set_title('%d combinations of %d images' %(combs_tot, avg_nims))
        plt.tight_layout()

        # map of scan locations
        gri, gci = np.unravel_index(comb_inds, ims_orig_shape[:2])
        map_im = np.zeros(ims_orig_shape[:2])
        for i in range(cut_len):
            map_im[gri[i], gci[i]] += 1
        f, (ax1, ax2) = plt.subplots(1, 2, sharex=True, sharey=True, figsize=(8,4))
        ax1.imshow(map_im)
        ax1.set_xlabel('Scan X index')
        ax1.set_ylabel('Scan Y index')
        ax1.set_title('First %d combinations of %d images' %(cut_len, avg_nims))

    # find most common scan index within cut
    common_im_ind = np.bincount(comb_inds[:cut_len].flat).argmax()
    print('Most common scan index in 1st %d combinations of %d images:' %(cut_len, avg_nims), np.unravel_index(common_im_ind, ims_orig_shape[:2]))
    contains_common_im = (comb_inds[:cut_len] == common_im_ind).sum(1) > 0

    # unique image indices within cut with most popular image in common
    common_im_inds = np.unique(comb_inds[:cut_len][contains_common_im].flatten())
    print('Number of unique images in these combinations sharing this index: %d' %(len(common_im_inds)))
    if plot:
        # plot unique points
        sel_im = np.zeros(ims_orig_shape[:2])
        sel_im.flat[common_im_inds] = 1
        ax2.imshow(sel_im)
        ax2.set_xlabel('Scan X index')
        #plt.ylabel('Scan Y index')
        plt.title('Unique images in 1st %d combinations of %d images\nsharing most common image' %(cut_len, avg_nims))

    # calculate means and stds with mask if specified 
    if plot:
        f, axs = plt.subplots(3, 2, sharex=True, sharey=True, figsize=(5,8))
        ax1, ax2, ax3, ax4, ax5, ax6 = axs.flatten()
        
        im_common = ims[common_im_inds]
        im_common_mean = im_common.mean(0)
        im_common_std = im_common.std(0)
        ax1.imshow(im_common_mean)
        ax2.imshow(im_common_std)
        ax1.set_title('Most common %d best' %(len(common_im_inds)))
        
        im_best = ims[comb_inds[0]]
        im_best_mean = im_best.mean(0)
        im_best_std = im_best.std(0)
        ax3.imshow(im_best_mean)
        ax4.imshow(im_best_std)
        ax3.set_title('Best combination of %d' %(avg_nims))

        im_worst = ims[comb_inds[-1]]
        im_worst_mean = im_worst.mean(0)
        im_worst_std = im_worst.std(0)
        ax5.imshow(im_worst_mean)
        ax6.imshow(im_worst_std)
        ax5.set_title('Worst combination of %d' %(avg_nims))
    print('')

    # return data (without masks)
    yxi_combos = np.unravel_index(comb_inds, ims_orig_shape[:2])
    yxi_common = np.unravel_index(common_im_inds, ims_orig_shape[:2])

    ims_common = ims_orig[common_im_inds]
    ims_common_mean = ims_common.mean(0)
    ims_common_std = ims_common.std(0)
    
    ims_best = ims_orig[comb_inds[0]]
    ims_best_mean = ims_best.mean(0)
    ims_best_std = ims_best.std(0)
    
    # reshape original, in case ascontiguousarray returns view
    ims_orig.shape = ims_orig_shape
    
    rtn = namedtuple('matching', ['yxi_combos', 'yxi_common', 'ims_common', 'ims_best'])
    return rtn(yxi_combos, yxi_common, ims_common, ims_best)


def make_ref_im(image, edge_sigma, aperture=None, upscale=4, bin_opening=None, bin_closing=None, crop_pad=False, threshold=None, plot=True):
    '''
    Generate a cleaned version of the image supplied for use as a reference.
    
    Parameters
    ----------
    image : 2-D array
        Image to process.
    edge_sigma : float
        Edge width in pixels.
    aperture : None or 2-D array
        If not None, the data will be multiplied by the aperture mask.
    upscale : int
        Upscaling factor.
    bin_opening : None or int
        Circular element radius used for binary opening.
    bin_closing : None or int
        Circular element radius used for binary closing.
    crop_pad : bool
        If True and ``aperture`` is not None, the image is cropped before
        upscaling and padded in returned image for efficiency.
    threshold : scalar or None
        Image threshold. If None, Otsu's method is used. Otherwise, the scalar
        value is used.
    plot : bool
        If True, the images are plotted.
    
    Notes
    -----
    The sequence of operation is:
        apply aperture
        upscale
        threshold
        bin_opening
        bin_closing
        edge_sigma
        downscale
        scale magnitude
    
    Examples
    --------
    >>> from fpd.synthetic_data import disk_image
    >>> import fpd.fpd_processing as fpdp

    Generate synthetic image
    >>> image = disk_image(radius=32, intensity=64)
    
    Get centre and edge, and make aperture
    >>> cyx, cr = fpdp.find_circ_centre(image, sigma=6, rmms=(2, int(image.shape[0]/2.0), 1), plot=False)
    >>> edge_sigma = fpdp.disc_edge_sigma(image, sigma=2, cyx=cyx, r=cr, plot=False)[0]
    >>> aperture = fpdp.synthetic_aperture(image.shape[-2:], cyx=cyx, rio=(0, cr+16), sigma=0, aaf=1)[0]
    
    Make reference image
    >>> ref_im = fpdp.make_ref_im(image, edge_sigma, aperture)
    
    '''
    
    # float
    im = image.astype(float)
    im_shape = image.shape
    
    # mask
    if aperture is not None:
        im = im*aperture
        if crop_pad:
            #crop and pad for efficiency
            ci, cf = np.where((aperture>0.5).sum(0)>0)[0][[0, -1]]
            ri, rf = np.where((aperture>0.5).sum(0)>0)[0][[0, -1]]
            im = im[ri:rf+1, ci:cf+1]
        
    
    # upscale and threshold
    ref_imu = sp.ndimage.interpolation.zoom(im, zoom=4, output=None,
                                            order=3, mode='constant',
                                            cval=0.0, prefilter=True)
    if threshold is None:
        thresh = threshold_otsu(ref_imu)
    else:
        thresh = float(threshold)
    processed = ref_imu >= thresh
    
    # binary opening / closing
    if bin_opening is not None:
        el = disk(bin_opening*upscale)
        processed = binary_opening(processed, el)
    if bin_closing is not None:
        el = disk(bin_closing*upscale)
        processed = binary_closing(processed, el)

    # smooth and downscale
    processed = sp.ndimage.filters.gaussian_filter(processed*1.0, edge_sigma*upscale)
    processed = sp.ndimage.interpolation.zoom(processed, zoom=1.0/upscale,
                                              output=None, order=3,
                                              mode='constant', cval=0.0,
                                              prefilter=True)

    # scale mag
    mag_scale = np.percentile(im[processed>0.5], 50)
    processed = processed*mag_scale
    
    if aperture is not None and crop_pad:
        im_pad = np.zeros_like(image, dtype=float)
        im_pad[ri:rf+1, ci:cf+1] = im
        im = im_pad
        
        im_pad = np.zeros_like(image, dtype=float)
        im_pad[ri:rf+1, ci:cf+1] = processed
        processed = im_pad

    # plot
    if plot:
        err = processed-im
        pct = 0.1
        vmin_max = np.percentile(err, [pct, 100-pct])
        vmin, vmax = np.abs(vmin_max).max() * np.array([-1, 1])
        
        f, (ax1, ax2, ax3) = plt.subplots(1, 3, sharex=True, sharey=True, figsize=(9,3))
        ax1.imshow(im)
        ax2.imshow(processed)
        ax3.imshow(err, vmin=vmin, vmax=vmax, cmap='bwr')
        ax1.set_title('Original')
        ax2.set_title('Processed')
        ax3.set_title('Processed : Original\n%0.3f - %0.3f' %(vmin_max[0], vmin_max[1]))
    
    return processed




def _parse_crop_rebin(crop_r, detY, detX, cyx, rebin, print_stats):
    # TODO: crop and rebin could be better intergrated 
    
    # cropping
    if crop_r is None:
        # all indices
        rii, rif = 0, detY-1
        cii, cif = 0, detX-1
    else:
        crop_r = np.round([crop_r]).astype(int)[0]
        if cyx is None:
            cyx = [(detY-1)/2.0, (detX-1)/2.0]
        cy, cx = np.round(cyx).astype(int)
    
        crop_r_max = int(min(cx, detX-1-cx, cy, detY-1-cy))  # L R T B
        if crop_r > crop_r_max:
            if print_stats:
                print("WARNING: 'crop_r' (%d) is being set to max. value (%d)." %(crop_r, crop_r_max))
            crop_r = crop_r_max
        # indices
        rii, rif = (cy-crop_r, cy+crop_r-1)
        cii, cif = (cx-crop_r, cx+crop_r-1)
    cropped_im_shape = (rif+1-rii, cif+1-cii)
    
    
    # rebinning
    rebinf = 1
    rebinning = rebin is not None and rebin != 1
    if rebinning:
        # change crop
        extra_pixels = int(np.ceil(cropped_im_shape[0]/float(rebin))*rebin) - cropped_im_shape[0]
        ext_pix_pads = extra_pixels // 2
        
        # this is where the decision on if extra pixels can be added and where 
        # they should go could be made
        if extra_pixels % 2:
            # odd
            ext_pix_pads = (-ext_pix_pads, ext_pix_pads+1)
        else:
            # even
            ext_pix_pads = (-ext_pix_pads, ext_pix_pads)
        riic, rifc = rii + ext_pix_pads[0], rif + ext_pix_pads[1]
        ciic, cifc = cii + ext_pix_pads[0], cif + ext_pix_pads[1]
        if riic < 0 or rifc > detY-1 or ciic < 0 or cifc > detX-1:
            # change rebin
            f, fs = _find_nearest_int_factor(cropped_im_shape[0], rebin)
            if rebin != f:
                if print_stats:
                    print('Image data cropped to:', cropped_im_shape)
                    print('Requested rebin (%d) changed to nearest value: %d. Possible values are:' %(rebin, f), fs)
                rebin = f
        else:
            rii, rif = riic, rifc
            cii, cif = ciic, cifc
            cropped_im_shape = (rif+1-rii, cif+1-cii)
            if print_stats:
                print('Image data cropped to:', cropped_im_shape)
        rebinf = rebin

    return cropped_im_shape, rebinf, rebinning, rii, rif, cii, cif




def map_image_function(data, nr, nc, cyx=None, crop_r=None, func=None, params=None,
                       rebin=None, parallel=True, ncores=None, print_stats=True,
                       nrnc_are_chunks=False):
    '''
    Map an arbitrary function over a multidimensional dataset.
    
    Parameters
    ----------
    data : array_like
        Mutidimensional data of shape (scanY, scanX, ..., detY, detX).
    nr : integer or None
        Number of rows to process at once (see Notes).
    nc : integer or None
        Number of columns to process at once (see Notes).
    cyx : length 2 iterable or None
        Centre of disk in pixels (cy, cx).
        If None, the centre is used.
    crop_r : scalar or None
        Radius of circle about `cyx` defining square crop limits used for
        cross-corrolation, in pixels.
        If None, the maximum square array about cyx is used.
    func : callable
        Function that operates (out-of-place) on an image: out = pre_func(im),
        where `im` is an ndarray of shape (detY, detX).
    params : None or dictionary
        If not None, a dictionary of parameters passed to the function.
    rebin : integer or None
        Rebinning factor for detector dimensions. None or 1 for none. 
        If the value is incompatible with the cropped array shape, the
        nearest compatible value will be used instead. 
        'cyx' and 'crop_r' are for the original image and need not be modified.
    parallel : bool
        If True, the calculations are multiprocessed.
    ncores : None or int
        Number of cores to use for mutliprocessing. If None, all cores
        are used.
    print_stats : bool
        If True, calculation progress is printed to stdout.
    nrnc_are_chunks : bool
        If True, `nr` and `nc` are interpreted as the number of chunks to
        process at once. If `data` is not chunked, `nr` and `nc` are used
        directly.
        
    Returns
    -------
    rtn : ndarray
        The result of mapping the function over the dataset. If the output of
        the function is non-uniform, the dimensions are those of the nondet axes
        and the dtype is object. If the function output is uniform, the first
        axis is of the length of the function return, unless it is singular, in
        which case it is removed.
    
    Notes
    -----
    
    If `nr` or `nc` are None, the entire dimension is processed at once.
    For chunked data, setting `nrnc_are_chunks` to True, and `nr` and `nc`
    to a suitable values can improve performance.
    
    Specifying 'crop_r' (and appropriate cyx) can speed up calculation significantly.
    
    Examples
    --------
    Center of mass:
    >>> import scipy as sp
    >>> import numpy as np
    >>> import fpd.fpd_processing as fpdp
    >>> from fpd.synthetic_data import disk_image, fpd_data_view
    
    >>> radius = 32
    >>> im = disk_image(intensity=1e3, radius=radius, size=256, upscale=8, dtype='u4')
    >>> data = fpd_data_view(im, (32,)*2, colours=0)
    >>> func = sp.ndimage.center_of_mass
    >>> com_y, com_x = fpdp.map_image_function(data, nr=9, nc=9, func=func)
    
    Non-uniform return:
    >>> def f(image):
    ...    l = np.random.randint(4)+1
    ...    return np.arange(l)
    >>> r = fpdp.map_image_function(data, nr=9, nc=9, func=f)

    Parameter passing:
    >>> def f(image, v):
    ...    return (image >= v).sum()
    >>> r = fpdp.map_image_function(data, nr=9, nc=9, func=f, params={'v' : 2})
    
    Doing very little (when reading from file, this is a measure of access
    and decompression overhead):
    >>> def f(image):
    ...    return None
    >>> data_chunk = data[:16, :16]
    >>> r = fpdp.map_image_function(data_chunk, nr=None, nc=None, func=f)
    
    '''
    
    if params is None:
        params = {}
    
    if nrnc_are_chunks:
        nr, nc = _condition_nrnc_if_chunked(data, nr, nc, print_stats)
    
    if ncores is None:
        ncores = mp.cpu_count()
    
    nondet = data.shape[:-2]
    nonscan = data.shape[2:]
    scanY, scanX = data.shape[:2]
    detY, detX = data.shape[-2:]
    
    r_if, c_if = _block_indices((scanY, scanX), (nr, nc))
    
    rtn = _parse_crop_rebin(crop_r, detY, detX, cyx, rebin, print_stats)
    cropped_im_shape, rebinf, rebinning, rii, rif, cii, cif = rtn

    rebinned_im_shape = tuple([x//rebinf for x in cropped_im_shape])
    #print('Cropped shape: ', cropped_im_shape)
    #if rebinning:
        #print('Rebinned cropped shape: ', rebinned_im_shape)
    
    
    rd = np.empty(nondet, dtype=object)
    
    if print_stats:
        print('\nMapping image function')
        tqdm_file = sys.stderr
    else:
        tqdm_file = DummyFile()
    total_nims = np.prod(nondet)
    with tqdm(total=total_nims, file=tqdm_file, mininterval=0, leave=True, unit='images') as pbar:
        for i, (ri, rf) in enumerate(r_if):
            for j, (ci, cf) in enumerate(c_if):               
                # read selected data (into memory if hdf5)  
                d = data[ri:rf, ci:cf, ..., rii:rif+1, cii:cif+1]
                d = np.ascontiguousarray(d)
                if rebinning:
                    ns = d.shape[:-2] + tuple([int(x/rebinf) for x in d.shape[-2:]])
                    d = rebinA(d, *ns)
                
                partial_func = partial(func, **params)
                d_shape = d.shape
                d.shape = (np.prod(d_shape[:-2]),)+d_shape[-2:]
                
                if parallel:
                    pool = mp.Pool(processes=ncores)
                    rslt = pool.map(partial_func, d)
                    pool.close()
                else:
                    rslt = list(map(partial_func, d))
                
                t = np.empty(len(rslt), dtype=object)
                t[:] = rslt
                rd[ri:rf, ci:cf].flat = t 
                
                pbar.update(np.prod(d.shape[:-2]))
    if print_stats:
        print('')
        sys.stdout.flush()
    
    # convert dtype from object to more appropriate type if possible
    try:
        rdf = rd.ravel()
        rdfa = np.vstack(rdf).reshape(rd.shape + (-1,))
        rtn = np.rollaxis(rdfa, -1, 0)
    except ValueError:
        rtn = rd

    # remove return axis if singular
    if rtn.ndim > rd.ndim:
        if rtn.shape[0] == 1:
            rtn = rtn[0]
    
    return rtn



def rotate_vector(yx_array, theta, axis=0):
    '''
    Rotate a vector by an angle.
    
    Parameters
    ----------
    yx_array : ndarray
        Arrays of vectors, one dimension of which has [y,x].
    theta : scalar
        Rotation angle in degrees (anticlockwise).
    axis : scalar
        Axis of yx_array with [y, x] values.
    
    '''
    
    single_yx = False
    if yx_array.ndim == 1:
        yx_array = yx_array[..., None]
        single_yx = True
    
    yx = np.rollaxis(yx_array, axis, 0)
    yx_shape = yx.shape
    yx = yx.reshape((yx.shape[0], np.prod(yx.shape[1:])))
    
    t = np.deg2rad(theta)
    rot_mat = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]]).T
    # transpose for anticlockwise with yx in 1st axis
    
    yx_rot = rot_mat.dot(yx)
    yx_rot.shape = yx_shape
    ims_rot = np.rollaxis(yx_rot, 0, axis+1)
    
    if single_yx:
        ims_rot = ims_rot[..., 0]
    return ims_rot


class VirtualAnnularImages(object):
    def __init__(self, data, nr=16, nc=16, cyx=None, parallel=True, ncores=None,
                 nrnc_are_chunks=False, print_stats=True, mask=None, spf=1):
        '''
        Fast virtual annular aperture image class using cumulative sums to
        calculate all data only once, and also provides interactive plotting.
        
        To do this, it uses: `fpd.fpd_processing.radial_average` and
        `fpd.fpd_processing.map_image_function`. See those functions for details
        not documented below.
                
        This method is very fast and so useful for exploring, but is not as
        flexible or accurate as `fpd.fpd_processing.synthetic_images`.
        
        The accuracy is typically a few percent with 'spf=1'. It can be made
        to be more accurate at the expense of computation time by increasing the 
        subpixel evaluation of the radial distribution through the `spf` parameter.
        
        Parameters
        ----------
        data : ndarray or string or dict
            If ndarray, `data` is the data to be processed, as defined in the
            fpd.fpd_processing.map_image_function. If a string, it should be the
            filename of a npz file with the parameters saved from the `save_data`
            method. If a dictionary, it must contain the same parameters.
        cyx : length 2 iterable or None
            The centre y and x coordinates of the direct beam in pixels.
            This value must be specified unless `data` is an object to be loaded. 
        '''
        
        self.r1 = None
        self.r2 = None
        self.virtual_image = None
        
        if _p3:
            s_obj = str
        else:
            s_obj = basestring
        
        if isinstance(data, s_obj):
            # add data filename attribute and load data as dict
            self._source_filename = data
            data = dict(np.load(data))
        if isinstance(data, dict):
            # add attributes
            for k,v in data.items():
                setattr(self, k, v)                
        else:
            # process data to generate attributes
            if cyx is None:
                raise TypeError('cyx must be specified')
            self.data_shape = np.array(data.shape)
            self.cyx = np.array(cyx)
            self._calc_rdf(data, nr, nc, cyx, mask, spf, parallel, ncores,
                           nrnc_are_chunks, print_stats)
        
        # cummulative sums
        self.rms_cs = np.cumsum(self.rms * 2*np.pi * self.r_pix[:, None, None], axis=0)
        self.a_cs = np.cumsum(2*np.pi*(self.r_pix), axis=0)
    
    
    def save_data(self, filename=None):
        '''
        Save the calculated parameters to file for later reloading through the `data`
        initialisation parameter.
        
        Parameters
        ----------
        filename : None or string
            File name to save data under. If None a date stamped filename is generated.
            If the file name does not end in '.npz', it is automatically added.
        '''
        
        version = 1
        
        if filename is None:
            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = 'VirtualAnnularImages_' + now
        if filename.endswith('.npz') is False:
            filename = filename + '.npz'
        
        np.savez(filename, 
                 data_shape=self.data_shape,
                 cyx=self.cyx,
                 r_pix=self.r_pix,
                 rms=self.rms,
                 version=version)
        print('Data saved to: %s' %(filename))
        
    def _calc_rdf(self, data, nr, nc, cyx, mask, spf, parallel, ncores,
                  nrnc_are_chunks, print_stats):
        rtn = map_image_function(data, nr, nc, 
                        cyx=cyx, 
                        crop_r=None,
                        func=radial_average,
                        params={'cyx': cyx, 'mask': mask, 'spf': spf},
                        rebin=None,
                        parallel=parallel,
                        ncores=ncores,
                        nrnc_are_chunks=nrnc_are_chunks,
                        print_stats=print_stats)
        
        r_pix, rms = rtn.reshape((2, -1) + rtn.shape[1:])
        
        # 1-D
        self.r_pix = np.squeeze(r_pix[:, 0, 0])
        # rdf, scanY, scanX
        if rms.ndim == 4:
            # colour
            rms = rms[..., 0]
        
        self.rms = rms
        del rtn
        
    
    def annular_slice(self, r1, r2):
        '''
        Calculate an annular virtual image.
        
        Parameters
        ----------
        r1 : scalar
            Inner radius of aperture in pixels.
        r2 : scalar
            Inner radius of aperture in pixels.
        
        Returns
        -------
        virtual_image : ndarray
            The virtual image.
        
        '''
        self.r1 = r1
        self.r2 = r2
        
        r1i = np.argmax(self.r_pix>=r1)
        r2i = np.argmin(self.r_pix<=r2)-1
        v = self.rms_cs[r2i] - self.rms_cs[r1i]
        va = self.a_cs[r2i] - self.a_cs[r1i]
        n = np.pi*(r2**2-r1**2) / va
        self.virtual_image = v*n
        
        return self.virtual_image
    
    
    def plot(self, r1=None, r2=None, nav_im=None, norm='log', scroll_step=1, alpha=0.3, cmap=None, pct=0.1, mradpp=None):
        '''
        Interactive plotting of the virtual aperture images.
        
        The sliders control the parameters and may be clicked, dragged or scrolled.
        Clicking on inner (r1) and outer (r2) slider labels sets the radii values
        to the minimum and maximum, respectively.
        
        Parameters
        ----------
        r1 : scalar
            Inner radius of aperture in pixels.
        r2 : scalar
            Inner radius of aperture in pixels.
        nav_im : None or ndarray
            Image used for the navigation plot. If None, a blank image is used.
        norm : None or string:
            If not None and norm='log', a logarithmic cmap normalisation is used.
        scroll_step : int
            Step in pixels used for each scroll event.
        alpha : float
            Alpha for aperture plot in [0, 1].
        cmap : None or a matplotlib colormap
            If not None, the colormap used for both plots.
        pct : scalar
            Slice image percentile in [0, 50).
        mradpp : None or scalar
            mrad per pixel.
        
        '''
        
        from matplotlib.widgets import Slider
        
        self._scroll_step = max([1, int(scroll_step)])
        self._pct = pct
        
        if norm is not None:
            if norm.lower() == 'log':
                from matplotlib.colors import LogNorm
                norm = LogNorm()
        
        # condition rs
        if r1 is not None:
            self.r1 = r1
        else:
            if self.r1 is None:
                self.r1 = 0
        if r2 is not None:
            self.r2 = r2
        else:
            if self.r2 is None:
                self.r2 = int((self.data_shape[-2:]/4).mean())
        self.rc = (self.r2 + self.r1) / 2.0
        
        if nav_im is None:
            nav_im = np.zeros(self.data_shape[-2:])
        
        # calculate data
        virtual_image = self.annular_slice(self.r1, self.r2)
        
        # prepare plots
        if mradpp is None:
            self._f_nav, (ax_nav, ax_cntrst) = plt.subplots(1, 2, figsize=(8.4, 4.8))
        else:
            # add 2nd x-axis
            # https://matplotlib.org/examples/axes_grid/parasite_simple2.html
            from mpl_toolkits.axes_grid1.parasite_axes import SubplotHost
            import matplotlib.transforms as mtransforms
            self._f_nav = plt.figure(figsize=(8.4, 4.8))
            ax_nav = SubplotHost(self._f_nav, 1, 2, 1)
            ax_cntrst = SubplotHost(self._f_nav, 1, 2, 2)
            
            aux_trans = mtransforms.Affine2D().scale(1.0/mradpp, 1.0)
            ax_mrad = ax_cntrst.twin(aux_trans)
            ax_mrad.set_viewlim_mode("transform")
            
            self._f_nav.add_subplot(ax_nav)
            self._f_nav.add_subplot(ax_cntrst)
            
            ax_mrad.axis["top"].set_label('mrad')
            ax_mrad.axis["top"].label.set_visible(True)
            ax_mrad.axis["right"].major_ticklabels.set_visible(False)
        
        self._f_nav.subplots_adjust(bottom=0.3, wspace=0.3)
        axr1 = plt.axes([0.10, 0.05, 0.80, 0.03])
        axr2 = plt.axes([0.10, 0.10, 0.80, 0.03])
        axr3 = plt.axes([0.10, 0.15, 0.80, 0.03])
        
        val_max = self.r_pix.max()
        try:
            self._sr1 = Slider(axr1, 'r1', 0, val_max-1, valinit=self.r1, valfmt='%0.0f', valstep=1)
            self._sr2 = Slider(axr2, 'r2', 1, val_max, valinit=self.r2, valfmt='%0.0f', valstep=1)
        except AttributeError:
            self._sr1 = Slider(axr1, 'r1', 0, val_max-1, valinit=self.r1, valfmt='%0.0f')
            self._sr2 = Slider(axr2, 'r2', 1, val_max, valinit=self.r2, valfmt='%0.0f')
        self._sr3 = Slider(axr3, 'rc', 1, val_max, valinit=self.rc, valfmt='%0.1f')
        
        # these don't seem to work
        #self._sr1.slider_max = self._sr2
        #self._sr2.slider_min = self._sr1
        
        self._sr1.on_changed(self._update_r_from_slider)
        self._sr2.on_changed(self._update_r_from_slider)
        self._sr3.on_changed(self._update_rc_from_slider)
        
        ax_nav.imshow(nav_im, norm=norm, cmap=cmap)
        ax_nav.set_xlabel('Detector X (pixels)')
        ax_nav.set_ylabel('Detector Y (pixels)')
        
        
        # line plot
        r_cntrst_max = int(np.abs(self.data_shape[-2:] - self.cyx).max())
        dw = 1
        rs = np.arange(dw, r_cntrst_max)
        
        r1, r2 = self.r1, self.r2
        sls = np.array([self.annular_slice(r-dw, r) for r in rs])
        self.r1, self.r2 = r1, r2
        
        self._contrast_y = np.std(sls, (1,2))**2 / np.mean(sls, (1, 2))
        self._contrast_x = rs-dw/2.0
        ax_cntrst.plot(self._contrast_x, self._contrast_y)
        ax_cntrst.minorticks_on()
        ax_cntrst.set_xlabel('Radius (pixels)')
        ax_cntrst.set_ylabel('Contrast (std^2/mean)')
        self._span = ax_cntrst.axvspan(self.r1, self.r2, color=[1, 0, 0, 0.1], ec='r')
        
        # wedges
        fc = [0, 0, 0, alpha]
        ec = 'r'
        from matplotlib.patches import Wedge
        self._rmax = val_max + 1
        self._w2 = Wedge(self.cyx[::-1], self._rmax, 0, 360, width=self._rmax-self.r2, fc=fc, ec=ec)
        self._w1 = Wedge(self.cyx[::-1], self.r1, 0, 360, width=self.r1, fc=fc, ec=ec)
        ax_nav.add_artist(self._w2)
        ax_nav.add_artist(self._w1)
        
        self._f_im, ax_im = plt.subplots(1, 1)
        vmin, vmax = np.percentile(virtual_image, [self._pct, 100-self._pct])
        self._vim = ax_im.imshow(virtual_image, cmap=cmap, vmin=vmin, vmax=vmax)
        self._cb = plt.colorbar(self._vim)
        self._cb.set_label('Counts')
        ax_im.set_xlabel('Scan X (pixels)')
        ax_im.set_ylabel('Scan Y (pixels)')
        
        cid = self._f_nav.canvas.mpl_connect('scroll_event', self._onscroll)
        
        self._sr1.label.set_picker(True)
        self._sr2.label.set_picker(True)
        cid_pick = self._f_nav.canvas.mpl_connect('pick_event', self._onpick)
        
    def _onpick(self, event):
        if event.artist == self._sr1.label:
            self.r1 = self._sr1.valmin
            self._update_plot_r_from_val()
        if event.artist == self._sr2.label:
            self.r2 = self._sr2.valmax
            self._update_plot_r_from_val()
    
    def _update_r_from_slider(self, val):
        self.r1 = int(self._sr1.val)
        self.r2 = int(self._sr2.val)
        self.rc = (self.r2 + self.r1) / 2.0
        
        self._sr3.eventson = False
        self._sr3.set_val(self.rc)
        self._sr3.eventson = True
        
        _ = self.annular_slice(self.r1, self.r2)
        
        self._w1.set_radius(self.r1)
        self._w1.set_width(self.r1)
        self._w2.set_width(self._rmax - self.r2)
        
        xy = self._span.xy
        xy[:, 0] = [self.r1, self.r1, self.r2, self.r2, self.r1]
        self._span.set_xy(xy)
        
        self._vim.set_data(self.virtual_image)
        #vmin, vmax = self.virtual_image.min(), self.virtual_image.max()
        vmin, vmax = np.percentile(self.virtual_image, [self._pct, 100-self._pct])        
        self._vim.set_clim(vmin, vmax)
        
        self._f_im.canvas.draw_idle()
        self._f_nav.canvas.draw_idle()

    def _update_rc_from_slider(self, val):
        rc_prev = (self.r2 + self.r1) / 2.0
        
        drc = self._sr3.val - rc_prev
        
        self._sr1.eventson = False
        self._sr1.set_val(self._sr1.val + drc)
        self._sr1.eventson = True
        
        self._sr2.eventson = False
        self._sr2.set_val(self._sr2.val + drc)
        self._sr2.eventson = True
        
        self._update_r_from_slider(None)
    
    def _update_plot_r_from_val(self):
        self._sr1.eventson = False
        self._sr1.set_val(self.r1)
        self._sr1.eventson = True
        
        self._sr2.eventson = False
        self._sr2.set_val(self.r2)
        self._sr2.eventson = True
        
        self._update_r_from_slider(None)
            
    def _onscroll(self, event):
        if event.inaxes not in [self._sr1.ax, self._sr2.ax, self._sr3.ax]:
            return
        if event.button == 'up':
            dr =  self._scroll_step
        else:
            dr = -self._scroll_step
        
        if event.inaxes == self._sr1.ax:
            self.r1 += dr
        elif event.inaxes == self._sr2.ax:
            self.r2 += dr
        else:
            self.r1 += dr
            self.r2 += dr
        self._update_plot_r_from_val()

