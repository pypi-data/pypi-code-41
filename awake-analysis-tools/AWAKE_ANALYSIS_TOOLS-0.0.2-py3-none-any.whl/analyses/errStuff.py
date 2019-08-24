#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 01:19:51 2018

@author: awakeop
"""

import numpy as np
from scipy.optimize import curve_fit
from scipy.integrate import cumtrapz


''' Define Gaussian Shape '''
def gaussian(x, amp, cen, wid, off):

    return amp * np.exp(-(x-cen)**2 /(2*wid**2)) + off


def erf(x,amp,cen,wid,off,off2):
    res = cumtrapz(gaussian(x, amp, cen, wid, off))+off2
    return cumtrapz(gaussian(x, amp, cen, wid, off))+off2


''' Fit Gaussian. Not called by default '''
def gaussFit(axis,prof,guess):
    
    try:
        result,pcov = curve_fit(gaussian,axis,prof,guess)
        result[2] = abs(result[2])
        fit = gaussian(axis, *result)
    except:
        #print('Failed to fit in '+axis+'-direction')
        result = [0,0,0,0]
        fit = np.zeros(np.shape(axis))
        
    return result, fit

def errFit(axis, prof, guess):
    try:
        result,pcov = curve_fit(erf,axis,prof,guess)
        result[2] = abs(result[2])
        fit = erf(axis, *result)
    except:
        #print('Failed to fit in '+axis+'-direction')
        result = [0,0,0,0]
        fit = np.zeros(np.shape(axis))
        
    return result, fit