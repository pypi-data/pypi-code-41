# -*- coding: utf-8 -*-
"""
Funktionen für 
"""

import numpy as np
import scipy.signal as dsp
import math
from PyDynamic.misc import impinvar
import sys
import warnings


def Gp2gt (num, den, fs, tmax):
    
    
    '''
    nutzt Matlabs 'Impulse invariance method', um aus dem Analogfilter 
    ein Digialfilter mit der Abtastfrequent fs zu generieren
    also: gt korrespondiert exakt mit der abgetasteten 
    Impulsantwort des Analogsystems
    
    tmax ist die berechnete LÃ¤nge der IR
    '''    
    
    warnings.filterwarnings("ignore")
    a_dig, b_dig    = impinvar(num, den, fs); #Koeff Dig. Filter
    
    t0              = 1/fs
    t               = np.arange(1, tmax, t0)
    N               = np.shape(t)[0]-1
    
    xin             = np.zeros(N+1)
    xin[0]          = 1
    
    y               = dsp.lfilter(a_dig, b_dig, xin)
    gt              =y[0:N] * fs
    
    return t, gt

def GroupD( f, Gf ):
    #Berechnet die Gruppenlaufzeit durch numerische Differentiation

    df  = np.diff(f)
    y=-1/(2*math.pi) * np.diff( np.unwrap(np.angle(Gf)))/df
    y=np.append(y, y[-1])
    return y

def besself2(N):
    #gibt Besselkoeffizienten dür eine (normierte) Gruppenlaufzei vom tg(0)=1
    
    df      = 1e-8
    f       = np.array([0, df])
    a,b     = dsp.bessel(N, 1, analog=True)
    
    Gf      = dsp.freqs(a,b, 2* math.pi *f)[1]
    tg      = np.diff( np.angle(Gf))[0] / (-2 * math.pi * df)
    a,b     = dsp.bessel(N, 1*tg, analog = True)
    
    return a,b
    
    
def besself3(N, Wp):
    #gibt Besselkoeffizienten für 3dB-Kreisfrequenz von Wp zurück
    
    
    df      = 1e-8
    f       = np.array([0, df])
    a,b     = dsp.bessel(N, 1, analog=True)
    
    Gf      = dsp.freqs(a,b, 2* math.pi *f)[1]
    tg      = np.diff( np.angle(Gf))[0] / (-2 * math.pi * df)
    a,b     = dsp.bessel(N, 1*tg, analog = True)
    
    f0      = 0.0001
    f       = np.arange(0,1,f0) #3db-grenzfrequenz ligt sicher in dem Bereich
    Gf      = dsp.freqs(a,b, 2*math.pi*f)[1]
    
    ind     = np.nonzero(np.abs(Gf) >= 1/math.sqrt(2))[0]
    
    Wg      = f[ind]*2*math.pi
    a,b     = dsp.bessel(N, 1*tg/Wg*Wp)
    
    return a,b

def besself4(N, amax, Wp):
    #Wp: Bandpassecken
    #aamx: bandpassloss in dB
    
    if (amax>12):
        sys.exit('Error: aMax muss kleiner als 12 dB sein')
    
    
     
    df      = 1e-8
    f       = np.array([0, df])
    a,b     = dsp.bessel(N, 1, analog=True)
    
    Gf      = dsp.freqs(a,b, 2* math.pi *f)[1]
    tg      = np.diff( np.angle(Gf))[0] / (-2 * math.pi * df)
    a,b     = dsp.bessel(N, 1*tg, analog = True)
    f0      = 0.0001
    f       = np.arange(0,2,f0)
    loss    = -20*np.log10(np.abs( dsp.freqs(a, b, 2*math.pi*f)[1] ) );
    
    ind     = np.nonzero( loss >= amax)[0][0];
    Wg      = f[ind]*2*math.pi
    
    [a,b]   = dsp.bessel(N, 1*tg*Wp/Wg )
        
    return a,b
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    