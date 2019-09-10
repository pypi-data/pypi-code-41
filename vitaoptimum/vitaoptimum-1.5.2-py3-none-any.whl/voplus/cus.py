import ctypes
import numpy

from vitaoptimum.voplus.unconstrained import VitaOptimumPlusUnconstrained
from vitaoptimum.base import StrategyPlus, Validation
from vitaoptimum.result import VitaOptimumPlusCusResult


class Cus(VitaOptimumPlusUnconstrained):
    """Continuous Unconstrained Global Optimization Method"""

    def __init__(self, fobj, dim, low, high, np=100,
                 strategy=StrategyPlus.curr2pbest,
                 stagnation=10000,
                 qmeasures=numpy.zeros(4, dtype=ctypes.c_double)):
        self._low = low
        self._high = high
        VitaOptimumPlusUnconstrained.__init__(self, fobj, dim, np, strategy, stagnation, qmeasures)

    def run(self, restarts=1, verbose=False):
        """Runs the algorithm"""

        converged = numpy.zeros(1, dtype=ctypes.c_bool)
        xopt = numpy.zeros(self._dim, dtype=ctypes.c_double)

        callback_type = ctypes.PYFUNCTYPE(ctypes.c_double,  # return
                                          ctypes.POINTER(ctypes.c_double),
                                          ctypes.c_int32)

        self._lib_plus.vitaOptimumPlus_Cus.restype = ctypes.c_double
        self._lib_plus.vitaOptimumPlus_Cus.argtypes = [
            callback_type,          # fobj
            self._array_1d_double,  # xopt
            ctypes.c_int32,         # dim
            self._array_1d_double,  # low
            self._array_1d_double,  # high
            ctypes.c_int32,         # np
            ctypes.c_int32,         # strategy
            ctypes.c_int32,         # stagnation
            self._array_1d_bool,    # converged
            self._array_1d_double,  # qmeasures
            ctypes.c_bool           # verbose
        ]

        best = self._lib_plus.vitaOptimumPlus_Cus(
            callback_type(self._fobj),
            xopt,
            self._dim,
            self._low,
            self._high,
            self._np,
            self._strategy.value,
            self._stagnation,
            converged,
            self._qmeasures,
            verbose
        )

        return VitaOptimumPlusCusResult(self._dim, self._low, self._high,
                                        self._fobj_orig, best, xopt, converged,
                                        self._qmeasures)

    def info(self):
        self._lib_plus.vitaOptimumPlus_Cus_info()

    def _validate(self):
        Validation.lh(self._low, self._high, self._dim)

    def _fobj_wrapper(self, v, d):
        v = numpy.asarray(v[:d])
        return self._fobj_orig(v)

    def _set_wrapper(self, fobj_orig):
        self._fobj = self._fobj_wrapper
