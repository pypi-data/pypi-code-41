""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.4.6
Author  : Stefano Covino
Date    : 14/03/2019
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : GetApPhot

Remarks :

History : (17/11/2015) First version.
        : (12/12/2015) Better management of the upper limits.
        : (18/12/2015) Again a minor correction for the upper limits.
        : (28/01/2016) Possible centering before photometry.
        : (02/02/2016) nan handling.
        : (09/02/2016) Background subtraction choosable.
        : (25/02/2016) DaoPhot-like aperture photometry.
        : (26/02/2016) Report new positions if requested.
        : (27/07/2016) Syntax error correction.
        : (14/12/2016) Bug correction.
        : (19/04/2017) SRPFITS added.
        : (14/03/2019) Change in output.
"""


from astropy.io.fits import getdata
import SRPGW as GW
import numpy
from SRPFITS.Photometry.centerMoment import centerMoment
from SRPGW.SexPhot import SexPhot
from SRPGW.MyPhot import MyPhot
from SRPGW.ApyPhot import ApyPhot
from SRPGW.DaoPhot import DaoPhot
from SRPGW.Flux2Mag import Flux2Mag



def GetApPhot(x,y,fname,rds=(5,10,15),zp=30.0,sept='my',cent=False,bck=True):
    data = getdata(fname)
    #
    if cent:
        xx = []
        yy = []
        for i,l in zip(x,y):
            a,b = centerMoment(data,i,l,rds[1])
            xx.append(a)
            yy.append(b)
    else:
        xx = x
        yy = y
    #
    if sept == 'sex':
        flux,fluxerr = SexPhot(xx,yy,data,rds,backgr=bck)
    elif sept == 'my':
        flux,fluxerr = MyPhot(xx,yy,data,rds,backgr=bck)
    elif sept == 'apy':
        flux,fluxerr = ApyPhot(xx,yy,data,rds,backgr=bck)
    elif sept == 'dao':
        flux,fluxerr = DaoPhot(xx,yy,data,rds,backgr=bck)
    #
    res = Flux2Mag(flux,fluxerr,zp)
    #
    return res['mags'],res['emags'],res['fluxes'],res['efluxes']
    
