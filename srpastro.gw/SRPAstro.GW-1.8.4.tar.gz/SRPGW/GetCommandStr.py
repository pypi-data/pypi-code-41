""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.0.0
Author  : Stefano Covino
Date    : 28/10/2015
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : AddHeaderEntry (fitsfile, keylist, entrylist, commentlist, outfilename=None)

Remarks :

History : (28/10/2015) First version.
"""


def GetCommandStr (inputstr, collist, root):
    cmdstr = []
    for en in inputstr.split():
        if en in collist:
            cmdstr.append(root+"['"+en+"'] ")
        elif en[0] == ':':
            cmdstr.append(root+"['"+en[1:]+"'] ")
        else:
            cmdstr.append(en+" ")
    return "".join(cmdstr)
