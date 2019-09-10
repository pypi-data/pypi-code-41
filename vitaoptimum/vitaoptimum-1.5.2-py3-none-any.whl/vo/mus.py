import ctypes
import numpy

from vitaoptimum.base import Strategy
from vitaoptimum.vo.mixed import VitaOptimumMixed
from vitaoptimum.result import VitaOptimumMusResult


class Mus(VitaOptimumMixed):
    """Mixed Unconstrained Global Optimization Method"""

    def __init__(self, fobj,
                 dc, lc, hc,
                 di, li, hi,
                 db, dp,
                 nfe=10000, np=25,
                 fc=0.85, fi=0.85,
                 cCr=0.4, iCr=0.4, bCr=0.2,
                 cS=Strategy.rand3, iS=Strategy.rand3, bS=Strategy.rand3, pS=Strategy.rand3,
                 lf=5):
        VitaOptimumMixed.__init__(self, fobj,
                                  dc, lc, hc,
                                  di, li, hi,
                                  db, dp,
                                  nfe, np,
                                  fc, fi,
                                  cCr, iCr, bCr,
                                  cS, iS, bS, pS,
                                  lf
                                  )

    def run(self, restarts=1, verbose=False):
        """Runs the algorithm"""

        xoptC = numpy.zeros(self._dc, dtype=ctypes.c_double)
        xoptI = numpy.zeros(self._di, dtype=ctypes.c_int)
        xoptB = numpy.zeros(self._db, dtype=ctypes.c_int)
        xoptP = numpy.zeros(self._dp, dtype=ctypes.c_int)
        conv = numpy.zeros(self._nfe, dtype=ctypes.c_double)

        callback_type = ctypes.PYFUNCTYPE(ctypes.c_double,  # return
                                          ctypes.POINTER(ctypes.c_double),  # xc
                                          ctypes.c_int,  # dc
                                          ctypes.POINTER(ctypes.c_int),  # xi
                                          ctypes.c_int,  # di
                                          ctypes.POINTER(ctypes.c_int),  # xb
                                          ctypes.c_int,  # db
                                          ctypes.POINTER(ctypes.c_int),  # xp
                                          ctypes.c_int)  # dp
        self._lib.vitaOptimum_Mus.restype = ctypes.c_double  # best
        self._lib.vitaOptimum_Mus.argtypes = [ctypes.c_bool,  # verbose
                                              callback_type,  # fobj
                                              ctypes.c_int,  # Dc
                                              self._array_1d_double,  # Lc
                                              self._array_1d_double,  # Hc
                                              ctypes.c_int,  # Di
                                              self._array_1d_int,  # Li
                                              self._array_1d_int,  # Hi
                                              ctypes.c_int,  # Db
                                              ctypes.c_int,  # Dp
                                              ctypes.c_int,  # nfe
                                              ctypes.c_int,  # Np
                                              ctypes.c_double,  # Fc
                                              ctypes.c_double,  # Fi
                                              ctypes.c_double,  # cCr
                                              ctypes.c_double,  # iCr
                                              ctypes.c_double,  # bCr
                                              ctypes.c_int,  # cS
                                              ctypes.c_int,  # iS
                                              ctypes.c_int,  # bS
                                              ctypes.c_int,  # pS
                                              ctypes.c_int,  # LF
                                              self._array_1d_double,  # xoptC
                                              self._array_1d_int,  # xoptI
                                              self._array_1d_int,  # xoptB
                                              self._array_1d_int,  # xoptP
                                              self._array_1d_double  # conv
                                              ]

        best = self._lib.vitaOptimum_Mus(verbose,
                                         callback_type(self._fobj),
                                         self._dc, self._lc, self._hc,
                                         self._di, self._li, self._hi,
                                         self._db, self._dp,
                                         self._nfe, self._np,
                                         self._fc, self._fi,
                                         self._cCr, self._iCr, self._bCr,
                                         self._cS.value, self._iS.value, self._bS.value, self._pS.value,
                                         self._lf,
                                         xoptC, xoptI, xoptB, xoptP,
                                         conv)
        return VitaOptimumMusResult(self._fobj_orig, best, xoptC, xoptI, xoptB, xoptP,
                                    conv[:int(self._nfe / self._np) * self._np])

    def info(self):
        self._lib.vitaOptimum_Mus_info()

    def _validate(self):
        pass

    def _fobj_wrapper(self, xc, dc, xi, di, xb, db, xp, dp):
        xc = numpy.asarray(xc[:dc])
        xi = numpy.asarray(xi[:di])
        xb = numpy.asarray(xb[:db])
        xp = numpy.asarray(xp[:dp])
        return self._fobj_orig(xc, xi, xb, xp)

    def _set_wrapper(self, fobj_orig):
        self._fobj = self._fobj_wrapper
