""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.2.3
Author  : Stefano Covino
Date    : 31/07/2018
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : Score

Remarks :

History : (06/03/2016) First version.
        : (18/03/2016) Lower weight to magnitude difference.
        : (24/12/2016) Chi2 in score.
        : (18/01/2017) Higher score for nearby galaxies.
        : (21/12/2017) More moderate score for nearby galaxies.
        : (31/07/2019) Even more moderate score for nearby galaxies.
"""

import numpy


def NeiFct (neigh):
    fn = 0.20*neigh+0.0
    return numpy.where(neigh > 5, 1.0, fn)

def DNeiFct (dneigh):
    fd  = 0.2*(dneigh-2.5)+1.0
    return numpy.where(dneigh > 2.5, 1.0, numpy.where(fd < 0.0, 0.0, fd))

def neiWei (neigh,dneigh):
    return numpy.where((dneigh>2.5) | (neigh>5), 1.0, (NeiFct(neigh)+DNeiFct(dneigh))/2.)

def magWei(magave):
    return (30.-magave)/30.




def Score(magave,varmag,neigh,dneigh,closegal=-99,chi2=-99):
    #
    sco = varmag * neiWei(neigh, dneigh) + magWei(magave)
    #
    sco = numpy.where(closegal != -99, sco + 0.55, sco)
    #
    sco = numpy.where(chi2 != -99, sco + chi2/100., sco)
    #
    return 100*sco
