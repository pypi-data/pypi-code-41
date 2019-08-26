""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.0.2
Author  : Stefano Covino
Date    : 19/04/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : GetApPhot

Remarks :

History : (11/02/2016) First version.
        : (13/02/2016) Improved error estimate.
        : (19/04/2017) SRPFITS added.
"""



import SRP.SRPAstro as SRPAstro
import SRPGW as GW
import numpy
from SRPFITS.Photometry.getBackground import getBackground


def MyPhot(x,y,data,rds=(5,10,15),backgr=True):
    flux = []
    fluxerr = []
    for i,l in zip(x,y):
       totf,npix,maxf = SRPAstro.sumApert(data,i-1,l-1,rds[0])
       if backgr:
            bg,sbg,ebg,chbg,nbg = getBackground(data,i-1,l-1,rds[1],rds[2])
       else:
            bg = 0.0
            ebg = 0.0
       #
       tflux = totf-bg*npix
       tfluxerr = numpy.sqrt(numpy.fabs(totf)*GW.VSTgain + npix*(ebg*GW.VSTgain)**2 + npix*GW.VSTron)
       flux.append(tflux)
       fluxerr.append(tfluxerr)
    #
    return numpy.array(flux),numpy.array(fluxerr)
    
