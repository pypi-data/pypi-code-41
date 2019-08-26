""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.0.0
Author  : Stefano Covino
Date    : 05/01/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : AddHeaderEntry (fitsfile, keylist, entrylist, commentlist, outfilename=None)

Remarks :

History : (05/01/2017) First version.
"""


from SRP.SRPCatalogue.GetVizierCat import GetVizierCat
from astropy.table import Table




def GetPanSTARRS(rad,decd,rds):
    skybotaddress = "archive.stsci.edu"
    skybotquery = "/panstarrs/search.php?RA=%.5f&DEC=%.5f&radius=%.2f&outputformat=CSV&action=Search"
    #
    pstars= []
    for r,d in zip(rad,decd):
        data = GetVizierCat(skybotaddress,skybotquery % (r,d,rds/60.))
        #
        if data != ['no rows found']:
            dt = Table.read(data,format='ascii.csv')
            objid = dt['objName'][1]
            pstars.append("%s" % (objid))
        else:
            pstars.append('No')
    #
    return pstars
