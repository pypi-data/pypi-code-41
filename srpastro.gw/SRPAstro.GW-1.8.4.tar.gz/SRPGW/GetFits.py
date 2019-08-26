""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.0.3
Author  : Stefano Covino
Date    : 06/12/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : GetFits

Remarks :

History : (07/01/2016) First version.
        : (11/02/2016) Simpler and faster.
        : (18/05/2017) Minor update.
        : (06/12/2017) Workaround since with astropy.io.fits functions it does not work.
"""

import os
from astropy.io import fits
import astLib.astWCS as aw
import astLib.astImages as aLaI
from SRPFITS.Fits.GetData import GetData
from SRPFITS.Fits.GetHeader import GetHeader
#import pyfits



def GetFits (ra, dec, cutname, fname, size=1.):
    dat = GetData(fname)[0]
    #hd = pyfits.open(fname)
    #hed = hd[0].header
    hed = GetHeader(fname)[0]
    wcs = aw.WCS(hed,mode='pyfits')
    wcs.NUMPY_MODE = False
    #
    ndata = aLaI.clipImageSectionWCS(dat,wcs,ra,dec,size/60.0)
    fitsfname = cutname+'_'+os.path.splitext(os.path.split(fname)[-1])[0]+'.fits'
    aLaI.saveFITS(fitsfname,ndata['data'],ndata['wcs'])
    return fitsfname
    
