from vitaoptimum.base import VitaOptimumBase
from vitaoptimum.base import Validation


class VitaOptimumUnconstrained(VitaOptimumBase):
    """Base Unconstrained Global Optimization Method Class"""

    def __init__(self, fobj, dim, nfe, np, strategy):
        self._dim = dim
        self._nfe = nfe
        self._np = np
        self._strategy = strategy
        self._validate_unconstrainted()
        VitaOptimumBase.__init__(self, fobj)

    def info(self):
        """Prints information about the algorithm to standard output"""
        pass

    def run(self):
        pass

    def _validate(self):
        pass

    def _validate_unconstrainted(self):
        Validation.dim(self._dim)
        Validation.np(self._np)
        Validation.nfe(self._nfe, self._np)
        Validation.strategy(self._strategy)
        self._validate()
