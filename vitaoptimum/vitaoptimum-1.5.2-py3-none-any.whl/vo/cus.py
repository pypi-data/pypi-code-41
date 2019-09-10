import ctypes
import numpy

from vitaoptimum.vo.unconstrained import VitaOptimumUnconstrained
from vitaoptimum.base import Strategy, Validation
from vitaoptimum.result import VitaOptimumCusResult


class Cus(VitaOptimumUnconstrained):
    """Continuous Unconstrained Global Optimization Method"""

    def __init__(self, fobj, dim, low, high,
                 nfe=10000, np=25, f=0.85, cr=0.4,
                 strategy=Strategy.rand3):
        self._low = low
        self._high = high
        self._f = f
        self._cr = cr
        VitaOptimumUnconstrained.__init__(self, fobj, dim, nfe, np, strategy)

    def run(self, restarts=1, verbose=False):
        """Runs the algorithm"""

        xopt = numpy.zeros(self._dim, dtype=ctypes.c_double)
        conv = numpy.zeros(self._nfe, dtype=ctypes.c_double)

        callback_type = ctypes.PYFUNCTYPE(ctypes.c_double,  # return
                                          ctypes.POINTER(ctypes.c_double),
                                          ctypes.c_int)

        self._lib.vitaOptimum_Cus.restype = ctypes.c_double
        self._lib.vitaOptimum_Cus.argtypes = [ctypes.c_bool,
                                              callback_type,
                                              ctypes.c_int,
                                              self._array_1d_double,
                                              self._array_1d_double,
                                              ctypes.c_int,
                                              ctypes.c_int,
                                              ctypes.c_double,
                                              ctypes.c_double,
                                              ctypes.c_int,
                                              self._array_1d_double,
                                              self._array_1d_double
                                              ]
        best = self._lib.vitaOptimum_Cus(verbose,
                                         callback_type(self._fobj),
                                         self._dim,
                                         self._low,
                                         self._high,
                                         self._nfe,
                                         self._np,
                                         self._f,
                                         self._cr,
                                         self._strategy.value,
                                         xopt,
                                         conv)
        return VitaOptimumCusResult(self._dim, self._low, self._high,
                                    self._fobj_orig, best, xopt,
                                    conv[:int(self._nfe / self._np) * self._np])

    def info(self):
        self._lib.vitaOptimum_Cus_info()

    def _validate(self):
        Validation.lh(self._low, self._high, self._dim)
        Validation.cr(self._cr)
        Validation.f(self._f)

    def _fobj_wrapper(self, v, d):
        v = numpy.asarray(v[:d])
        return self._fobj_orig(v)

    def _set_wrapper(self, fobj_orig):
        self._fobj = self._fobj_wrapper
