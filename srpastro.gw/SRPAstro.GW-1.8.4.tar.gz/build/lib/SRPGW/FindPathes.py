""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.0.0
Author  : Stefano Covino
Date    : 12/11/2015
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : FindSubPathes

Remarks :

History : (12/11/2015) First version.
"""



def FindPathes (col1, col2):
    posset = set()
    for p1,p2 in zip(col1,col2):
        posset.add((p1,p2))
    #
    posstr = list(posset)
    return posstr