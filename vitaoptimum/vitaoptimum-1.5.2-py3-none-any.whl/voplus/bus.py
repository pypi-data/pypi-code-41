import ctypes
import numpy

from vitaoptimum.voplus.unconstrained import VitaOptimumPlusUnconstrained
from vitaoptimum.base import StrategyPlus
from vitaoptimum.result import VitaOptimumPlusBusResult


class Bus(VitaOptimumPlusUnconstrained):
    """Binary Unconstrained Global Optimization Method"""

    def __init__(self, fobj, dim, np=100,
                 strategy=StrategyPlus.curr2pbest,
                 stagnation=10000,
                 qmeasures=numpy.zeros(4, dtype=ctypes.c_double)):
        VitaOptimumPlusUnconstrained.__init__(self, fobj, dim, np, strategy, stagnation, qmeasures)

    def run(self, restarts=1, verbose=False):
        """Runs the algorithm"""

        converged = numpy.zeros(1, dtype=ctypes.c_bool)
        xopt = numpy.zeros(self._dim, dtype=ctypes.c_int32)

        callback_type = ctypes.PYFUNCTYPE(ctypes.c_double,  # return
                                          ctypes.POINTER(ctypes.c_int32),
                                          ctypes.c_int32)

        self._lib_plus.vitaOptimumPlus_Bus.restype = ctypes.c_double
        self._lib_plus.vitaOptimumPlus_Bus.argtypes = [
            callback_type,  # fobj
            self._array_1d_int,  # xopt
            ctypes.c_int32,  # dim
            ctypes.c_int32,  # np
            ctypes.c_int32,  # strategy
            ctypes.c_int32,  # stagnation
            self._array_1d_bool,  # converged
            self._array_1d_double,  # qmeasures
            ctypes.c_bool  # verbose
        ]

        best = self._lib_plus.vitaOptimumPlus_Bus(
            callback_type(self._fobj),
            xopt,
            self._dim,
            self._np,
            self._strategy.value,
            self._stagnation,
            converged,
            self._qmeasures,
            verbose
        )

        return VitaOptimumPlusBusResult(self._dim, self._fobj_orig, best,
                                        xopt, converged, self._qmeasures)

    def info(self):
        self._lib_plus.vitaOptimumPlus_Bus_info()

    def _validate(self):
        pass

    def _fobj_wrapper(self, v, d):
        v = numpy.asarray(v[:d])
        return self._fobj_orig(v)

    def _set_wrapper(self, fobj_orig):
        self._fobj = self._fobj_wrapper
