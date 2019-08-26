""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.1.0
Author  : Stefano Covino
Date    : 07/12/2016
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : AddHeaderEntry (fitsfile, keylist, entrylist, commentlist, outfilename=None)

Remarks :

History : (17/02/2016) First version.
        : (14/06/2016) Column added even if no matches.
        : (30/08/2016) Bug correction.
        : (07/12/2016) Better management of input coordinates and masks.
"""

from astropy.table import Table, join, unique
from astropy import units as u
import SRPGW as GW
from astroquery.xmatch import XMatch



def GetSimbadxMatch(tab, rds, cccol=(GW.RACOL,GW.DECCOL)):
    itab = Table([tab[cccol[0]],tab[cccol[1]]])
    otab = XMatch.query(cat1=itab,cat2='simbad',max_distance=rds*u.arcsec,colRA1=cccol[0],colDec1=cccol[1])
    #
    otabsel = Table([otab[cccol[0]],otab[cccol[1]],otab['main_id']])
    #
    if len(otabsel) > 0:
        newtab = join(tab, otabsel, join_type='left')
    else:
        tab[GW.SIMBCOL] = 'No'
        newtab = tab
    #
    try:
        newtab2 = unique(newtab,GW.IDCOL)
    except KeyError:
        newtab2 = newtab
    #
    if 'main_id' in newtab2.columns.keys():
        newtab2['main_id'][newtab2['main_id'].mask == True] = 'No'
        #
        if GW.SIMBCOL in newtab2.columns.keys():
            newtab2.remove_column(GW.SIMBCOL)
        newtab2.rename_column('main_id',GW.SIMBCOL)
    #
    return newtab2
