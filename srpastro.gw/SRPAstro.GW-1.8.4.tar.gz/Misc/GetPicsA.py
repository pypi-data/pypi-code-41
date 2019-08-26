""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.0.0
Author  : Stefano Covino
Date    : 06/11/2015
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : GetPics

Remarks :

History : (06/11/2015) First version.
"""

import os
import astropy.io.fits as aif
import aplpy
from SRPGW.GetFits import GetFits


def GetPicsA (ra, dec, picid, fname, size=15., osize=2.5):
    ffn = GetFits(ra,dec,"_temp",fname,0.5)
    #
    f = aplpy.FITSFigure(ffn)
    os.remove(ffn)
    f.show_grayscale(invert=True,pmax=99.)
    f.recenter(ra,dec,radius=size/3600.)
    f.show_circles(ra, dec, osize/3600.,edgecolor='blue')
    f.frame.set_linewidth(2)
    f.frame.set_color('black')
    f.add_grid()
    f.grid.show()
    picfname = picid+'_'+os.path.splitext(os.path.split(fname)[-1])[0]+'.png'
    f.save(picfname)
    return picfname
    