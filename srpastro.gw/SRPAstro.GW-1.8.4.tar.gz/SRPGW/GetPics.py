""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 2.0.3
Author  : Stefano Covino
Date    : 18/05/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : GetPics

Remarks :

History : (06/11/2015) First version.
        : (23/01/2016) APLPY version for gravitown
        : (11/02/2016) Simpler and faster.
        : (03/03/2017) More cuts label tried.
        : (18/05/2017) Minor update.
"""

import os
import astLib.astWCS as aw
import astLib.astImages as aLaI
import astLib.astPlots as aLaP
from SRPFITS.Fits.GetData import GetData
from SRPFITS.Fits.GetHeader import GetHeader
import astropy.io.fits as aif
import aplpy
from SRPGW.GetFits import GetFits
import SRPGW as GW
import pylab
from SRP.SRPSystem.Pipe import Pipe
#import astropy.stats as AS


def GetPics (ra, dec, picid, fname, size=30., osize=5., fmode=GW.ASTLIB):
    if fmode == GW.APLPY:
        ffn = GetFits(ra,dec,"_temp",fname,0.5)
        #
        f = aplpy.FITSFigure(ffn)
        os.remove(ffn)
        #
        f.show_grayscale(invert=True,pmax=99.)
        f.recenter(ra,dec,radius=size/(2*3600.))
        f.show_circles(ra, dec, osize/(2*3600.),edgecolor='blue')
        f.frame.set_linewidth(2)
        f.frame.set_color('black')
        f.add_grid()
        f.grid.show()
        picfname = picid+'_'+os.path.splitext(os.path.split(fname)[-1])[0]+'.png'
        f.save(picfname)
    #
    elif fmode == GW.ASTLIB:
        dat = GetData(fname)[0]
        hed = GetHeader(fname)[0]
        wcs = aw.WCS(hed,mode='pyfits')
        wcs.NUMPY_MODE = False
        #
        ndata = aLaI.clipImageSectionWCS(dat,wcs,ra,dec,size/3600.0)
        #mn,md,si = AS.sigma_clipped_stats(ndata['data'])
        plfc = aLaP.ImagePlot(ndata['data'],ndata['wcs'],cutLevels=["relative",99.0],colorMapName='gist_yarg')
        #plfc = aLaP.ImagePlot(ndata['data'],ndata['wcs'],cutLevels=[mn-si,mn+si],colorMapName='gist_yarg')
        #plfc = aLaP.ImagePlot(ndata['data'],ndata['wcs'],cutLevels=["smart",99.5],colorMapName='gist_yarg')
        plfc.addPlotObjects([ra],[dec],"obj",size=osize,color='blue')
        picfname = picid+'_'+os.path.splitext(os.path.split(fname)[-1])[0]+'.png'
        plfc.save(picfname)
        #
    else:
        res = os.system("SRPGWPICSStamp -i %s -o %.6f %.6f -s %.2f -n %s " % (fname,ra,dec,size/60.,picid))
        picfname = picid+'_'+os.path.splitext(os.path.split(fname)[-1])[0]+'.png'
    #
    pylab.close()
    return picfname
    
