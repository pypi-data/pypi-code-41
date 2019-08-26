""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.0.0
Author  : Stefano Covino
Date    : 06/03/2019
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : 

Remarks :

History : (06/03/2019) First version.
"""

import numpy
from SRP.SRPTime.UT2MJD import UT2MJD
import SRPGW as GW



def ReadDate(res,header):
    if header == GW.DATEHEAD:
        return res
    elif header == 'JD':
        return res - GW.JD2MJD
    elif header == 'DATE-OBS':
        if res.find('T') >= 0:
            gyyg,gttg = res.split('T')
            gyg,gmog,gdg = gyyg.split('-')
            ghg,gmig,gsg = gttg.split(':')
            return UT2MJD(int(gyg),int(gmog),int(gdg),int(ghg),int(gmig),float(gsg))
        else:
            return -99.
    else:
        return -99.
#