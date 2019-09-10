from vitaoptimum.base import VitaOptimumBase
from vitaoptimum.base import Validation


class VitaOptimumPlusUnconstrained(VitaOptimumBase):
    """Base Unconstrained Global Optimization Method Class"""

    def __init__(self, fobj, dim, np, strategy, stagnation, qmeasures):
        self._dim = dim
        self._np = np
        self._strategy = strategy
        self._stagnation = stagnation
        self._qmeasures = qmeasures
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
        Validation.strategy_plus(self._strategy)
        Validation.stagnation(self._stagnation, self._np)
        Validation.qmeasures(self._qmeasures)
        self._validate()
