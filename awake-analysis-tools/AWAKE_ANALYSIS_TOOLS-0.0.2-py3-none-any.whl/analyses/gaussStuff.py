#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 14:37:47 2017

@author: sgess
"""
import numpy as np
from scipy.optimize import curve_fit

''' Define Gaussian Shape '''
def gaussian(x, amp, cen, wid, off):

    return amp * np.exp(-(x-cen)**2 /(2*wid**2)) + off

''' Define Gaussian Shape plus slope'''
def gaussSlope(x, amp, cen, wid, off, slope):

    return amp * np.exp(-(x-cen)**2 /(2*wid**2)) + off + slope*x

''' Fit Gaussian with offset '''
def gaussFit(axis,prof,guess,weights=0):
    
    if np.sum(weights) > 0:
        weights = weights
    else:
        weights = np.ones(len(axis))
            
    
    try:
        result,pcov = curve_fit(gaussian,axis,prof,guess,sigma=weights,absolute_sigma=False)
        result[2] = abs(result[2])
        fit = gaussian(axis, *result)
    except:
        #print('Failed to fit in '+axis+'-direction')
        result = [0,0,0,0]
        pcov = np.zeros((4,4))
        fit = np.zeros(np.shape(axis))
        
    return result, fit, pcov
    
''' Fit Gaussian with slope '''
def gaussFitSlope(axis,prof,guess,weights=0):
    
    if np.sum(weights) > 0:
        weights = weights
    else:
        weights = np.ones(len(axis))
    
    try:
        result,pcov = curve_fit(gaussSlope,axis,prof,guess,sigma=weights,absolute_sigma=False)
        result[2] = abs(result[2])
        fit = gaussSlope(axis, *result)
    except:
        #print('Failed to fit in '+axis+'-direction')
        result = [0,0,0,0]
        pcov = np.zeros((4,4))
        fit = np.zeros(np.shape(axis))
        
    return result, fit, pcov
