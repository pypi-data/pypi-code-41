""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.1.1
Author  : Stefano Covino
Date    : 08/02/2016
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : AddHeaderEntry (fitsfile, keylist, entrylist, commentlist, outfilename=None)

Remarks :

History : (03/11/2015) First version.
        : (20/01/2016) Rome MySQL server query.
        : (08/02/2016) Rome server catalogue name.
"""

from astropy.table import Table
from astropy.coordinates import SkyCoord
from astropy.coordinates import search_around_sky
from astropy import units as u
from astroquery.vizier import Vizier
import warnings
import mysql.connector
import SRPGW as GW



def GetIGAIA(rad,decd,rds,myquery=False):
    if myquery == GW.IGAIABO or myquery == GW.IGAIARM:
        gaia = 'No'
        if myquery == GW.IGAIABO:
            cnx = mysql.connector.connect(user=GW.IGAIAUser, password=GW.IGAIAPwd, host=GW.IGAIAHost, database=GW.IGAIADB)
        else:
            cnx = mysql.connector.connect(user=GW.IGAIAUserRM, password=GW.IGAIAPwdRM, host=GW.IGAIAHostRM, database=GW.IGAIADBRM)
        #
        cursor = cnx.cursor()
        if myquery == GW.IGAIABO:
            query = "SELECT * FROM %s WHERE dif_circle(%s,%s,%s)" % (GW.IGAIACatBO,rad,decd,rds/60.0)
        else:
            query = "SELECT * FROM %s WHERE dif_circle(%s,%s,%s)" % (GW.IGAIACatRM,rad,decd,rds/60.0)
        #
        cursor.execute(query)
        res = []
        for i in cursor:
            res.append(i)
        if len(res) > 0:
            for l in range(len(cursor.column_names)):
                if cursor.column_names[l] == GW.IGAIACol:
                    gaia = 'IGAIA'+str(res[0][l])
                    break
        cursor.close()
        cnx.close()

    #
    else:
        crd = SkyCoord(ra=rad*u.degree, dec=decd*u.degree)
        #
        warnings.filterwarnings('ignore', category=UserWarning, append=True)
        try:
            restab = Vizier.query_region(crd, radius=rds*u.arcsec, catalog=["GAIA"])
        except:
            restab = []
        warnings.resetwarnings()
        if len(restab) == 0:
            gaia = "No"
        else:
            try:
                gaia = 'IGAIA'+str(restab[0][GW.IGAIACol][0])
            except KeyError:
                gaia = 'IGAIA'+str(restab[0][GW.IGAIAColb][0])
            #
    return gaia
