### Author: Devin Whitten
### Main driver for normalization routine, intended for SEGUE medium-resolution spectra.

import numpy as np
import pandas as pd
import sys, os
#sys.path.append("interface")
#from spectrum import Spectrum
from astropy.io import fits

from GISIC.spectrum import Spectrum



def normalize(wavelength, flux, sigma=30, k=3, cahk=False, band_check=True):
    spec = Spectrum(wavelength, flux)
    spec.generate_inflection_segments(sigma=sigma, cahk=cahk, band_check = band_check)
    spec.assess_segment_variation()
    spec.define_cont_points()
    spec.set_segment_continuum()
    spec.set_segment_midpoints()

    spec.spline_continuum(k=k)
    spec.normalize()

    return np.array(spec.wavelength), np.array(spec.flux_norm), np.array(spec.continuum)
