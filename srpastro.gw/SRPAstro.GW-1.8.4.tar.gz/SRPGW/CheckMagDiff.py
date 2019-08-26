""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.0.0
Author  : Stefano Covino
Date    : 21/12/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : Score

Remarks :

History : (21/12/2017) First version.
"""

import numpy as np



def CheckMagDiff (m1, em1, m2, em2, th, mode='all'):
    err = np.where( ((em1 < 90) & (em2 < 90)), np.sqrt(em1**2+em2**2),
                np.where( ((em1 > 90) & (em2 < 90)), em2,
                        np.where( ((em1 < 90) & (em2 > 90) ), em1, 99.)))
    #
    if mode == 'all':
        return np.where((m1<90) & (m2<90), abs(m1-m2) >= th+err, False)
    elif mode == 'high':
        return np.where((m1<90) & (m2<90), m1-m2 >= th+err, False)
    elif mode == 'low':
        return np.where((m1<90) & (m2<90), m1-m2 <= th+err, False)

