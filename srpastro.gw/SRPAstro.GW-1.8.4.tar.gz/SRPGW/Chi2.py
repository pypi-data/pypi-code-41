""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.1.0
Author  : Stefano Covino
Date    : 25/03/2019
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   :

Remarks :

History : (23/12/2016) First version.
        : (25/03/2019) Fluxes rather than magnitudes.

"""

import numpy as np
from SRP.SRPStatistics.WeightedMean import WeightedMean
import SRPGW as GW


def Chi2(tab):
    res = []
    #
    fs = []
    efs = []
    #
    for e in tab.columns.keys():
        if GW.FLUX in e and e.find(GW.FLUX) == 0:
            fs.append(e)
    if len(fs) == 0:
        return -99
    #
    for e in tab.columns.keys():
        if GW.eFLUX in e:
            efs.append(e)
    if (len(efs) == 0) or (len(fs) != len(efs)):
        return -99
    #
    for e in tab:
        c = [(e[i],e[j]) for i,j in zip(fs,efs)]
        res.append(WeightedMean(c)[3])
    return res
