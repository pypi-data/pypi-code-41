""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.0.0
Author  : Stefano Covino
Date    : 14/05/2019
E-mail  : stefano.covino@inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   :

Remarks :

History : (14/05/2019) First version.
"""

from astropy.table import Table, join, unique
from astropy import units as u
import SRPGW as GW
from astroquery.xmatch import XMatch



def GetSDSSxMatch(tab, rds, cccol=(GW.RACOL,GW.DECCOL)):
    itab = Table([tab[cccol[0]],tab[cccol[1]]])
    otab = XMatch.query(cat1=itab,cat2='vizier:V/147/sdss12',max_distance=rds*u.arcsec,colRA1=cccol[0],colDec1=cccol[1])
    #
    otabsel = Table([otab[cccol[0]],otab[cccol[1]],otab['objID']])
    #
    if len(otabsel) > 0:
        newtab = join(tab, otabsel, join_type='left')
    else:
        tab[GW.SDSSCOL] = -99
        newtab = tab
    #
    try:
        newtab2 = unique(newtab,GW.IDCOL)
    except KeyError:
        newtab2 = newtab
    #
    if 'objID' in newtab2.columns.keys():
        newtab2['objID'][newtab2['objID'].mask == True] = -99
        #
        if GW.SDSSCOL in newtab2.columns.keys():
            newtab2.remove_column(GW.SDSSCOL)
        newtab2.rename_column('objID',GW.SDSSCOL)
    #
    return newtab2
