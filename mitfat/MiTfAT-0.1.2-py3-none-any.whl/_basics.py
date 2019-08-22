#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 18:10:24 2019

@author: vbokharaie

This module includes methods of fmri_dataset class used as basic opeartions.
Such as nomralising, fixing anamolies, linear regression, etc.

"""

from mitfat import _Lib
__methods__ = [] # self is a DataStore
register_method = _Lib.register_method(__methods__)

#%%
@register_method
def calc_mean_segments(self):
    """Mean value of each time-segment in the time-series.

    Time-segments are automatically defined based on specified values of cutoff indices ot times.
    If they are not defined, there would be only one time-segment including all time-steps.

    Yields
    ------
    mean_segments : 'numpy.ndarray', (len_segments-1, num_voxels)
    """

    import numpy as np
    len_segments = len(self.indices_cutoff)
    if len_segments>2:
        mean_segments = np.empty([len_segments-1, self.num_voxels])
        for idx, ind in enumerate(self.indices_cutoff[:-1]):
            ind_next = self.indices_cutoff[idx+1]
            mean_segments[idx,:] = np.nanmean(self.data[ind:ind_next,:], axis=0)
        self.mean_segments = mean_segments
    else:
        self.mean_segments = self.data_mean


#%% Fix anomolies
# If there are overshoots or undershoots in the data,
# outside (mean +- 3*std), they are replaced with 'np.nan' values
@register_method
def fix_anomolies(self):
    """Fix overshoot and undershoots occasioanlly recorded by the fMRI scanners.

    Replaces any value outside +-3 SD range of signal MEAN with np.nan.

    Returns
    -------
    my_data : 'numpy.ndarray', np.shape(self.data)
    """

    from mitfat import flags
    my_data = self.data
    import numpy as np
    n_2 = np.shape(my_data)[1]
    for cc_ in np.arange(n_2):
        my_signal = my_data[:, cc_].copy()
        mean_signal = np.nanmean(my_signal)
        std_signal = np.nanstd(my_signal)
        ind_nan = []
        for idx, my_el in enumerate(my_signal):
            if my_el < mean_signal-3*std_signal:
                ind_nan.append(idx)
                my_signal[idx] = np.nan
            if my_el > mean_signal+3*std_signal:
                ind_nan.append(idx)
                my_signal[idx] = np.nan
        if ind_nan != []:
            if flags.if_verbose:
                print('-------------------------------------------------')
                print('For voxel', cc_,\
                      'the following Time-Steps (TS) turned to np.nan:')
            for el2 in ind_nan:
                np.set_printoptions(precision=2)
                if (not el2 == 0) and (not el2 == len(my_signal)-1):
                    val_curr = my_data[el2, cc_]
                    val_prev = my_data[el2-1, cc_]
                    val_next = my_data[el2+1, cc_]
                    val_mean_prev_next = (val_prev + val_next)/2
                    diff_pc = ((val_curr - val_mean_prev_next)/val_curr)*100
                    if flags.if_verbose:
                        print('TS', el2, \
                              '-> its value was ', "{0:0.2f}".format(diff_pc), \
                              '% more than mean of prev. and next TS')
                elif el2 == 0:
                    val_curr = my_data[el2, cc_]
                    val_next = my_data[el2+1, cc_]
                    diff_pc = ((val_curr - val_next)/val_next)*100
                    if flags.if_verbose:
                        print('TS', el2, \
                              '-> its value was ', "{0:0.2f}".format(diff_pc), \
                              '% different than the next TS.')
                elif el2 == len(my_signal)-1:
                    val_curr = my_data[el2, cc_]
                    val_prev = my_data[el2-1, cc_]
                    diff_pc = ((val_curr - val_prev)/val_prev)*100
                    if flags.if_verbose:
                        print('TS', el2, \
                              '-> its value was ', "{0:0.2f}".format(diff_pc), \
                              '% different than the previous TS.')
        my_data[:, cc_] = my_signal
    return my_data

#%%
@register_method
def impute(self):
    """Interpolates nan values in the time series.
    uses sklearn.impute.SimpleImputer

    Yields
    ------
    data: 'numpy.ndarray'
    """

    from sklearn.impute import SimpleImputer
    imp = SimpleImputer(strategy='mean')
    self.data = imp.fit_transform(self.data)
#%%
@register_method
def normalise(self):
    """Normalises the time-series.
    Divides all time-series in all voxel by their collective maximum value.

    Yields
    ------
    data_normalised : 'numpy.ndarray'
    data: 'numpy.ndarray'
    bbox_data_mean: 'numpy.ndarray'
    data_mean: 'numpy.ndarray'
    mean_segments : 'numpy.ndarray'
    """

    import numpy as np
    from mitfat._shapes import bbox_mean
    max_el = np.nanmax(self.data)
    self.data_normalised = self.data/max_el
    self.data = self.data_normalised
    self.bbox_data_mean = bbox_mean(self.bbox_mask, self.data_normalised)
    self.data_mean = np.nanmean(self.data_normalised, axis = 0)
    self.calc_mean_segments()

#%%
@register_method
def calc_lin_reg(self):
    """Calculates lineare regression for the time-series.
    Uses numpy.linalg.lstsq.

    Yields
    ------
    line_reg :  'numpy.ndarray', data.shape
    line_reg_slopes:    'numpy.ndarray', (num_voxels, num_segments)
    line_reg_biases:    'numpy.ndarray', (num_voxels, num_segments)
    """

    import numpy as np
    data = self.data
    ind_cutoff = self.indices_cutoff
    time_steps = self.time_steps
    time_steps_range = time_steps[-1]-time_steps[0]
    # makeing x and y values in the same range, so slopes are in the same range:
    data = data * time_steps_range
    num_voxels = self.num_voxels
    num_segments = len(self.cutoff_times)-1

    slopes = np.zeros([num_voxels, num_segments])
    biases = np.zeros([num_voxels, num_segments])
    data_2d_linearised = np.zeros(np.shape(data))

    for cc2 in np.arange(num_voxels):
        data_1d = data[:, cc2].copy()
#            data_1d_temp = np.ones(np.shape(data_1d))

        for cc4 in np.arange(num_segments):
            yy_ = data_1d[ind_cutoff[cc4]:ind_cutoff[cc4+1]+1]
            xx_ = time_steps[ind_cutoff[cc4]:ind_cutoff[cc4+1]+1]
            finite_y_mask = np.isfinite(yy_)
            y_clean = yy_[finite_y_mask]
            x_clean = xx_[finite_y_mask]
            aa_d = np.vstack([x_clean.T, np.ones(len(x_clean))]).T
            mm_d, cc_d = np.linalg.lstsq(aa_d, y_clean, rcond=None)[0]
            y_regressed = np.empty(np.shape(yy_))
            y_regressed[:] = np.NAN
            y_regressed[finite_y_mask] = mm_d*x_clean + cc_d
            angle = np.rad2deg(np.arctan2(y_regressed[-1] - y_regressed[0], xx_[-1] - xx_[0]))
            slopes[cc2, cc4] = angle
            biases[cc2, cc4] = cc_d

            data_1d[ind_cutoff[cc4]:ind_cutoff[cc4+1]+1] = y_regressed.flatten()
        data_2d_linearised[:, cc2] = data_1d
    self.line_reg = data_2d_linearised
    self.line_reg_slopes = slopes.T
    self.line_reg_biases = biases.T
