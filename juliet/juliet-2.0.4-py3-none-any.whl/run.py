# Import batman, for lightcurve models:
import batman
# Import radvel, for RV models:
import radvel
# Import george for detrending:
import george
# Import celerite for detrending:
import celerite
# Import dynesty for dynamic nested sampling:
try:
    import dynesty
    force_pymultinest = False
except:
    print('Dynesty installation not detected. Forcing pymultinest.')
    force_pymultinest = True
# Import multinest for (importance) nested sampling:
try:
    import pymultinest
    force_dynesty = False
except:
    print('(py)MultiNest installation (or libmultinest.dylib) not detected. Forcing sampling with dynesty.')
    force_dynesty = True
import sys

# Prepare the celerite term:
import celerite
from celerite import terms

from .utils import *
# This class was written by Daniel Foreman-Mackey for his paper: 
# https://github.com/dfm/celerite/blob/master/paper/figures/rotation/rotation.ipynb
class RotationTerm(terms.Term):
    parameter_names = ("log_amp", "log_timescale", "log_period", "log_factor")
    def get_real_coefficients(self, params):
        log_amp, log_timescale, log_period, log_factor = params
        f = np.exp(log_factor)
        return (
            np.exp(log_amp) * (1.0 + f) / (2.0 + f),
            np.exp(-log_timescale),
        )

    def get_complex_coefficients(self, params):
        log_amp, log_timescale, log_period, log_factor = params
        f = np.exp(log_factor)
        return (
            np.exp(log_amp) / (2.0 + f),
            0.0,
            np.exp(-log_timescale),
            2*np.pi*np.exp(-log_period),
        ) 

__all__ = ['fit'] 

class fit(object):
    """
    Given a dictionary with priors and a dataset, this class performs a juliet fit. Example usage:
        >>> out = juliet.fit(priors,t_lc=times,y_lc=fluxes,yerr_lc=fluxes)
    """

    def __init__(self,priors,t_lc = None, y_lc = None, yerr_lc = None, instruments_lc = None,\
                 t_rv = None, y_rv = None, yerr_rv = None, instruments_rv = None):
        if ((t_lc is  None) or (y_lc is None) or (yerr_lc is None)) and ((t_rv is None) or \
             (y_rv is None) or (yerr_rv is None)):
            raise Exception('No complete dataset (photometric or radial-velocity) given.\n'+\
                  ' Make sure to feed times (t_lc and/or t_rv) values (y_lc and/or y_rv) \n'+\
                  ' and errors (yerr_lc and/or yerr_rv).')
        
        self.results = {}
        val1,val2 = reverse_ld_coeffs('quadratic',0.1,0.5)     
        print("yup:",val1,val2)   
