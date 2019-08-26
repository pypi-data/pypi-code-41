""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.1.0
Author  : Stefano Covino
Date    : 16/12/2016
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : DaoPSFPhot

Remarks :

History : (24/02/2016) First version.
        : (13/07/2016) Case of single object.
        : (16/12/2016) FWHM in PSF computation.
"""


import SRPGW as GW
import numpy
from PythonPhot import aper
from PythonPhot import getpsf
from PythonPhot import pkfit



def DaoPSFPhot(x,y,px,py,data,rds=(5,10,15),fwhm=5,zp=30.0,cent=False,bck=True):
    mag,magerr,flux,fluxerr,sky,skyerr,badflag,outstr = aper.aper(data,px,py,phpadu=GW.VSTgain,apr=rds[0],zeropoint=zp,skyrad=[rds[1],rds[2]],verbose=False)
    gauss,psf,psfmag = getpsf.getpsf(data,px,py,mag,sky,ronois=GW.VSTron,phpadu=GW.VSTgain,idpsf=numpy.arange(len(px)),psfrad=rds[2],fitrad=fwhm,psfname='/dev/null')
    pk = pkfit.pkfit_class(data,gauss,psf,ronois=GW.VSTron,phpadu=GW.VSTgain)
    #
    mag,magerr,flux,fluxerr,sky,skyerr,badflag,outstr = aper.aper(data,x,y,phpadu=GW.VSTgain,apr=rds[0],zeropoint=zp,skyrad=[rds[1],rds[2]],verbose=False)
    #
    pflux = []
    pfluxerr = []
    if len(x) < 2:
        x = [x,]
        y = [y,]
        sky = [sky,]
    for x,y,s in zip(x,y,sky):
        errmag,chi,sharp,niter,scale = pk.pkfit(1,x,y,s,radius=rds[0],recenter=cent)
        f = scale*10**(0.4*(zp-psfmag))
        ef = errmag*10**(0.4*(zp-psfmag))
        pflux.append(float(f))
        pfluxerr.append(float(ef))
    #
    return flux.flatten(), fluxerr.flatten(), pflux, pfluxerr
    
