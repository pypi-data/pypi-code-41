#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 18:02:06 2019

@author: vbokharaie

This module includes methods of fmri_dataset class related to bbox plots.

"""

#%%
def bbox_3d(img3):
    """calculates a minimal rectangular cube which includes all the non-zero values of mask.
    This is known as a bbox.
    Parameters
    ----------
    img3: 'numpy.ndarray', (d1, d2, d3)
        the mask including ones and zeros
    Returns
    -------
    mask_bbox: 'numpy.ndarray', (e1, e2, e3)
    """
    import numpy as np
    a_t = np.where(img3 != 0)
    bbox = np.min(a_t[0]), np.max(a_t[0])+1, np.min(a_t[1]), \
            np.max(a_t[1])+1, np.min(a_t[2]), np.max(a_t[2])+1
    mask_bbox = img3[bbox[0]:bbox[1], bbox[2]:bbox[3], bbox[4]:bbox[5]]
    return mask_bbox

#%%
def bbox_mean(mask_bbox, data):
    """Mean value of time-series in each non-zero cell in bbox mask
    Parameters
    ----------
    mask_bbox: 'numpy.ndarray', (e1, e2, e3)
    data: 'numpy.ndarray', (N_voxels, N_time_steps)
    Returns
    -------
    bbox_mean: 'numpy.ndarray', (e1, e2, e3)
    """
    import numpy as np
    bbox_mean = np.zeros(np.shape(mask_bbox))
    bbox_mean[mask_bbox == 1] = np.mean(data, axis=0)
    return bbox_mean

#%%
def bbox_3d_seq(bbox_3d):
    """replaces non-zeros values with a sequential list of integers.
    Only used in debugging. Not needed for normal operations.
    This is known as a bbox.
    Parameters
    ----------
    bbox_3d: 'numpy.ndarray', (e1, e2, e3)

    Returns
    -------
    bbox_seq: 'numpy.ndarray', (e1, e2, e3)
    """
    import numpy as np
    [n1, n2, n3] = bbox_3d.shape
    bbox_seq = np.zeros(bbox_3d.shape, dtype=int)
    vox_count = 1
    for cc1 in np.arange(n1):
        for cc2 in np.arange(n2):
            for cc3 in np.arange(n3):
                if bbox_3d[cc1, cc2, cc3,] > 0:
                    bbox_seq[cc1, cc2, cc3,] = vox_count
                    vox_count = vox_count+1

    return bbox_seq
