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



def FindSubPathes (col1, col2):
    posset = set()
    for p1,p2 in zip(col1,col2):
        comfin = ""
        for c1,c2 in zip(p1[::-1],p2[::-1]):
            if c1 == c2:
                comfin = comfin + c1
            else:
                posset.add(comfin[::-1])
                break
    #
    posstr = list(posset)
    posstr.sort()
    #
    resstr = set()
    for p1,p2 in zip(col1,col2):
        resstr.add((p1[:-len(posstr[0])],p2[:-len(posstr[0])]))
    return list(resstr)