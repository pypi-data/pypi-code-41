#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 14:21:19 2017

@author: sgess
"""

import numpy as np
from scipy import signal

def findPeaks(fft):
    
    mx=np.array(signal.argrelmax(fft)).squeeze()
    mn=np.array(signal.argrelmin(fft)).squeeze()

    len_x = mx.size
    if not len_x:
        mx = 0
        len_x = 1
    if len_x == 1:
        mx = np.array([mx])
    len_n = mn.size
    if not len_n:
        mn = len(fft)-1
        len_n = 1
    if len_n == 1:
        mn = np.array([mn])
    
#    if not mx.size:
#        mx = 0
#    if not mn.size:
#        mn = len(fft)-1
#
#    if not mx.size:
#        len_x = 1
#        mx = np.array([mx])
#    else:
#        len_x = len(mx)
#    
#    if not mn.size:
#        len_n = 1
#        mn = np.array([mn])
#    else:
#        len_n = len(mn)
    
    if len_x < len_n:
        maxs = fft[mx]
        mins = fft[mn]

        lps = maxs - mins[0:-1]
        rps = maxs - mins[1:]

        return maxs, mins, lps, rps, mx, mn

    if len_x == len_n:
        if mx[0] > mn[0]:
            mn = np.append(mn,len(fft)-1)
        else:
            mn = np.insert(mn,0,0)
        
        maxs = fft[mx]
        mins = fft[mn]

        lps = maxs - mins[0:-1]
        rps = maxs - mins[1:]

        return maxs, mins, lps, rps, mx, mn
        
    if len_x > len_n:
        mn = np.append(mn,len(fft)-1)
        mn = np.insert(mn,0,0)
        
        maxs = fft[mx]
        mins = fft[mn]

        lps = maxs - mins[0:-1]
        rps = maxs - mins[1:]

        return maxs, mins, lps, rps, mx, mn
        
    print('You fucked up')
        
        


            
            
