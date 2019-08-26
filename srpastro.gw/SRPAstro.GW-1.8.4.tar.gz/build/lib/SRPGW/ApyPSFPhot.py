""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.2.1
Author  : Stefano Covino
Date    : 03/06/2019
E-mail  : stefano.covino@inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : DaoPSFPhot

Remarks :

History : (16/12/2016) First version.
        : (06/12/2017) PSF from image.
        : (07/12/2017) Better coding.
        : (29/05/2019) Improvements in PSF modeling.
        : (03/06/2019) Correction for PSF aperture photomerty radius.
"""


import SRPGW as GW
import numpy as np
from photutils.psf import DAOGroup
from photutils.background import MMMBackground, MADStdBackgroundRMS
from astropy.modeling.fitting import LevMarLSQFitter
from astropy.stats import gaussian_sigma_to_fwhm
from astropy.stats import sigma_clipped_stats
from photutils.psf import BasicPSFPhotometry
from astropy.table import Table
from photutils.detection import DAOStarFinder
from photutils.psf import extract_stars
from astropy.nddata import NDData
from photutils import EPSFBuilder
from photutils import CircularAperture
from photutils import aperture_photometry


OVERSAMPLING = 4

def ApyPSFPhot(x,y,px,py,data,rds=(5,10,15),fwhm=5,zp=30.0,cent=False):
    pflux = []
    pfluxerr = []
    #
    sigma_psf = fwhm/gaussian_sigma_to_fwhm
    bkgrms = MADStdBackgroundRMS()
    daogroup = DAOGroup(3.0*sigma_psf*gaussian_sigma_to_fwhm)
    mmm_bkg = MMMBackground()
    fitter = LevMarLSQFitter()
    size = np.rint(rds[0]*15).astype(np.int)
    #
    psfpos = Table(names=['x', 'y'], data=[px,py])
    mean_val, median_val, std_val = sigma_clipped_stats(data, sigma=2.)
    datas = data - median_val
    nddata = NDData(data=datas)
    stars = extract_stars(nddata, psfpos, size=2*rds[2])
    epsf_builder = EPSFBuilder(oversampling=OVERSAMPLING, maxiters=3, progress_bar=False)
    epsf, fitted_stars = epsf_builder(stars)
    #
    # compute the correction factor
    aper = CircularAperture([(epsf.shape[0]/2.,epsf.shape[1]/2.)], r=rds[0]*OVERSAMPLING)
    phap = aperture_photometry(epsf.data, aper)
    corrfact = phap['aperture_sum']
    if not cent:
        epsf.x_0.fixed = True
        epsf.y_0.fixed = True
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
        daofind = DAOStarFinder(threshold=5.*std+mmm_bkg(image), fwhm=fwhm, exclude_border=True)
        dobj = daofind.find_stars(image)
        dobj.rename_column('xcentroid', 'x_0')
        dobj.rename_column('ycentroid', 'y_0')
        #
        photometry = BasicPSFPhotometry(group_maker=daogroup,bkg_estimator=mmm_bkg,psf_model=epsf,fitter=LevMarLSQFitter(),fitshape=2*int(rds[0])+1,aperture_radius=rds[0])
        #
        if len(dobj) == 0:
            pos = Table(names=['x_0', 'y_0'], data=[[x[o]-i+size],[y[o]-l+size]])
            rt = photometry(image=image, init_guesses=pos)
        else:
            rt = photometry(image=image, init_guesses=dobj)
        #
        dist = np.sqrt((rt['x_fit'] - size)**2 + (rt['y_fit'] - size)**2)
        mdist = np.min(dist)
        flu = rt[dist == mdist]['flux_fit'][0]
        flue = rt[dist == mdist]['flux_unc'][0]
        #
        flu0 = rt[dist == mdist]['flux_0'][0]
        #
        flu = flu*corrfact/OVERSAMPLING**2
        flue = flue*corrfact/OVERSAMPLING**2
        #
        pflux.append(float(flu))
        pfluxerr.append(float(flue))
        #
    return pflux, pfluxerr, pflux, pfluxerr
    
