""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.1.1
Author  : Stefano Covino
Date    : 24/02/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : AddHeaderEntry (fitsfile, keylist, entrylist, commentlist, outfilename=None)

Remarks :

History : (03/04/2016) First version.
		: (26/05/2016) Working for arrays in input.
        : (24/02/2017) Better management of demanding WCS.
"""



from astropy.wcs import WCS
import astropy.wcs.wcs
import numpy




def IsCoordIn(rad,decd,fname):
    w = WCS(fname)
    #
    try:
        x, y = w.all_world2pix(rad,decd,0)
    except astropy.wcs.wcs.NoConvergence:
        x, y = w.wcs_world2pix(rad,decd,0)
    #
    X = numpy.array(x)
    Y = numpy.array(y)
    #
    return numpy.where((X >= 0) & (X <= w._naxis1) & (Y >= 0) & (Y <= w._naxis2), True, False)
