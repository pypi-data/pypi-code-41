""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.2.0
Author  : Stefano Covino
Date    : 04/03/2019
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : 

Remarks :

History : (29/11/2016) First version.
        : (07/12/2016) Better management of input coordinates and masks.
        : (04/03/2019) GAIA DR2
"""

from astropy.table import Table, join, unique
from astropy import units as u
import SRPGW as GW
from astroquery.xmatch import XMatch



def GetGAIAxMatch(tab, rds, cccol=(GW.RACOL,GW.DECCOL)):
    itab = Table([tab[cccol[0]],tab[cccol[1]]])
    #otab = XMatch.query(cat1=itab,cat2='vizier:I/337/gaia',max_distance=rds*u.arcsec,colRA1=cccol[0],colDec1=cccol[1])
    otab = XMatch.query(cat1=itab,cat2='vizier:I/345/gaia2',max_distance=rds*u.arcsec,colRA1=cccol[0],colDec1=cccol[1])
    #
    otabsel = Table([otab[cccol[0]],otab[cccol[1]],otab['source_id']])
    #
    if len(otabsel) > 0:
        newtab = join(tab, otabsel, join_type='left')
    else:
        tab[GW.GAIACOL] = -99
        newtab = tab
    #
    try:
        newtab2 = unique(newtab,GW.IDCOL)
    except KeyError:
        newtab2 = newtab
    #
    if 'source_id' in newtab2.columns.keys():
        newtab2['source_id']._sharedmask = False
        newtab2['source_id'][newtab2['source_id'].mask == True] = -99
        #
        if GW.GAIACOL in newtab2.columns.keys():
            newtab2.remove_column(GW.GAIACOL)
        newtab2.rename_column('source_id',GW.GAIACOL)
    #
    return newtab2
