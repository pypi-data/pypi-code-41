# -*- coding: utf-8 -*-
'''
    geophpy.processing.general
    --------------------------

    DataSet Object general processing routines.

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''

import numpy as np
from numpy.polynomial.polynomial import Polynomial as npPolynomial

import scipy.ndimage as ndimage
from scipy.stats import pearsonr, spearmanr, kendalltau

from geophpy.misc.utils import *
from geophpy.operation.general import *
import geophpy.operation.general as genop

import warnings

#------------------------------------------------------------------------------#
# User defined parameters                                                      #
#------------------------------------------------------------------------------#
# list of correlation methods available for wumappy interface
festoon_correlation_list = ['Crosscorr', 'Pearson', 'Spearman', 'Kendall']

# list of destriping methods available for wumappy interface
destriping_list = ['additive', 'multiplicative']

destripingreference_list = ['mean', 'median']

destripingconfig_list = ['mono', 'multi']

# list of regional trend methods available for wumappy interface
regtrendmethod_list = ['relative', 'absolute']

# list of regional trend components available for wumappy interface
regtrendcomp_list = ['local', 'regional']

class NoGriddedData(UserWarning):
    ''' Warning when no gridded data are encounter in in a dataset. '''
    pass

#------------------------------------------------------------------------------#
# Processings                                                                  #
#------------------------------------------------------------------------------#
def peakfilt(dataset, method='hampel', halfwidth=5, threshold=3, mode='relative',
              setnan=False, valfilt=False):
    ''' Datset peak filtering

    cf. :meth:`~geophpy.dataset.DataSet.peakfilt`

    '''

    # Data to filter ###########################################################
    # Values
    if valfilt or dataset.data.z_image is None:
        val = dataset.data.values[:,2]

    # Zimage
    elif not valfilt and dataset.data.z_image is not None:
        val = dataset.data.z_image

    # Otherwise
    else:
        return # raise error here

    # Filter type ##############################################################
    # Hampel filter
    if method=='hampel':
        valcorr = _hampel_filter1d(val, K=halfwidth, t=threshold)

    # Median filter
    elif method=='median':
        valcorr = _median_filter1d(val, K=halfwidth, t=threshold, mode=mode)

    # Unknown filter
    else:
        pass # raise error here

    # Value replacement type ###################################################
    # Replacing by NaNs
    if setnan:
        val[val!=valcorr] = np.nan

    # or by local median
    else:
        val = valcorr

    # Filter statistics ########################################################
    # ...Unused...
    # Number of replaced value
    nb_filt = sum(val!=valcorr)


    # Returning filtered values ################################################
    if valfilt or dataset.data.z_image is None:
        dataset.data.values[:,2] = val

    else:
        dataset.data.z_image = val

    return dataset


def _hampel_filter1d(arr, K, t=3):
    '''
    One-dimensional Hampel filter.

    If the array has multiple dimensions, the filter is computed
    along a flattened version of the array.

    Parameters
    ----------
    arr : ndarray
        Input array to filter.

    K : integer
        Filter half-width (val[k-K],... , val[k], ..., val[k+K]).

    t : scalar (positive)
        Hampel filter threshold parameter.
        If t=0, it is equal to a ``standard median filter``.

    Returns
    -------
    hampel_filter1d : ndarray

    ...Notes, citation...
    '''

    arr = np.asarray(arr)  #  ensures input is a numpy array
    N = arr.size
    out_shape = arr.shape
    arrfilt = np.empty(arr.shape).flatten()  # output allocation
    
    #
    # ...TBD... pad with NaNs instead of repeatinf 1st and last element ?
    #
    arrPad =  np.pad(arr.flatten(), K, 'edge')  # Padded to ensure a centered filter
                                      # for all elements of the array

    
    # 1-D Hampel filter on each row array
##    for line in arr:
##        N = arr.size
##        #
##        # ...TBD... pad with NaNs instead of repeatinf 1st and last element ?
##        #
##        arrPad =  np.pad(arr.flatten(), K, 'edge')  # Padded to ensure a centered filter
##                                          # for all elements of the array
        
        #
        # ...TBD... define an hampeloperator function as in wallisoperator ??
        #
    for i in range(N):
        vals = arrPad[i:i+2*K+1]  # values in the current window
        center = vals[K]  # center value of the window
        ref = np.median(vals)  # window reference value (median)

        # eq 4.72 from Pearson and Gabbouj 2016 for the MADM scale estimate
        # "unbiased estimator of standard deviation for Gaussian data"
        Sk = 1.4826*np.median( np.abs(vals - ref) )  # MADM scale estimate
        condition = t*Sk
        deviation =  np.abs(center - ref)

        # Central point is an outlier 
        if deviation > condition:
            valfilt = ref

        # Central point is an inlier
        else:
            valfilt = center

        arrfilt[i] = valfilt

    return arrfilt.reshape(out_shape)


def _median_filter1d(arr, K, t=5, mode='relative'):
    '''
    One-dimensional (decision-theoretic) median filter.

    Parameters
    ----------
    arr : ndarray
        Input array to filter.

    K : integer
        Filter half-width (val[k-K],... , val[k], ..., val[k+K]).

    t : scalar (positive)
        Median filter threshold parameter. Absolute value or percentage
        in the range [0-1].

    mode : str {'relative', 'absolute'}
        Filter mode. If 'relative', the threshold is a percentage of the local
        median value. If 'absolute', the threshold is a value.

    Returns
    -------
    median_filter1d : ndarray

    Notes
    -----
    In this decision-theoretic version of the median filter, by opposition to
    a standard median filter, the value are replaced only if the deviation to
    the local median is greater than a ``threshold``.
    The threshold can be expressed in percentage of the local median (the values
    are replaced only if the deviation to the median is greater than
    ``threshold*percent`` of the local median)  or in absolute value
    (the values are replaced only if the deviation to the median is
    greater than ``threshold``).

    '''

    arr = np.asarray(arr)  #  ensures input is a numpy array
    N = arr.size
    out_shape = arr.shape
    arrfilt = np.empty(arr.shape).flatten()  # output allocation
    t = np.abs(t)  # ensures a positive threshold
    
    #
    # ...TBD... pad with NaNs instead of repeatinf 1st and last element ?
    #
    arrPad =  np.pad(arr.flatten(), K, 'edge')  # Padded to ensure a centered filter
                                      # for all elements of the array

    for i in range(N):
        vals = arrPad[i:i+2*K+1]  # values in the current window
        center = vals[K]  # center value of the window
        ref = np.median(vals)  # window reference value (median)

        deviation =  np.abs(center - ref)

        #print('center', 'ref', 'deviation', 'Dev/ref')
        #print(center, ref, deviation, deviation/ref)

        # Threshold type selection
        if mode=='relative':
            if t>1:  # raise error
                t=t/100
            condition = np.abs(t*ref)

        else:
            condition = t

        # Inlier/Outlier decision
        if deviation > condition:
            valfilt = ref

        else:
            valfilt = center

        arrfilt[i] = valfilt

    return arrfilt.reshape(out_shape)


def threshold(dataset, setmin=None, setmax=None, setmed=False, setnan=False, valfilt=False):
    ''' Dataset thresholding

    cf. :meth:`~geophpy.dataset.DataSet.threshold`

    '''

    if valfilt or dataset.data.z_image is None:
        val = dataset.data.values[:,2]

    elif not valfilt and dataset.data.z_image is not None:
        val = dataset.data.z_image
        ny, nx = val.shape

    if setmin is not None:
        idx = np.where(val < setmin)
        if (setnan):
            val[idx] = np.nan
        elif (setmed):
            # ...TBD... replace by median on x sample centered in the replaced value
            # Median of each profile
            median_profile = np.nanmedian(val, axis=0)
            # Into a matrix for global indexing
            median_profile.shape = [1,median_profile.size]
            med_mat = np.repeat(median_profile, val.shape[0],axis=0)
            # Data replacement
            val[idx] = med_mat[idx]
         
        else:
            val[idx] = setmin

    if setmax is not None:
        idx = np.where(val > setmax)

        if setnan:
            val[idx] = np.nan

        elif setmed:
            # ...TBD... replace by median on x sample centered in the replaced value
            # Median of each profile
            median_profile = np.nanmedian(val, axis=0)
            # Into a matrix for global indexing
            median_profile.shape = [1,median_profile.size]
            med_mat = np.repeat(median_profile, val.shape[0],axis=0)
            # Data replacement
            val[idx] = med_mat[idx]

        else:
            val[idx] = setmax

    return dataset


def medianfilt(dataset, nx=3, ny=3, percent=0, gap=0, valfilt=False):
    ''' 2-D median filter

    cf.  :meth:`~geophpy.dataset.DataSet.medianfilt`

    '''

    # Filter values ...TBD... ######################################
    if valfilt or dataset.data.z_image is None:
        # ...TBD... should use original wumap algorithm
        pass
    # Filter zimage ################################################
    elif not valfilt and dataset.data.z_image is not None:
        zimg = dataset.data.z_image

        # Standard median filter (each value is replaced by the median)
        if (percent == 0) & (gap == 0):
            zimg[:,:] = ndimage.median_filter(zimg, size=(nx, ny))

        # Decision-theoric median filter (replaced only if condition fulfilled)
        else:
            # ...TBD... should use here also original wumap algorithm
            zmed = ndimage.median_filter(zimg, size=(nx, ny))
            zdiff = np.absolute(zimg-zmed)
            
            # Gap to the median in percent (Electric surveys) 
            if (percent != 0) & (gap == 0):
                idx = np.where(zdiff> percent/100 * zmed)

            # Gap to the median value (Magnetic surveys)
            elif (percent == 0) & (gap != 0):
                idx = np.where(zdiff> gap)

            zimg[idx[0],idx[1]] = zmed[idx[0],idx[1]]


def getfestooncorrelationlist():
    '''
    cf. dataset.py
    '''

    return festoon_correlation_list


def festoonfilt(dataset, method='Crosscorr', shift=0, corrmin=0.4, uniformshift=False,
                setmin=None, setmax=None, valfilt=False):
    ''' Destaggering filter

    cf. :meth:`~geophpy.dataset.DataSet.festoonfilt`

    '''

    # Ignoring out of the range data
    dstmp = dataset.copy()
    dstmp.threshold(setmin=setmin, setmax=setmax, setnan=True, valfilt=valfilt)

    ###
    ##
    #...TBD...
    ##
    ###
    # Filtering ungridded data
    if valfilt or dataset.data.z_image is None:
        pass
        # use dataset.interpolate('none') and sample to propagaet festoon filter in
        # ungridded dataset.
        return

    # Filtering gridded data
    else:
        # Valid data profiles
        zimg = dataset.data.z_image
        idx_nan_slice = np.all(np.isnan(zimg), axis=0)  # index of columns containing only nans
        ny, nx = zimg[:, ~idx_nan_slice].shape

        cols = even_cols_idx(nx)
        shift = np.array(shift) # shift as ndarray (use of shape, size)
 
        ###
        # Dataset correlation map and best shift
        cormap, pva1 = correlmap(dstmp, method)  # correlation map
        shift_best, shifts = correlshift(cormap, pva1, corrmin=corrmin)  # global best shift

        # Uniform shift
        if uniformshift:

            # Shift not provided (default=0)
            if shift == 0 and shift.size == 1:
                shifts = np.repeat(shift_best, len(cols))  # best shift repeated for each profile

            # Shift provided (uniform scalar value)
            elif shift != 0 and shift.size == 1:
                shifts = np.repeat(shift, len(cols))   # given shift repeated for each profile
        
        # Non-uniform shift
        elif not uniformshift:

            # Shift not provided / uniform shift provided
            if shift.size == 1:
                pass  # estimated best shifts wil be used

            # Shift provided (custom shift sequence)
            else:
                shifts = shift

        # Apply the shift to each valid profile
        j = 0
        for i in cols:
            zimg[:,i] = arrayshift(zimg[:,i], shifts[j], val=np.nan)
            j+=1

##        # Uniform shift
##        if uniformshift:
##
##            # Shift not provided (default=0)
##            if shift == 0 and shift.size == 1:
##                cormap, pva1 = correlmap(dstmp, method)  # correlation map
##                shift, shiftprf = correlshift(cormap, pva1, corrmin=corrmin)  # global best shift
##                shiftprf = np.repeat(shift, len(cols))  # best shift repeated for each profile
##              
##            # Shift provided (uniform scalar value)
##            elif shift != 0 and shift.size == 1:
##                shiftprf = np.repeat(shift, len(cols))   # given shift repeated for each profile
##
##        # Non-uniform shift
##        elif not uniformshift:
##
##            # Shift not provided / uniform shift provided
##            if shift.size == 1:
##                cormap, pva1 = correlmap(dstmp, method)  # correlation map
##                shift, shiftprf = correlshift(cormap, pva1, corrmin=corrmin)  # global and profile best shifts
##              
##            # Shift provided (custom shift sequence)
##            else:
##                tmp = shift  # custom shift sequence
##                cormap, pva1 = correlmap(dataset, method)  # correlation map
##                shift, shiftprf = correlshift(cormap, pva1, corrmin=corrmin)  # global best shift
##                shiftprf =  tmp
##
##        # Apply the shift to each valid profile
##        j = 0
##        for i in cols:
##            zimg[:,i] = arrayshift(zimg[:,i], shiftprf[j], val=np.nan)
##            j+=1

    return shift


def correlcols(nx):
   ''' Return odd column index for a number of columns '''

   # Even column number
   if nx % 2 == 0:
       return range(1, nx-1, 2)

   # Odd column number
   else:
       return range(1, nx, 2) # ...TBD... à revoir ?


def even_cols_idx(ncol):
    ''' Return even column index for a given number of columns.

    As Python index starts at 0, return index are actually odd numbers ^^.

    '''

    return range(1, ncol, 2) 


def correlmap(dataset, method='Crosscorr'):
    ''' Profile-to-profile correlation map.

    cf. :meth:`~geophpy.dataset.correlmap`

    '''

    ###
    ##
    # TO IMPLEMEBTED in next version if possible
    ##
    ###
    # Processing ungridded data values #########################################
    valfilt = False
    if valfilt or dataset.data.z_image is None:
        warnings.warn('No gridded data, no processing done.', NoGriddedData)

    # Ignoring All-NaN slices
    ## Typically 1m x-step displayed at 50cm without interpolation.
    zimg_original = dataset.data.z_image
    idx_nan_slice = np.all(np.isnan(zimg_original), axis=0)  # index of columns containing only nans
    zimg = zimg_original[:, ~idx_nan_slice].copy()

    # Spatial properties
    #zimg   = dataset.data.z_image
    #ny, nx = zimg.shape
    #cols = correlcols(zimg.shape[1])  # index of even columns
    ###
    ny, nx = zimg.shape
    cols = even_cols_idx(nx)

    if nx % 2 == 0:  # even number of profiles
        last_col = np.reshape(zimg[:,-1], (-1, 1))
        zimg = np.hstack((zimg, last_col))
    ###

    # Correlation map & pvalue initialization
    jmax = 2*ny-1  # maximum profile shift
    cormap = np.full((jmax, len(cols)), np.nan)  # arrays filled with NaN
    pva1 = cormap.copy()

    # Use Cross-correlation map ################################################
    ii   = 0
    if method.upper() == 'CROSSCORR':
       for col in cols:
 
          # Standardized mean profile
          zm   = (zimg[:,col-1] + zimg[:,col+1]) / 2. # ...TBD... nanmean ?
          zm   = (zm - np.nanmean(zm)) / np.nanstd(zm)
              
          # Standardized current profile
          zi   = zimg[:,col] * 1.
          zi   = (zi - np.nanmean(zi)) / np.nanstd(zi)
               
          # Valid data index
          idx  = np.isfinite(zm) & np.isfinite(zi)
          jlen = 2*len(idx.nonzero()[0])-1
               
          # Cross-correlation function map
          if (jlen > 0):
             jmin  = (jmax - jlen) // 2
             cormap[jmin:jmin+jlen,ii] = np.correlate(zm[idx],zi[idx], mode='full') / idx.sum()
             pva1[jmin:jmin+jlen,ii] = 1
                  
          ii += 1
         
    ###
    ##
    #  ??? Should we really keep these correlation calculation ???
    # their are computationally extensive without for no real gain
    # I'd stick with only the cross-correlation
    ##
    ###
    # Use Pearson, Spearman or Kendall correlation ##############
    ## The current profile is manually shifted of a sample at each
    ## iteration. The correlation coefficient is then computed
    ## between the shifted profile and the mean of its two
    ## adjacent profiles.       
    else:           
        for col in cols:
               
            # Mean profile
            zm = (zimg[:,col-1] + zimg[:,col+1]) / 2. # ...TBD... nanmean ?
            zm   = (zm - np.nanmean(zm)) / np.nanstd(zm)
            
            k = 0
     
            for shift in range(-ny+1,ny):
                # Calculation for at least 1/2 of  overlap between profiles
                # Prevents high correlation value at the border of the
                # correlation map (low number of samples)
                if shift<=ny//2 and shift >= -ny//2:
                     # Shifting current profile
                    zi = arrayshift(zimg[:,col], shift, val=None)
                
                    # Not NaN or inf in data
                    idx = np.isfinite(zm) & np.isfinite(zi)
                    jlen = 2*len(idx.nonzero()[0])-1
                
                    # Correlation coefficent map
                    if (jlen > 0):
                     
                        # Pearson
                        if (method == 'Pearson'):
                            corcoef, pval = pearsonr(zm[idx],zi[idx])

                        # Spearman
                        elif (method == 'Spearman'):
                            corcoef, pval = spearmanr(zm[idx],zi[idx])

                        # Kendall
                        elif (method == 'Kendall'):
                            corcoef, pval = kendalltau(zm[idx],zi[idx])

                        # Undefined
                        else:
                           # ...TBD... raise an error here !
                           corcoef = 0
                           pval = 0
                           pass
                     
                        # Filling arrays
                        cormap[k,ii] = corcoef
                        pva1[k,ii] = pval
                     
                k+=1
                  
            ii+=1

    return cormap, pva1


def correlshift(cormap, pva1, corrmin=0.4, apod=None, output=None):
    ''' Maximum correlation shift.

    cf. :meth:`~geophpy.dataset.correlshift`

    '''

    ny = (cormap.shape[0] + 1) // 2

    # Define correlation curve apodisation threshold #################
    if apod is None:
        apod = 0.1  # percent of the max correl coef

    # Make a mask for nans and apodisation ######################
    MaskApod  = np.isfinite(cormap).sum(axis=1).astype(float)
    idx   = np.where(MaskApod < max(MaskApod) * apod)
    MaskApod[idx] = np.nan

    pval  = np.isfinite(pva1).sum(axis=1).astype(float)
    idx   = np.where(pval < max(pval) * apod)
    pval[idx] = np.nan

    # Mask for 1/2 overlap profile in correlation map ###########
    # Prevents high correlation value at the border of the
    # correlation map (low number of samples) to drag the shift
    y = np.arange(cormap.shape[0])
    ymin = cormap.shape[0]*  2 // 6  # inf 1/4 of correl map
    ymax = cormap.shape[0]*  4 // 6  # sup 1/4 of correl map
    idx = np.where(np.logical_or(y<ymin, y>ymax))

    coroverlap = cormap.copy()
    coroverlap[idx,:] =  0

    # Maximum correlation shift for every profile ###############
    idx = np.argmax(coroverlap, axis=0)
    corrmax = np.amax(coroverlap, axis=0)  # profiles' max correlation
    shiftprf = idx -ny+1

    if corrmin is not None:
        shiftprf[np.where(corrmax<corrmin)] = 0
          
    # Fold the correlation map for global shift #################
    cor  = np.nansum(coroverlap,axis=1) / MaskApod
    #cor  = np.nansum(cormap,axis=1) / MaskApod
    #pva2  = np.nansum(pva1,axis=1) / pval
    
    #corm2  = cor2 / pva2
    # corm  = cor / pva2  # producess very high value if pval is low
    corm  = cor
         
    # Deduce the best 'shift' value from the max correl coef ####
    idx   = (corm == np.nanmax(corm)).nonzero()
    
    # ... TBD ... temporay fix for correlation calculation bug
    # giving no results
    if idx[0] is None:
        shift = 0

    # ...TBD... en fait ici fitter une gaussienne et trouver son max
    else:
        shift = idx[0][0]-ny+1

    if output is not None:
        output[:] = corm[:]

    return shift, shiftprf


def zeromeanprofile(dataset, setvar='median', setmin=None, setmax=None, valfilt=False):
    ''' Zero-traverse filter

    cf. :meth:`~geophpy.dataset.DataSet.zeromeanprofile`

    '''

    destripecon(dataset, Nprof=0, setmin=setmin, setmax=setmax, method='additive', reference=setvar, config='mono', valfilt=valfilt)
    #return dataset


def getdestripinglist():
    '''
    cf. dataset.py
    '''
    return destriping_list


def getdestripingreferencelist():
    '''
    cf. dataset.py
    '''
    return destripingreference_list


def getdestripingconfiglist():
    '''
    cf. dataset.py
    '''
    return destripingconfig_list


def detrend(dataset, order=1, setmin=None, setmax=None, valfilt=False):
    '''Dataset detreding using a constant value, a linear or polynomial fit.

    cf. :meth:`~geophpy.dataset.DataSet.detrend`

    '''

    # Ignoring data out of the range [setmin, setmax] ##########################
    dstmp = dataset.copy()
    dstmp.threshold(setmin=setmin, setmax=setmax, setnan=True, valfilt=valfilt)

    # Filtering ungridded values ###############################################
    if valfilt or dataset.data.z_image is None:
        values = dstmp.data.values
        profiles = genop.arrange_to_profile(values)

        values_corr = []
        pts_corr = []

        for prof in profiles:

            # Retrieving profile's values
            x = [pts[0] for pts in prof]
            y = [pts[1] for pts in prof]
            z = [pts[2] for pts in prof]
            x = np.asarray(x)
            y =  np.asarray(y)
            z =  np.asarray(z)

            # Ditance along profile
            x0 = x[0]
            y0 = y[0]
            dist = np.sqrt( (x-x0)**2 + (y-y0)**2 )

            # Least squares polynomial fit
            ## Original code was classic
            ## zfit = np.polyval(np.polyfit(dist, z, deg=order), dist)
            ## But as Numpy's documentation recommands using
            ## "The Polynomial.fit class method [...] for new code as it is more stable numerically."
            ## it was switched to using the Polynomial class's fit method:
            ## >> p = polynomial.fit(x, y, deg)
            ## >> yfit = p(x)
            zfit = npPolynomial.fit(dist, z, order)(dist)
            zcorr = z - zfit

            # Zipping results together
            pts_corr =  [list(a) for a in zip(x, y, zcorr)]
            values_corr.extend(pts_corr)
    
        # Storing results
        dataset.data.values = np.array(values_corr)

    # Filtering gridded values #################################################
    elif not valfilt and dataset.data.z_image is not None:
        zimg = dataset.data.z_image
        nl, nc = zimg.shape
        cols = range(nc)

        Z = dstmp.data.z_image
        zcorr = Z.copy()
        X, Y = dataset.get_xygrid()

        for col in cols:

            # Retrieving profile's values
            x = X[:,col]
            y = Y[:,col] 
            z = Z[:,col]

            x0 = x[0]
            y0 = y[0]
            dist = np.sqrt( (x-x0)**2 + (y-y0)**2 )

            # Least squares polynomial fit
            zfit = npPolynomial.fit(dist, z, order)(dist)
            zcorr[:,col] = z - zfit

        # Storing results
        dataset.data.z_image = zcorr

    return dataset


def destripecon(dataset, Nprof=0, setmin=None, setmax=None, method='additive', reference='mean', config='mono', valfilt=False):
    '''Destripe dataset using a constant value.

    cf. :meth:`~geophpy.dataset.DataSet.destripecon`

    '''

    # Ignoring data out of the range [setmin, setmax] ##########################
    dstmp = dataset.copy()
    dstmp.threshold(setmin=setmin, setmax=setmax, setnan=True, valfilt=valfilt)

    # Filter ungridded values ##################################################
    if valfilt or dataset.data.z_image is None:
        values = dstmp.data.values
        profiles = genop.arrange_to_profile(values)

        # Statistics for each profile ######################################
        m_i, sig_i, med_i = [], [], []
        q25_i, q75_i, iqr_i = [], [], []

        for prof in profiles:
            z = [pts[2] for pts in prof]

            # Mean and standard deviation
            m_i.append(np.nanmean(z))
            sig_i.append(np.nanstd(z))

            # Median and InterQuartile Range
            med_i.append(np.nanmedian(z))
            q25, q75 = np.nanpercentile(z, [25,75])
            iqr = q75 - q25

            q25_i.append(q25)
            q75_i.append(q75)
            iqr_i.append(iqr)

        # References values computation ########################################
        # Zero-mean (zero-median) profiles
        if Nprof == 0:
            m_d   = 0
            sig_d = 1

            med_d    = 0
            iqr_d    = 1

        # Global mean and std dev, median and IQR of the dataset
        elif Nprof == 'all':
            Z = [pts[2] for prof in profiles for pts in prof]

            m_d   = np.nanmean(Z)
            sig_d = np.nanstd(Z)

            med_d    = np.nanmedian(Z)
            q25_d, q75_d = np.nanpercentile(Z,[25,75])
            iqr_d    = q75_d - q25_d

        # References for Nprof neighboring profile
        else:
            for i, prof in enumerate(profiles):
                #Nprof
                pass
            
                
            pass

        # Rescaling profiles ###################################################
        zcorr = []
        
        ### TODO add 'multiplicative' for ungridded values
        if method=='additive':
            # Matching mean and standard deviation ###################
            if reference.lower()=='mean':
                # Mono sensor
                if config.lower()=='mono':
                    for i, prof in enumerate(profiles):
                        zcorr.append([pts[2]- m_i[i] + m_d for pts in prof])

                # Multi sensors
                elif config.lower()=='multi':    
                    for i, prof in enumerate(profiles):
                        zcorr.append([(pts[2] - m_i[i])*(sig_d[i]/sig_i[i]) + m_d for pts in prof])
                    
            # Matching median and iterquartile range #################
            if reference.lower()=='median':
                # Mono sensor
                if config.lower()=='mono':
                    for i, prof in enumerate(profiles):
                        zcorr.append([pts[2]- med_i[i] + med_d for pts in prof])

                # Multi sensors
                elif config.lower()=='multi':
                    for i, prof in enumerate(profiles):
                        zcorr.append([(pts[2] - med_i[i])*(iqr_d[i]/iqr_i[i]) + med_d for pts in prof])

        
        # Re-arranging profile in a list of points #############################
        values_corr = []
        pts_corr = []
        ###TODO enhance this implemenation if possible
        ## 
        for i, prof in enumerate(profiles):
            for j, pts in enumerate(prof):
                 pts_corr = [pts[0], pts[1], zcorr[i][j]]
                 #pts_corr = list(*[pts[0], pts[1], zcorr[i], pts[3:]])  # ensure no nested list from pts[3:]
                 #pts_corr = [element for element in pts_corr]  # ensure no nested list from pts[3:]
    
                 values_corr.append(pts_corr)
    
        dataset.data.values = np.array(values_corr)        

    # Filter zimage ############################################################
    elif not valfilt and dataset.data.z_image is not None:
        zimg = dataset.data.z_image
        nl, nc = zimg.shape
        cols = range(nc)

        # Statistics for each profile ##########################################
        Z = dstmp.data.z_image
        
        # Mean and standard deviation
        m_i = np.nanmean(Z, axis=0, keepdims=True)
        sig_i = np.nanstd(Z, axis=0, keepdims=True)

        # Median and InterQuartile Range
        med_i = np.nanmedian(Z, axis=0, keepdims=True)
        q25_i, q75_i = np.nanpercentile(Z, [25,75], axis=0, keepdims=True)
        iqr_i = q75_i - q25_i

        # References values computation ########################################
        # Zero-mean (zero-median) profiles
        if Nprof == 0:
            m_d   = 0
            sig_d = 1

            med_d    = 0
            iqr_d    = 1

        # Global mean and std dev, median and IQR of the dataset
        elif Nprof == 'all':
            m_d   = np.nanmean(Z)
            sig_d = np.nanstd(Z)

            med_d    = np.nanmedian(Z)
            q25_d, q75_d = np.nanpercentile(Z,[25,75])
            iqr_d    = q75_d - q25_d

        # References for Nprof neighboring profile
        else:
            # Allocation
            m_d   = np.zeros(m_i.shape)
            sig_d = np.zeros(sig_i.shape)

            med_d   = np.zeros(med_i.shape)
            iqr_d = np.zeros(iqr_i.shape)

            # Computation
            for col in cols:
                # A Centered scheme is used for computation
                # example Nprof=6 and center profile: #=(cpy)
                #            Nprof
                #        <----------->
                # col -nx              col +nx
                #        o - - # - - o 
                #        - - - # - - -  
                #        - - - # - - -  
                #        - - - # - - -   
                #        o - - # - - o
                # col -nx              col +nx

                # profiles index
                # ...TBD... because of the centered scheme, less profiles are used at the edges, change that ?
                idL = max(0, col-Nprof)  # left col index
                idR = min(nc-1, col+Nprof)  # right col index

                # Mean and standard deviation
                m_d[0,col] = np.nanmean(Z[:,idL:idR])
                sig_d[0,col] = np.nanstd(Z[:,idL:idR])

                # Median and InterQuartile Range
                med_d[0,col] = np.nanmedian(Z[:,idL:idR])
                q25, q75     = np.nanpercentile(Z[:,idL:idR],[25,75])
                iqr_d[0,col] = q75 - q25

        # Rescaling profiles ###################################################
        if method=='additive':
            ### ------------------------------------------------------
            # Matching mean and standard deviation ###################
            if reference.lower()=='mean':
                # Mono sensor
                if config.lower()=='mono':
                    zcorr = zimg - m_i + m_d

                # Multi sensors
                elif config.lower()=='multi':
                    zcorr = (zimg - m_i)*(sig_d/sig_i) + m_d
                    
            # Matching median and iterquartile range #################
            if reference.lower()=='median':
                # Mono sensor
                if config.lower()=='mono':
                    zcorr = zimg - med_i + med_d

                # Multi sensors
                elif config.lower()=='multi':
                    zcorr = (zimg - med_i)*(iqr_d/iqr_i) + med_d

            dataset.data.z_image = zcorr
            ### ------------------------------------------------------
            
            #zimg -= m_i
            #zimg += m_d
         
        elif method=='multiplicative':
            ### ------------------------------------------------------
            # Matching mean and standard deviation ###################
            if reference.lower()=='mean':
                # Mono sensor
                if config.lower()=='mono':
                    zcorr = zimg * (m_d / m_i)
                    
                # Multi sensor
                elif config.lower()=='multi':
                    zcorr = zimg * (sig_d/sig_i) * (m_d/m_i)
                    
            # Matching median and iterquartile range #################
            if reference.lower()=='median':
                # Mono sensor
                if config.lower()=='mono':
                    zcorr = zimg * (med_d/med_i)
                    
                # Multi sensor
                elif config.lower()=='multi':
                    zcorr = zimg *(iqr_d/iqr_i) * (med_d/med_i)

            dataset.data.z_image = zcorr
            ### ------------------------------------------------------
                    
                    
            #zimg *= m_d
            #zimg /= m_i
        else:
           # Undefined destriping method ###############################
           # ...TBD... raise an error here !
           pass


def destripecub(dataset, Nprof=0, setmin=None, setmax=None, Ndeg=3, valfilt=False):
    ''' Destripe dataset using a polynomial fit.

    cf. :meth:`~geophpy.dataset.DataSet.destripecub`

    '''

    # Ignoring data out of the range [setmin, setmax] ##########################
    dstmp = dataset.copy()
    dstmp.threshold(setmin=setmin, setmax=setmax, setnan=True, valfilt=valfilt)

    # Filtering ungridded values ###############################################
    if valfilt:
        values = dstmp.data.values
        profiles = genop.arrange_to_profile(values)

        # Polynomial fit for each profile ######################################
        
        pfit  = []  # initialization of polynomial coeff
        for prof in profiles:

            # Retrieving profile's values
            x = np.asarray([pts[0] for pts in prof])
            y = np.asarray([pts[1] for pts in prof])
            z = np.asarray([pts[2] for pts in prof])

            # Ditance along profile
            x0, y0 = x[0], y[0]
            dist = np.sqrt( (x-x0)**2 + (y-y0)**2 )

            # Least squares polynomial fit roots
            pfit.append(npPolynomial.fit(dist, z, Ndeg).roots())

        # References values computation ########################################
        pfit = np.asarray(pfit).flatten().reshape((-1, Ndeg))

        # Polynomial coefficients of each profile
        if Nprof == 0:
            pref = pfit

        # Mean polynomial coefficients
        elif Nprof =='all':
            pref = np.nanmean(pfit, axis=0, keepdims=True)
            pref = np.repeat(pref, len(profiles), axis=0)

        # Nprof-mean polynomial coefficients
        else:
            # Padding with 1st and last profile to compute centered mean on Nprof profiles
            init_pad = np.array([pfit[0],]*Nprof)
            final_pad =  np.array([pfit[-1],]*Nprof)
            pfit_pad = np.vstack((init_pad, pfit, final_pad))

            # Nprof-mean coefficients
        
            # Normal array index
            #   2xNprof+1
            # <----------->
            #  Nprof  Nprof
            # <---->i<---->
            # o - - # - - o
            # - - - # - - -
            # - - - # - - -
            # - - - # - - -
            # o - - # - - o
            #
            # Padded Array index
            # 0     i     i+2xNprof +1
            # <-----#----->
            # o - - # - - o
        
            pref = np.array([]).reshape((0, Ndeg))
            for i, p in enumerate(pfit):
                pNprof = pfit_pad[i:i+2*Nprof+1]
                pmean = np.nanmean(pNprof, axis=0, keepdims=True)
                pref = np.vstack((pref, pmean))

        # Rescaling profiles ###################################################
        values_corr = []
        pts_corr = []

        for i, prof in enumerate(profiles):
            x = np.asarray([pts[0] for pts in prof])
            y = np.asarray([pts[1] for pts in prof])
            z = np.asarray([pts[2] for pts in prof])

            # Ditance along profile
            x0, y0 = x[0], y[0]
            dist = np.sqrt( (x-x0)**2 + (y-y0)**2 )

            zref = npPolynomial(pref[i])(dist)
            zcorr = z - zref

            # Zipping results together
            pts_corr =  [list(a) for a in zip(x, y, zcorr)]
            values_corr.extend(pts_corr)

        # Storing results ######################################################
        dataset.data.values = np.array(values_corr)

    # Filtering gridded values ################################################
    else:
        zimg   = dataset.data.z_image
        nl, nc = zimg.shape
        cols   = range(nc)
        #y      = getgrid_ycoord(dataset)
        _, y   = dataset.get_xygrid()

        # Compute the polynomial coefs for each profile ################
        Z    = dstmp.data.z_image
        ZPOL = np.polyfit(y[:,0],Z,Ndeg)

        # Compute the polynomial reference #############################
        if (Nprof == 0):
            POLR = np.nanmean(ZPOL, axis=1, keepdims=True)
        else:
            POLR = np.zeros(ZPOL.shape)
            kp2  = Nprof // 2
            for jc in cols:
                jc1 = max(0,jc-kp2)
                jc2 = min(zimg.shape[1]-1,jc+kp2)
                POLR[:,jc] = np.nanmean(ZPOL[:,jc1:jc2], axis=1, keepdims=True)[:,0]

        # Rescale the profiles #########################################
        for d in range(Ndeg):
            zimg -= np.array([ZPOL[d+1]])*y**(d+1)
        if (Nprof != 1):
            zimg -= ZPOL[0]
            for d in range(Ndeg+1):
                zimg += np.array([POLR[d]])*y**d
 

def getregtrendmethodlist():
    '''
    cf. dataset.py
    '''
    return regtrendmethod_list


def getregtrendcomplist():
    '''
    cf. dataset.py
    '''
    return regtrendcomp_list


def regtrend(dataset, nx=3, ny=3, method="relative", component="local", loctrendout=None, regtrendout=None, valfilt=False):
   '''
   cf. dataset.py
   '''
   if (valfilt):
      # Filter values ...TBD... ######################################
      pass
   else:
      # Filter zimage ################################################
      zimg = dataset.data.z_image
      cols = range(zimg.shape[1])
      ligs = range(zimg.shape[0])
      nx2  = nx//2
      ny2  = ny//2
      znew = zimg * 0.

      # Compute the mean of all data #################################
      zmoy = np.nanmean(zimg)

      # Compute the mean in each window ##############################
      for jl in ligs:
         jl1 = max(0, jl - nx2)            # ...TBD... -1 ?
         jl2 = min(max(ligs), jl + nx2)    # ...TBD... -1 ?
         for jc in cols:
            jc1 = max(0, jc - ny2)         # ...TBD... -1 ?
            jc2 = min(max(cols), jc + ny2) # ...TBD... -1 ?
            zloc = np.nanmean(zimg[jl1:jl2,jc1:jc2])
            if (component == "local"):
               if (method == "relative"):
                  znew[jl,jc] = zimg[jl,jc] * zmoy / zloc
               elif (method == "absolute"):
                  znew[jl,jc] = zimg[jl,jc] - zloc
               else:
                  # Undefined method #################################
                  # ...TBD... raise an error here !
                  pass
            elif (component == "regional"):
               znew[jl,jc] = zloc
            else:
               # Undefined component #################################
               # ...TBD... raise an error here !
               pass

      # Write result to input dataset ################################
      zimg[:,:] = znew


def _wallisoperator(cval, winval, setgain, targmean, targstdev, limitstdev, edgefactor):
    r'''
    Computes the Wallis operator (brigthess contrast enhancement) for the
    central value of a given vector.

    Parameters
    ----------

    :cval:  current window center value [f(x,y)]

    :winval: current window values

    :setgain: amplification factor for contrast [A]

    :targmean: target mean brightness level (typically between {0-255}) [m_d]

    :targstdev: target brightness standard deviation [\sigma_d]

    :limitstdev: maximal allowed window standard deviation (prevent infinitly high gain value if data are dispersed)

    :edgefactor: brightness forcing factor (controls ratio of edge to background intensities) [\alpha]

    Returns:
    
    :g_xy: Wallis operator at the current window center location [g(x,y)]

    Notes
    -----
    The Wallis operator is defined as:
    
    :math:`\frac{A \sigma_d}{A \sigma_{(x, y)} + \sigma_d} [f_{(x, y)} - m_{(x, y)}] + \alpha m_d + (1 - \alpha)m_{(x, y)}`

    where: :math:`A` is the amplification factor for contrast;
    :math:`\sigma_d` is the target standard deviation;
    :math:`\sigma_{(x, y)}` is the standard deviation in the current window;
    :math:`f_{(x, y)}` is the center pixel of the current window;
    :math:`m_{(x, y)}` is the mean of the current window;
    :math:`\alpha` is the edge factor (controlling portion of the observed mean, and brightness locally to reduce or increase the total range);
    :math:`m_d` is the target mean.

    '''

    # ...TBD... to homogeneize through the package
    #
    # arr = np.asarray(arr)  #  ensures input is a numpy array
    # K = arr.size
    # 

    # Wallis constants
    A = setgain           # amplification factor
    m_d = targmean        # the target mean
    sig_d = targstdev     # target standard deviation
    alpha = edgefactor    # edgefactor
    sig_lim = limitstdev  # maximum standard deviation value

    # Window statistics
    # winval                       # current window values
    f_xy = cval                    # window center pixel
    m_xy = np.nanmean(winval)      # window mean 
    sig_xy = np.nanstd(winval)     # window strd. dev.
    sig_xy = min(sig_xy, sig_lim)  # limitation on max strd. dev.

    # Wallis operator
    g_xy = A*sig_d / (A * sig_xy + sig_d) * (f_xy - m_xy) + alpha*m_d + (1-alpha)*m_xy

    return g_xy


def wallisfilt(dataset, nx=11, ny=11, targmean=125, targstdev=50, setgain=8, limitstdev=25, edgefactor=0.1, valfilt=False):
    '''
    cf.  :meth:`~geophpy.dataset.DataSet.wallisfilt`
    '''
    # Filter values ...TBD... ######################################
    if (valfilt):
       
       pass

    # Filter zimage ##################################################
    else:    
        # Map/Image properties #######################################
        zimg = dataset.data.z_image
        zmin, zmax = dataset.histo_getlimits()
        nl, nc = zimg.shape

        # Converting values to brightness ############################
        nblvl = 256  # number of levels
        zlvl = array_to_level(zimg, nblvl=nblvl, valmin=zmin, valmax=zmax)

        # ...TBD... ##################################################
        # Replacement of the mean and standard deviation by the median
        # (M a for m a and local median for if(i, j)) and interquartile
        # distance (Qd for o a and local interquartile for a(i, j)),
        # respectively, was suggested as a solution. The Huang-Yang-Tang
        # [14] running median algorithm was employed for computational
        # efficiency.

        # Filter constantes (names as in Scollar, 1990) ##############
        A, sig_d, m_d = setgain, targstdev, targmean
        alpha, sig_lim = edgefactor, limitstdev

        # 2D Sliding Window ##########################################
        ####
        # ...TBD... 2D sliding window with  more Pythonic ?
        # ...TBD... scipy.ndimage.generic_filter ?
        ####
        # The SW is centered on the pixel so it has (ny) pixels above
        # and under the center pixel (#), and (nx) pixels to its left
        # and to its right.
        #
        # example for SW with nx=3, ny=2 and center pixel: #=(cpx, cpy)
        #              lx
        #         <----------->
        # cpx -nx              cpx +nx
        # cpy +ny              cpy +ny
        #    ^    o - - - - - o 
        #    |    - - - - - - -  
        # ly |    - - - # - - -  
        #    |    - - - - - - -   
        #    v    o - - - - - o
        # cpx -nx              cpx +nx
        # cpy +ny              cpy +ny
        #

        # Sliding Window dimension
        lx = 2*nx + 1  # total window length
        ly = 2*ny + 1  # total window height
        g_xy = np.empty(zimg.shape)

        # Sweeping rows & columns preventing out of range index
        # using comparison to nl and nc
        for cpy in range(nl):
            sw_top = max(cpy - ny, 0)  # SW top index
            sw_bot = min(cpy + ny, nl-1)  # SW bottom index
            swy = np.arange(sw_top,sw_bot+1).reshape((-1,1))  # SW rows index
          
            for cpx in range(nc):
                # Current SW index bounds
                sw_left = max(cpx - nx, 0)  # SW left index
                sw_right = min(cpx + nx, nc-1) # SW right index
                swx = np.arange(sw_left,sw_right+1).reshape((1,-1))  # SW cols index

                # Current SW index (broadcating index vectors)
                swi = swy*np.ones(swx.shape) # SW matix rows index
                swj = swx*np.ones(swy.shape) # SW matix cols index
                swi = np.asarray(swi.reshape((1,-1)), dtype=np.int16)
                swj = np.asarray(swj.reshape((1,-1)), dtype=np.int16)

                # Current SW Wallis operator
                win_xy = zlvl[swi,swj]   # current window
                f_xy = zlvl[cpy,cpx]    # current window center
                if ~np.isnan(f_xy):
                    g_xy[cpy,cpx] = _wallisoperator(f_xy, win_xy, A,
                                                   m_d, sig_d, sig_lim, alpha)
                else:
                    g_xy[cpy,cpx] = f_xy
  
        # Converting brightness back to values #######################
        # ...TDB... raise warniing when comapring with nan ?
        # ...TDB... using nan ignoring technic/mask ?
        g_xy[np.where(g_xy<0)] = 0
        g_xy[np.where(g_xy>nblvl-1)] = nblvl-1
        zfilt = level_to_array(g_xy, zmin, zmax, nblvl=nblvl)

        # Writting result to input dataset ###########################
        zimg[:,:] = zfilt


def ploughfilt(dataset, apod=0, azimuth=0, cutoff=100, width=2, valfilt=False):
    '''
    cf. :meth:`~geophpy.dataset.DataSet.ploughfilt`
    '''

    # Filter values ...TBD... ##################################################
    if (valfilt):
        pass

    # Filter zimage ############################################################
    else:
        zimg = dataset.data.z_image

        # Apodization before FT
        if (apod > 0):
            apodisation2d(zimg, apod)

        # Fourier Transform computation
        znan = np.copy(zimg)
        nan_idx = np.asarray([], dtype=int)  # index of NaNs in the original dataset
        zfill = genop.fillnanvalues(znan, indexout=nan_idx)  # Filled dataset

        zmean = np.nanmean(zimg)
        zfill = zfill-zmean   # De-meaning

        ZTF = np.fft.fft2(zfill)  # Frequency domain

        # Directional filter design in the frequency domain
        Filt = _gaussian_lowpass_dir_filter(ZTF.shape, cutoff, azimuth, width)

        # Data Filtering and transformation back to spatial domain
        ZTF_filt = ZTF*Filt  # Applying filter

        zfilt = np.fft.ifft2(ZTF_filt)  # Spatial domain
        zfilt = np.real(zfilt) + zmean  # Re-meaning

        # Writting result to input dataset ###########################
        zfilt[nan_idx] = np.nan  # unfilled dataset
        zimg[:,:] = zfilt

    return dataset


def _gaussian_lowpass_dir_filter(shape, fc=None, azimuth=90, n=2):
    '''
    Two-dimensional gaussian low-pass directional filter.

    Parameters
    ----------
    shape : tuple
        Filter shape.
    
    fc : ndarray
        Input array to filter.

    n : integer
        Gaussian filter cutoff frequency.

    azimuth : scalar
        Directional filter azimuth angle in degree.

    Returns
    -------
    gaussian_lowpass_dir_filter : ndarray

    ...Notes, citation...
    
    '''

    azimuth = np.deg2rad(azimuth)
    cosAz = np.cos(azimuth)
    sinAz = np.sin(azimuth)

    # Creating x and y coordinates matrix ######################################
    # using the same order as in numpy.fft.fftfreq
    # (applying the filter is then a simple multiplication whith fft):
    # coord = [0, 1, ...,   n/2-1,     -n/2, ..., -1] if n is even
    # coord = [0, 1, ..., (n-1)/2, -(n-1)/2, ..., -1] if n is odd)

    # x-coordinate vector
    ny, nx = shape
    Nx = (nx-1)//2 + 1
    Ny = (ny-1)//2 + 1

    x = np.empty(nx, int)
    xpos = np.arange(0, Nx, dtype=int)
    x[:Nx] = xpos
    xneg = np.arange(-(nx//2), 0, dtype=int)
    x[Nx:] = xneg

    # y-coordinate vector
    y = np.empty(ny, int)
    ypos = np.arange(0, Ny, dtype=int)
    y[:Ny] = ypos
    yneg = np.arange(-(ny//2), 0, dtype=int)
    y[Ny:] = yneg

    # x,y-coordinate matrix
    x, y = np.meshgrid(x, y)
    y  = np.flipud(y)
    #x = np.fft.fftshift(x)
    #y = np.fft.fftshift(np.flipud(y))
    
    # Filter design ############################################################
    # Deviation angle to the filter azimuth
    u = x*cosAz - y*sinAz
    v = x*sinAz + y*cosAz
    r = np.sqrt(u**2 + v**2)
    phi = np.arctan2(v, u)
    phi[u==0] = np.pi/2

    # Gaussian low-pass directional filter
    gamma = np.abs(np.tan(phi))**n
    gamma[np.abs(phi) <= np.pi/4] = 1

    if (fc is None) or (fc==0):
        GausFilt = 1 # No Gaussian low-pass filter
    else:
        GausFilt = np.exp(-(r/fc)**2) 

    DirFilt = (1 - np.exp(-r**2/gamma))

    filt = GausFilt * DirFilt

    return filt
