""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.2.2
Author  : Stefano Covino
Date    : 14/03/2019
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : GetPSFPhot

Remarks :

History : (25/02/2016) First version.
        : (26/02/2016) Minor improvement.
        : (13/12/2016) ApyPSF photometry added.
        : (16/12/2016) FWHM for PSF computation.
        : (14/03/2019) Change in output.
"""


from astropy.io.fits import getdata
import SRPGW as GW
from SRPGW.Flux2Mag import Flux2Mag
from SRPGW.DaoPSFPhot import DaoPSFPhot
from SRPGW.ApyPSFPhot import ApyPSFPhot



def GetPSFPhot(x,y,px,py,fname,rds=(5,10,15),fwhm=5,zp=30.0,sept='dao',cent=False,bck=True):
    data = getdata(fname)
    #
    if sept=='dao':
        flux,fluxerr,pflux,pfluxerr = DaoPSFPhot(x,y,px,py,data,rds,fwhm,zp,cent,bck)
        resa = Flux2Mag(flux.flatten(),fluxerr.flatten(),zp)
        resp = Flux2Mag(pflux,pfluxerr,zp)
    elif sept=='apy':
        aflux,afluxerr,pflux,pfluxerr = ApyPSFPhot(x,y,px,py,data,rds,fwhm,zp,cent)
        resa = Flux2Mag(aflux,afluxerr,zp)
        resp = Flux2Mag(pflux,pfluxerr,zp)
    #
    return resa['mags'], resa['emags'], resp['mags'], resp['emags'], resp['fluxes'], resp['efluxes']
    
