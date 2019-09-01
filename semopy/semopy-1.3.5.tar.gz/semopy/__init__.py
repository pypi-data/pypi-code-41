'''semopy is a Python package that implements numerous SEM-related functonality.'''
from .stats import gather_statistics, calc_likelihood, calc_aic,\
                   calc_bic, calc_aic, calc_bic, calc_likelihood
from .optimizer import Optimizer
from .inspector import inspect
from .model_nl import ModelNL
from .model import Model

name = "semopy"
__version__ = "1.3.5"
