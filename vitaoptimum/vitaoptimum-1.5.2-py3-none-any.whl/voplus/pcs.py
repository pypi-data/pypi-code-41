import ctypes
import numpy

from vitaoptimum.voplus.constrained import VitaOptimumPlusConstrained
from vitaoptimum.base import StrategyPlus
from vitaoptimum.result import VitaOptimumPlusPcsResult


class Pcs(VitaOptimumPlusConstrained):
    """Permutation Constrained Global Optimization Method"""

    def __init__(self, fobj, dim, ng, nh, np=100,
                 strategy=StrategyPlus.curr2pbest,
                 stagnation=10000, tol=0.001,
                 qmeasures=numpy.zeros(4, dtype=ctypes.c_double)):
        VitaOptimumPlusConstrained.__init__(self, fobj, dim, np, strategy, stagnation, qmeasures, ng, nh, tol)

    def run(self, restarts=1, verbose=False):
        """Runs the algorithm"""

        converged = numpy.zeros(1, dtype=ctypes.c_bool)
        xopt = numpy.zeros(self._dim, dtype=ctypes.c_int32)
        constr = numpy.zeros(self._ng + self._nh, dtype=ctypes.c_double)

        callback_type = ctypes.PYFUNCTYPE(ctypes.c_double,  # return
                                          ctypes.POINTER(ctypes.c_int),
                                          ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_double),
                                          ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_double),
                                          ctypes.c_int)

        self._lib_plus.vitaOptimumPlus_Pcs.restype = ctypes.c_double
        self._lib_plus.vitaOptimumPlus_Pcs.argtypes = [
            callback_type,          # fobj
            self._array_1d_int,     # xopt
            ctypes.c_int32,         # dim
            ctypes.c_int32,         # ng
            ctypes.c_int32,         # nh
            ctypes.c_int32,         # np
            ctypes.c_int32,         # strategy
            ctypes.c_int32,         # stagnation
            ctypes.c_double,        # tol
            self._array_1d_bool,    # converged
            self._array_1d_double,  # constraints
            self._array_1d_double,  # qmeasures
            ctypes.c_bool           # verbose
        ]

        best = self._lib_plus.vitaOptimumPlus_Pcs(
            callback_type(self._fobj),
            xopt,
            self._dim,
            self._ng,
            self._nh,
            self._np,
            self._strategy.value,
            self._stagnation,
            self._tol,
            converged,
            constr,
            self._qmeasures,
            verbose
        )

        return VitaOptimumPlusPcsResult(self._dim, self._fobj_orig,
                                        best, xopt, constr,
                                        converged, self._qmeasures)

    def info(self):
        self._lib_plus.vitaOptimumPlus_Pcs_info()

    def _validate(self):
        pass

    def _fobj_wrapper(self, x, d, g, ng, h, nh):
        x = numpy.asarray(x[:d])
        g = numpy.asarray(g[:ng])
        h = numpy.asarray(h[:nh])
        return self._fobj_orig(x, g, h)

    def _set_wrapper(self, fobj_orig):
        self._fobj = self._fobj_wrapper
