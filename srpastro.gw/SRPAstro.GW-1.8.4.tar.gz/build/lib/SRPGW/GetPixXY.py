""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.3.1
Author  : Stefano Covino
Date    : 19/04/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : AddHeaderEntry (fitsfile, keylist, entrylist, commentlist, outfilename=None)

Remarks :

History : (22/01/2016) First version.
        : (02/02/2016) Bug correction.
        : (11/02/2016) Simpler and faster.
        : (26/02/2016) Centering.
        : (16/05/2016) Better management of non-fully standard astrometry.
        : (19/04/2017) SRPFITS added.
"""


import numpy
from astropy.io.fits import getdata
from astropy.wcs import WCS
import astropy.wcs
from SRPFITS.Photometry.centerMoment import centerMoment
import astLib.astWCS as aLW




def GetPixXY(rad,decd,fname,cent=True,rds=5):
    dat = getdata(fname)
    APYWCS = False
    try:
        w = WCS(fname)
        APYWCS = True
    except astropy.wcs._wcs.InvalidTransformError:
        w = aLW.WCS(fname)
        w.NUMPY_MODE = False
    #
    if APYWCS:
        x, y = w.all_world2pix(rad,decd,0)
    else:
        XY = w.wcs2pix(rad.data, decd.data)
        x = [i[0] for i in XY]
        y = [i[1] for i in XY]
    #
    if cent:
        xx = []
        yy = []
        for i,l in zip(x,y):
            try:
                a,b = centerMoment(dat,i,l,rds)
                xx.append(a)
                yy.append(b)
            except (TypeError, ValueError):
                xx.append(i)
                yy.append(l)
    else:
        xx = x
        yy = y
    #
    return xx,yy
