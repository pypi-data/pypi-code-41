""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.1.1
Author  : Stefano Covino
Date    : 07/12/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : DaoPSFPhot

Remarks :

History : (16/12/2016) First version.
        : (06/12/2017) PSF from image.
        : (07/12/2017) Better coding.
"""


import SRPGW as GW
import numpy as np
from photutils.psf import IntegratedGaussianPRF, DAOGroup
from photutils.background import MMMBackground, MADStdBackgroundRMS
from astropy.modeling.fitting import LevMarLSQFitter
from astropy.stats import gaussian_sigma_to_fwhm
from photutils.psf import BasicPSFPhotometry
from astropy.table import Table
from scipy.stats import norm
from photutils.psf.sandbox import DiscretePRF
from photutils.detection import DAOStarFinder


def ApyPSFPhot(x,y,px,py,data,rds=(5,10,15),fwhm=5,zp=30.0,cent=False):
    pflux = []
    pfluxerr = []
    #
    corrfact = (norm.cdf(rds[0],scale=fwhm)/norm.cdf(fwhm,scale=fwhm))**2
    #corrfact = 1.
    #
    sigma_psf = fwhm/gaussian_sigma_to_fwhm
    bkgrms = MADStdBackgroundRMS()
    daogroup = DAOGroup(3.0*sigma_psf*gaussian_sigma_to_fwhm)
    mmm_bkg = MMMBackground()
    fitter = LevMarLSQFitter()
    size = np.rint(rds[0]*15).astype(np.int)
    #
    psfpos = Table(names=['x_0', 'y_0', 'flux_0'], data=[px,py,[1.]*len(px)])
    psf_model = DiscretePRF.create_from_image(data,psfpos,2*int(rds[0])+1,mode='median')
    if not cent:
        psf_model.x_0.fixed = True
        psf_model.y_0.fixed = True
    #
    for o in range(len(x)):
        i = np.rint(x[o]).astype(np.int)-1
        l = np.rint(y[o]).astype(np.int)-1
        image = data[l-size:l+size,i-size:i+size]
        #
        try:
            std = bkgrms(image)
        except TypeError:
            std = 0.0
        #
        daofind = DAOStarFinder(threshold=3.*std+mmm_bkg(image), fwhm=fwhm, exclude_border=True)
        dobj = daofind.find_stars(image)
        dobj.rename_column('xcentroid', 'x_0')
        dobj.rename_column('ycentroid', 'y_0')
        #
        photometry = BasicPSFPhotometry(group_maker=daogroup,bkg_estimator=mmm_bkg,psf_model=psf_model,fitter=LevMarLSQFitter(),fitshape=2*int(rds[0])+1,aperture_radius=rds[0])
        #
        if len(dobj) == 0:
            pos = Table(names=['x_0', 'y_0'], data=[[x[o]-i+size],[y[o]-l+size]])
            rt = photometry(image=image, init_guesses=pos)
        else:
            rt = photometry(image=image, init_guesses=dobj)
        #
        dist = np.sqrt((rt['x_fit'] - size)**2 + (rt['y_fit'] - size)**2)
        mdist = np.min(dist)
        npix = np.pi*rds[0]**2
        cbkg = npix*std**2
        flu = rt[dist == mdist]['flux_fit'][0]
        flu = flu*corrfact
        flu0 = rt[dist == mdist]['flux_0'][0]
        flue = np.sqrt(abs(flu)*GW.VSTgain + abs(cbkg)*GW.VSTgain + npix*GW.VSTron)
            #except TypeError:
            #flu = 0.0
            #flu0 = 0.0
            #flue = 0.0
        #
        pflux.append(float(flu))
        pfluxerr.append(float(flue))
        #
    return pflux, pfluxerr, pflux, pfluxerr
    
