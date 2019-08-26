""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.0.2
Author  : Stefano Covino
Date    : 30/08/2016
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : AddHeaderEntry (fitsfile, keylist, entrylist, commentlist, outfilename=None)

Remarks :

History : (17/02/2016) First version.
        : (14/06/2016) Column added even if no matches.
        : (30/08/2016) Bug correction.
"""

from astropy.table import Table, join, unique
from astropy import units as u
import SRPGW as GW
from astroquery.xmatch import XMatch



def GetIGAIAxMatch(tab, rds, cccol=(GW.RACOL,GW.DECCOL)):
    itab = Table([tab[cccol[0]],tab[cccol[1]]])
    otab = XMatch.query(cat1=itab,cat2='vizier:I/324/igsl3',max_distance=rds*u.arcsec,colRA1=cccol[0],colDec1=cccol[1])
    #
    otabsel = Table([otab[GW.RACOL],otab[GW.DECCOL],otab['sourceId']])
    #
    if len(otabsel) > 0:
        newtab = join(tab, otabsel, join_type='left')
    else:
        tab[GW.GAIACOL] = -99
        newtab = tab
    #
    newtab2 = unique(newtab,GW.IDCOL)
    #
    if 'sourceId' in newtab2.columns.keys():
        newtab2['sourceId'][newtab2['sourceId'].mask == True] = -99
        #
        if GW.GAIACOL in newtab2.columns.keys():
            newtab2.remove_column(GW.GAIACOL)
        newtab2.rename_column('sourceId',GW.GAIACOL)
    #
    return newtab2
