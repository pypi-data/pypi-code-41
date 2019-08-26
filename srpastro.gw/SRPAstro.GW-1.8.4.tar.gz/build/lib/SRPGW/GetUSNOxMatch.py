""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.0.0
Author  : Stefano Covino
Date    : 25/02/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : 

Remarks :

History : (25/02/2017) First version.
"""

from astropy.table import Table, join, unique
from astropy import units as u
import SRPGW as GW
from astroquery.xmatch import XMatch



def GetUSNOxMatch(tab, rds, cccol=(GW.RACOL,GW.DECCOL)):
    itab = Table([tab[cccol[0]],tab[cccol[1]]])
    otab = XMatch.query(cat1=itab,cat2='vizier:I/284/out',max_distance=rds*u.arcsec,colRA1=cccol[0],colDec1=cccol[1])
    #
    otabsel = Table([otab[cccol[0]],otab[cccol[1]],otab['USNO-B1.0']])
    #
    if len(otabsel) > 0:
        newtab = join(tab, otabsel, join_type='left')
    else:
        tab[GW.USNOCOL] = -99
        newtab = tab
    #
    try:
        newtab2 = unique(newtab,GW.IDCOL)
    except KeyError:
        newtab2 = newtab
    #
    if 'USNO-B1.0' in newtab2.columns.keys():
        newtab2['USNO-B1.0']._sharedmask = False
        newtab2['USNO-B1.0'][newtab2['USNO-B1.0'].mask == True] = 'No'
        #
        if GW.USNOCOL in newtab2.columns.keys():
            newtab2.remove_column(GW.USNOCOL)
        newtab2.rename_column('USNO-B1.0',GW.USNOCOL)
    #
    return newtab2
