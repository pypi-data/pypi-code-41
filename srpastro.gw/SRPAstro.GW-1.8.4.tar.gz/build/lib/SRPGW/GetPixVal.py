""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.2.1
Author  : Stefano Covino
Date    : 26/08/2019
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : AddHeaderEntry (fitsfile, keylist, entrylist, commentlist, outfilename=None)

Remarks :

History : (02/11/2015) First version.
        : (27/01/2016) Minor correction.
        : (10/02/2016) Simpler and more rational version.
        : (30/08/2016) More robust against problems.
        : (26/08/2019) Worksround for managing PS1 BPM data
"""


import numpy
from astropy.io.fits import getdata
from astropy.wcs import WCS
from SRPGW.GetHeadVal import GetHeadVal



def GetPixVal(rad,decd,fname):
    dat = getdata(fname)
    w = WCS(fname)
    #
    nx1 = GetHeadVal('NAXIS1',fname)
    nx2 = GetHeadVal('NAXIS2',fname)
    #
    x, y = w.all_world2pix(rad,decd,0)
    #
    a = numpy.rint(x)-1
    b = numpy.rint(y)-1
    aa = a.astype(numpy.int)
    bb = b.astype(numpy.int)
    #
    # Workaround for PS1 bpm frames
    if fname.find('ps1') > 0 and fname.find('bpm') > 0:
        dat = numpy.where(dat == 0, 1, 0)
    #
    inside = (aa >= 0) & (aa <= nx1) & (bb >= 0) & (bb <= nx2)
    #
    val = numpy.where(inside,dat[bb,aa],0.)
    #
    return val
