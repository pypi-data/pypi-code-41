""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.0.0
Author  : Stefano Covino
Date    : 07/12/2016
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : AddHeaderEntry (fitsfile, keylist, entrylist, commentlist, outfilename=None)

Remarks :

History : (21/01/2016) First version.
"""


import numpy
from astropy.io.fits import getdata
from astropy.wcs import WCS
from astropy.stats import sigma_clipped_stats



def GetTest(rad,decd,fname,size=5):
    dat = getdata(fname)
    w = WCS(fname)
    #
    x, y = w.all_world2pix(rad,decd,0)
    #
    a = numpy.rint(x)-1
    b = numpy.rint(y)-1
    aa = a.astype(numpy.int)
    bb = b.astype(numpy.int)
    #
    res = []
    for i,l in zip(aa,bb):
        datf = dat[l-size:l+size,i-size:i+size]
        mean, median, std = sigma_clipped_stats(datf,iters=5)
        #mean = numpy.mean(datf)
        #std =  numpy.std(datf)
        res.append(mean)
        #
    return res
