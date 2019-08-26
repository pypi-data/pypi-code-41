""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.1.0
Author  : Stefano Covino
Date    : 10/02/2016
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : GetHeadVal

Remarks :

History : (06/11/2015) First version.
        : (10/02/2916) Simpler and better version.
"""


from astropy.io.fits import getval



def GetHeadVal(headentry, fname):
    try:
        hdv = getval(fname, headentry)
    except KeyError:
        hdv = -99
    #
    return hdv