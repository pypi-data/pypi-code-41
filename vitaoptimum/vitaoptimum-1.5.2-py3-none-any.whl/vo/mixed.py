from vitaoptimum.base import VitaOptimumBase
from vitaoptimum.base import Validation


class VitaOptimumMixed(VitaOptimumBase):
    """Base Mixed Global Optimization Method Class"""

    def __init__(self, fobj,
                 dc, lc, hc,
                 di, li, hi,
                 db, dp,
                 nfe, np,
                 fc, fi,
                 cCr, iCr, bCr,
                 cS, iS, bS, pS,
                 lf):
        self._dc = dc
        self._lc = lc
        self._hc = hc
        self._di = di
        self._li = li
        self._hi = hi
        self._db = db
        self._dp = dp
        self._nfe = nfe
        self._np = np
        self._fc = fc
        self._fi = fi
        self._cCr = cCr
        self._iCr = iCr
        self._bCr = bCr
        self._cS = cS
        self._iS = iS
        self._bS = bS
        self._pS = pS
        self._lf = lf
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
        Validation.nfe(self._nfe, self._np)
        Validation.strategy(self._cS)
        Validation.strategy(self._iS)
        Validation.strategy(self._bS)
        Validation.strategy(self._pS)
        Validation.f(self._fc)
        Validation.f(self._fi)
        Validation.cr(self._cCr)
        Validation.cr(self._iCr)
        Validation.cr(self._bCr)
        Validation.lf(self._lf, self._dp)
        self._validate()
