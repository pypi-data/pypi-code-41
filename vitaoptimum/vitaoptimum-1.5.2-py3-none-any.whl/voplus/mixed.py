
from vitaoptimum.base import VitaOptimumBase
from vitaoptimum.base import Validation

class VitaOptimumPlusMixed(VitaOptimumBase):
    """Base Mixed Global Optimization Method Class"""

    def __init__(self, fobj,
                 dc, lc, hc,
                 di, li, hi,
                 db, dp,
                 np,
                 cS, iS, bS, pS,
                 stagnation, qmeasures):
        self._dc = dc
        self._lc = lc
        self._hc = hc
        self._di = di
        self._li = li
        self._hi = hi
        self._db = db
        self._dp = dp
        self._np = np
        self._cstrategy = cS
        self._istrategy = iS
        self._bstrategy = bS
        self._pstrategy = pS
        self._stagnation = stagnation
        self._qmeasures = qmeasures
        self._validate_mixed()
        VitaOptimumBase.__init__(self, fobj)

    def info(self):
        """Prints information about the algorithm to standard output"""
        pass

    def run(self):
        pass

    def _validate(self):
        pass

    def _validate_mixed(self):
        Validation.dim(self._dc)
        Validation.dim(self._di)
        Validation.dim(self._db)
        Validation.dim(self._dp)
        Validation.lh(self._lc, self._hc, self._dc)
        Validation.lh(self._li, self._hi, self._di)
        Validation.np(self._np)
        Validation.strategy_plus(self._cstrategy)
        Validation.strategy_plus(self._istrategy)
        Validation.strategy_plus(self._bstrategy)
        Validation.strategy_plus(self._pstrategy)
        Validation.stagnation(self._stagnation, self._np)
        Validation.qmeasures(self._qmeasures)
        self._validate()
