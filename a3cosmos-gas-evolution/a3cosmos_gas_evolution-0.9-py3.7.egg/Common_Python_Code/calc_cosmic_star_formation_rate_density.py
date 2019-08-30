#!/usr/bin/env python
# 

from __future__ import print_function

import os, sys, re, json, time, astropy
import numpy as np
from astropy.table import Table, Column, hstack
from copy import copy
from numpy import log10, power as pow

from astropy.cosmology import FlatLambdaCDM
cosmo = FlatLambdaCDM(H0=73, Om0=0.27, Tcmb0=2.725)

if sys.version_info.major >= 3:
    long = int
else:
    pass



# 
# def 
# 
def calc_cosmic_star_formation_rate_density_MadauDickinson2014(z):
    # Madau & Dickinson (2014)
    # converted to Chabrier IMF from Salpeter IMF
    rho_SFR = 0.015 * (1+z)**2.7 / (1.0 + ((1+z)/2.9)**5.6) / 1.64
    return rho_SFR








