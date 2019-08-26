""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.0.1
Author  : Stefano Covino
Date    : 05/03/2019
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   :

Remarks :

History : (20/09/2016) First version.
        : (05/03/2019) GLADE 2.
"""

from astropy.table import Table, join, unique
from astropy import units as u
import SRPGW as GW
from astroquery.xmatch import XMatch



def GetGLADExMatch(tab, rds, cccol=(GW.RACOL,GW.DECCOL)):
    itab = Table([tab[cccol[0]],tab[cccol[1]]])
    #otab = XMatch.query(cat1=itab,cat2='vizier:VII/275/glade1',max_distance=rds*u.arcsec,colRA1=cccol[0],colDec1=cccol[1])
    otab = XMatch.query(cat1=itab,cat2='vizier:VII/281/glade2',max_distance=rds*u.arcsec,colRA1=cccol[0],colDec1=cccol[1])
    #
    otabsel = Table([otab[cccol[0]],otab[cccol[1]],otab['angDist']])
    #
    if len(otabsel) > 0:
        newtab = join(tab, otabsel, join_type='left')
    else:
        tab[GW.GLADECOL] = -99
        newtab = tab
    #
    try:
        newtab2 = unique(newtab,GW.IDCOL)
    except KeyError:
        newtab2 = newtab
    #
    if 'angDist' in newtab2.columns.keys():
        newtab2['angDist'][newtab2['angDist'].mask == True] = -99
        #
        if GW.GLADECOL in newtab2.columns.keys():
            newtab2.remove_column(GW.GLADECOL)
        newtab2.rename_column('angDist',GW.GLADECOL)
    #
    return newtab2
