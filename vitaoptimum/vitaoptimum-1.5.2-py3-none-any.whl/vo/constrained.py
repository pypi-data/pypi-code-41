from vitaoptimum.base import VitaOptimumBase
from vitaoptimum.base import Validation


class VitaOptimumConstrained(VitaOptimumBase):
    """Base Constrained Global Optimization Method Class"""

    def __init__(self, fobj, dim, nfe, np, strategy, ng, nh, tol):
        self._dim = dim
        self._nfe = nfe
        self._np = np
        self._strategy = strategy
        self._ng = ng
        self._nh = nh
        self._tol = tol
        self._validate_constrainted()
        VitaOptimumBase.__init__(self, fobj)

    def info(self):
        """Prints information about the algorithm to standard output"""
        pass

    def run(self):
        pass

    def _validate(self):
        pass

    def _validate_constrainted(self):
        Validation.dim(self._dim)
        Validation.np(self._np)
        Validation.nfe(self._nfe, self._np)
        Validation.strategy(self._strategy)
        Validation.ng(self._ng)
        Validation.nh(self._nh)
        Validation.tol(self._tol)
        self._validate()
