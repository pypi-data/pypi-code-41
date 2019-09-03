# -*- coding: utf-8 -*-
"""
Funktionen für 
"""

import numpy as np
import scipy.signal as dsp
import scipy.special
import math

import sys
import warnings


def Gp2gt (a, b, fs, tmax):
    
    
    '''
    nutzt 'Impulse invariance method', um aus dem Analogfilter 
    ein Digialfilter mit der Abtastfrequent fs zu generieren
    also: gt korrespondiert exakt mit der abgetasteten 
    Impulsantwort des Analogsystems
    
    tmax ist die berechnete LÃ¤nge der IR
    '''    
    
    warnings.filterwarnings("ignore")
    a_dig, b_dig    = impinvar(a, b, fs); #Koeff Dig. Filter
    
    t0              = 1/fs
    t               = np.arange(0, tmax, t0)
    N               = np.shape(t)[0]
    
    xin             = np.zeros(N)
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
        
        
    
def impinvar (b, a, Fs = 1, tol = 1e-3):
#Impulsinvariantenmethode für Konstruktion von Digitaliltern aus analogfiltern

    if (np.ndim(a) != 1):
        sys.exit('a must be a vector')
    if (np.ndim(b) != 1):
        sys.exit('b must be a vector')
            
    a1 = a[0]
    if (a1 != 0):
        a = a/a1
    
    
    if (np.size(b) > np.size(a)):
        sys.exit('invalid size of input')
        
    elif (np.size(b) == np.size(a)):
        #remove direct feed-through
        kimp=b[0] / a[0]
        b = b-kimp*a
        b = b[1: ]
    
    
    
    pt      = np.roots(a)
    Npoles  = np.size(pt)
    mm, ip  = mpoles(pt, tol)
    
    pt      = pt[ip]
    starts  = np.nonzero(mm==1)[0]
    #if np.size(starts)>2:
    end     = np.append(starts[np.arange(1,np.size(starts))] , Npoles)
    #else:
        #end = np.array([Npoles])
    polemult=np.zeros_like(pt)
    poleavg=np.zeros_like(pt)
    
    for k in range(np.size(starts)):
        print(k)
        jkl             = np.arange(starts[k], end[k])
        polemult[jkl]   = mm[end[k]-1] * np.ones_like(jkl)
        poleavg[jkl]    = np.mean(pt[jkl]) * np.ones_like(jkl)
        
    rez = np.zeros(Npoles, dtype= complex)
    
    kp  = int(Npoles)
    
    while kp>0:
        pole = poleavg[kp-1]
        mulp = np.real(polemult[kp-1]).astype(int)
        num  = b
        
        
        den = np.poly(poleavg[np.append(np.arange(1,kp-mm[kp-1]+1), np.arange(kp+1, Npoles+1 ) ) -1 ])
#        if ((kp-mm[kp-1])>0):
#            if (Npoles>(kp+1)):
#                den  = np.poly(poleavg[np.array([np.arange(0,kp-mm[kp-1]) , np.arange(kp+1, Npoles)])])
#        elif (Npoles>(kp+1)):
#            den = np.poly(poleavg[np.arange(kp+1, Npoles)])
#        else:
#            den = np.array([1])
        if np.size(num)==1 and np.size(den)!=1 :
            rez[kp-1] = num / np.polyval(den, pole)
        elif np.size(num)!=1 and np.size(den)==1: 
            rez[kp-1] = np.polyval(num, pole) / den
        elif np.size(num)==1 and np.size(den)==1: 
            rez[kp-1] = num/den
        else:
            rez[kp-1] = np.polyval(num, pole) / np.polyval(den, pole)
        kp -= 1
        for k in range(1,int(mulp)):
            #print(k)
            num, den = polyder_div(num/k , den)
            rez[kp-1] = np.polyval(num, pole) / np.polyval(den, pole)
            kp -=1
        
    r   = rez/scipy.special.gamma(mm)   
    p   = poleavg
    
    az  = np.poly(np.exp(p/Fs))
    tn  = np.arange(Npoles)/Fs
    mm1 = mm-1
    tt  = np.tile(tn, (np.size(tn),1)).T ** np.tile(mm1,(np.size(tn),1))
    ee  = np.exp((p *   np.ones((np.size(p), np.size(tn)))).T   *   tn).T
    hh  = (tt*ee) @r   
    bz  = dsp.lfilter(az, 1, hh)
    
    if 'kimp' in locals():
        #restore direct feed through
        bz = kimp*az + np.append(bz , 0)
    
    bz  = bz/Fs
    if a1 != 0:
        az = az*a1
        
    #b,a = dsp.invres(r, p, k)
        


    return bz, az

def check_array(x):
    try:
        x.shape
        return True
    except:
        return False

def polyder_div(u,v):
    #returns derivate of u/v represented as a/b
    if not check_array(u):
        u=np.array(u)
    if not check_array(v):
        v=np.array(v)    
    nu = np.size(u)
    nv = np.size(v)
    if nu<=1:
        up = np.array([0])
    else:
        up = u[0:nu-1] * np.arange(nu-1, 0, -1)
        if np.size(up)==0:
            up=np.array([0])
    if nv<=1:
        vp = np.array([0])
    else:
        vp = v[0:nv-1] * np.arange(nv-1, 0, -1)
        if np.size(vp)==0:
            vp=np.array([0])
        
    

    if up.all()==0 or v.all()==0:
        a1 = np.zeros(np.size(up)+np.size(v)-1)
    else:
        a1 = np.convolve(up, v)
    if u.all()==0 or vp.all()==0:
        a2 = np.zeros(np.size(u)+np.size(vp)-1)
    else:
        a2 = np.convolve(u, vp)
    
    i = np.size(a1)
    j = np.size(a2)
    z = np.zeros(abs(i-j))
    if i>j:
        a2 = np.append(z, a2)#
    elif j>i:
        a1 = np.append(z, a1)
        
    a = a1-a2
    f = np.nonzero(a!=0)[0]
    if np.size(f)!=0: 
        a=a[f[0]:]
    else:
        a=np.zeros(1)
    b = np.convolve(v,v)   
    f = np.nonzero(b!=0)[0]
    if np.size(f)!=0: 
        b=b[f[0]:]
    else:
        b=np.zeros(1)
        
    if np.size(a) > np.max([nu + nv -2 ,1]):
        a= a[2:]
     
    return a,b        
            

   

def mpoles( p, tol=1e-3 , reorder=1):
    #Identify repeated poles & their multiplicities
    Lp      = np.size(p)
    
    indp    = np.argsort(-p)
    if(reorder==1):        
        p = p[indp]
        
    mults   = np.zeros_like(p)
    indx    = np.zeros_like(p)
    ii      = 0
    while(Lp > 1):
        test    = np.abs( p[0] - p)
        if (np.all(np.abs(p)>0)):
            jkl     = np.nonzero(test < tol*np.abs(p[0]))
        else:
            jkl     = np.nonzero(test < tol)
    
        kk           = np.arange(np.size(jkl))
        mults[ii+kk] = kk+1
        done         = jkl
        indx[ii+kk]  = indp[done]
        indp         = np.delete(indp, done)
        p            = np.delete(p   , done)
        Lp           = np.size(p)
        ii           = ii + np.size(done)
    if Lp == 1:
        indx[ii]    = indp[0] 
        mults[ii]   = 1
    
    return mults.astype(int), indx.astype(int)
    
    
    
    
    
    
    