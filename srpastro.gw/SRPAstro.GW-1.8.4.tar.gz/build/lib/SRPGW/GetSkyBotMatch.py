""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.3.0
Author  : Stefano Covino
Date    : 16/08/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : AddHeaderEntry (fitsfile, keylist, entrylist, commentlist, outfilename=None)

Remarks :

History : (06/03/2016) First version.
        : (16/05/2016) Better managent of not fully standard astrometry.
        : (13/06/2016) Search radius dependent on the telescope field of view.
        : (16/08/2017) Bug correction and better managemnt of coordinates.
"""


from SRP.SRPCatalogue.GetVizierCat import GetVizierCat
from astropy.wcs import WCS
import astropy.wcs
from SRPGW.GetHeadVal import GetHeadVal
import numpy
from astropy.table import Table
from astropy.coordinates import SkyCoord
from astropy.coordinates import search_around_sky
from astropy import units as u
import astropy.units.core
import SRPGW as GW
import astLib.astWCS as aLW
import ephem




def GetSkyBotMatch(rad,decd,fname,time,rds,maxerr):
    skybotaddress = "vo.imcce.fr"
    skybotquery = "/webservices/skybot/skybotconesearch_query.php?-ep=%s&-ra=%.5f&-dec=%.5f&-rd=%.2f&-mime=text&-outout=object&-filter=%.1f&-from=SRP"
    #
    APYWCS = False
    try:
        w = WCS(fname)
        APYWCS = True
    except astropy.wcs._wcs.InvalidTransformError:
        w = aLW.WCS(fname)
        w.NUMPY_MODE = False
    #
    nx1 = GetHeadVal('NAXIS1',fname)
    nx2 = GetHeadVal('NAXIS2',fname)
    tel = GetHeadVal(GW.TELHEAD,fname)
    if tel == GW.VSTName:
        radsearch = max(nx1,nx2)*GW.VSTpixsize/3600.0
    elif tel == GW.CNName:
        radsearch = max(nx1,nx2)*GW.CNpixsize/3600.0
    else:
        radsearch = 2.0
    #
    if APYWCS:
        rac, decc = w.all_pix2world(nx1/2,nx2/2,0,ra_dec_order=True)
    else:
        RADEC = w.pix2wcs(nx1/2,nx2/2)
        rac = RADEC[0]
        decc = RADEC[1]
    #
    data = GetVizierCat(skybotaddress,skybotquery % (time,rac,decc,radsearch,maxerr))
    #
    objl = []
    ral = []
    decl = []
    magl = []
    #
    if data != None:
        for en in data:
            il = en.split('|')
            if len(il) > 7:
                objid = il[1].strip()
                try:
                    ra = float(il[2])*15.0
                except ValueError:
                    ra = numpy.degrees(ephem.hours(il[2]))
                try:
                    dec = float(il[3])
                except ValueError:
                    dec = numpy.degrees(ephem.degrees(il[3]))
                objvmag = float(il[5])
                #
                objl.append(objid)
                ral.append(ra)
                decl.append(dec)
                magl.append(objvmag)
    #
    answ = numpy.array(['No']*len(rad),dtype='<U25')
    if len(objl) > 0:
        t = Table([objl,ral,decl,magl],names=('Object',GW.RACOL,GW.DECCOL,'Mag'))
        #
        try:
            c1 = SkyCoord(ra=rad*u.degree, dec=decd*u.degree)
        except astropy.units.core.UnitsError:
            c1 = SkyCoord(ra=rad, dec=decd)
        #
        try:
            c2 = SkyCoord(ra=t[GW.RACOL]*u.degree, dec=t[GW.DECCOL]*u.degree)
        except astropy.units.core.UnitsError:
            c2 = SkyCoord(ra=t[GW.RACOL], dec=t[GW.DECCOL])
        #
        id1, id2, d2d, d3d = search_around_sky(c1, c2, rds*u.arcsec)
        #
        if len(id1) > 0:
            answ[id1] = t[id2]['Object']
    #
    return answ

