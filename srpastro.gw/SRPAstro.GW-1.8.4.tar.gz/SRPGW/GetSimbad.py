""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.0.0
Author  : Stefano Covino
Date    : 29/10/2015
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : AddHeaderEntry (fitsfile, keylist, entrylist, commentlist, outfilename=None)

Remarks :

History : (29/10/2015) First version.
"""


from astropy.coordinates import SkyCoord
from astropy import units as u
from astroquery.simbad import Simbad
import warnings



def GetSimbad(rad,decd,rds):
    crd = SkyCoord(ra=rad*u.degree, dec=decd*u.degree)
    #
    warnings.filterwarnings('ignore', category=UserWarning, append=True)
    try:
        restab = Simbad.query_region(crd, radius=rds*u.arcsec)
    except:
        restab = None
    warnings.resetwarnings()
    if restab is None:
        obj = 'No'
    else:
        #if restab['MAIN_ID'].size == 1:
        #    obj = restab['MAIN_ID'][0].decode().strip().replace(' ','_')
        #else:
        #    obj = restab['MAIN_ID'][1].decode().strip().replace(' ','_')
        obj = restab[0]['MAIN_ID'].decode().strip().replace(' ','_')
    #
    return obj
