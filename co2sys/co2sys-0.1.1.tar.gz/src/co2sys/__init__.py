#from __future__ import absolute_import

__version__ = '0.1.0'


import sys

from . import calculations
from . import constants


from .calculations import CarbonateSystem as calc_co2_system
from .calculations import CarbonateSystem

import numpy as np
try:
    import matplotlib.pyplot as plt   
    HAS_PYPLOT = True
except ImportError:
    HAS_PYPLOT = False

def co2sys(temp,salt, **kwargs):
    """Calculate the carbonate system

    Caculate the carbonate system using the methodoloy based on
    CO2SYS (HREF). This mainly a python implementation of the
    CO2SYS.m script.

    Parameters (Two of [TA, TC, pCO2, fCO2, pH] must be specified)
    ==========
    salt : array_like
        Input salinity (PSU)
    temp : array_like
        Input temperature
    pres : array_like
        Input pressure, default=1000
    TA : array_like, optional
        Total Alkalinity
    TC : array_like, optional
        Dissolved Inorganic Carbon
    pCO2 : array_like, optional
        partial pressure of CO2 (\$mu$Atm)
    fCO2 : array_like, optional
        fugacitiy of CO2 (\$mu$Atm)
    pH : array_like, optional
        pH
    temp_out : array_like, optional
        Change Carbonate system to eq at temp_out
    salt_out : array_like, optional
        Change Carbonate system to eq at salt_out
    pres_out : array_like, optional
        Change Carbonate system to eq at pres_out
    """
    pass

def example_plot():
    """Create example plot from matlab script"""
    temp = np.arange(0, 41) 
    salt = np.arange(0, 41) 
    tmat,smat = np.meshgrid(temp, salt)
    co = CarbonateSystem(temp=tmat, salt=smat, TA=2300, TC=2100)

    plt.clf() 
    plt.contourf(tmat, smat, co.pCO2, 20, vmin=0, vmax=1200)
    plt.colorbar()
    plt.contour(tmat, smat, co.pCO2, 20, colors='w', linewidths=0.5)
    plt.ylabel('Salinity [psu]')
    plt.xlabel('Temperature [$\degree$C]')
    plt.title('Dependence of pCO2 [$\mu$atm] on T and S')

def calc_TAlk(salt, temp):
    """Calculate Total Alkalinity                                           
    From Lee et al (doi:10.1029/2006GL027207) North Atlantic                
    """
    aprm = 2305.                                                           
    bprm = 53.97                                                           
    cprm = 2.74                                                            
    dprm = -1.16                                                           
    eprm = -0.040                                                          
    return (aprm + bprm*(salt-35) + cprm*(salt-35)**2 +
                dprm*(temp-20) + eprm*(temp-20)**2)

