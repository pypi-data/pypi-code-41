""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.1.0
Author  : Stefano Covino
Date    : 14/03/2019
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : 

Remarks :

History : (25/02/2016) First version.
        : (19/04/2017) SRPFITS added.
        : (21/12/2017) Minor improvement.
        : (14/03/2019) Fluxes in output
"""

import numpy
from SRPFITS.Photometry.Counts2Mag import Counts2Mag



def Flux2Mag(flux,fluxerr,zp=25):
    mag = []
    emag = []
    oflux = []
    oeflux = []
    for f, ef in zip(flux,fluxerr):
        if f > 0 and ef > 0:
            m,em = Counts2Mag(f,ef,zp)
            of,oef = f,ef
            if em > 0.5:
                m,em = Counts2Mag(3*ef,ef,zp)
                em = 99
        elif f <= 0 and ef > 0:
            m,em = Counts2Mag(3*ef,ef,zp)
            em = 99
            of,oef = 0., ef
        else:
            m = 99
            em = 99
            of = -99
            oef = -99
        #
        if numpy.isnan(m) or numpy.isnan(em):
            m = 99
            em = 99
        if numpy.isnan(f) or numpy.isnan(ef):
            of = -99
            oef = -99
        #
        mag.append(m)
        emag.append(em)
        oflux.append(of)
        oeflux.append(oef)
    #
    resdict = {"mags":numpy.array(mag),"emags":numpy.array(emag),"fluxes":numpy.array(oflux),"efluxes":numpy.array(oeflux)}
    return resdict
