""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.0.0
Author  : Stefano Covino
Date    : 25/02/2016
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : GetApPhot

Remarks :

History : (25/02/2016) First version.

"""


import SRPGW as GW
import numpy
from PythonPhot import aper


def DaoPhot(x,y,data,rds=(5,10,15),backgr=True):
    if backgr:
        mag,magerr,flux,fluxerr,sky,skyerr,badflag,outstr = aper.aper(data,x,y,phpadu=GW.VSTgain,apr=rds[0],zeropoint=30,skyrad=[rds[1],rds[2]],readnoise=GW.VSTron)
    else:
        mag,magerr,flux,fluxerr,sky,skyerr,badflag,outstr = aper.aper(data,x,y,phpadu=GW.VSTgain,apr=rds[0],zeropoint=30,skyrad=[rds[1],rds[2]],setskyval=0.0,readnoise=GW.VSTron)
    #
    return flux.flatten(),fluxerr.flatten()
    


