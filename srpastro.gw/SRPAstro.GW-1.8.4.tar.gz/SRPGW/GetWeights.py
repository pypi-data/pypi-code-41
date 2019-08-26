""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.1.0
Author  : Stefano Covino
Date    : 10/02/2016
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : AddHeaderEntry (fitsfile, keylist, entrylist, commentlist, outfilename=None)

Remarks :

History : (21/01/2016) First version.
        : (27/01/2016) Minor improvement.
        : (02/02/2016) Bug correction.
        : (10/02/2016) Simpler and faster.
"""


import numpy
from astropy.io.fits import getdata
from astropy.wcs import WCS



def GetWeights(rad,decd,fname,weightlim=0.0,size=5):
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
        if numpy.count_nonzero(datf > weightlim) < datf.size or datf.size == 0:
            res.append(0)
        else:
            res.append(1)
        del datf
        #
    return res
