import ctypes
import numpy

from vitaoptimum.vo.unconstrained import VitaOptimumUnconstrained
from vitaoptimum.base import Strategy, Validation
from vitaoptimum.result import VitaOptimumBusResult


class Bus(VitaOptimumUnconstrained):
    """Binary Unconstrained Global Optimization Method"""

    def __init__(self, fobj, dim, nfe=10000, np=25, cr=0.2,
                 strategy=Strategy.rand3):
        self._cr = cr
        VitaOptimumUnconstrained.__init__(self, fobj, dim, nfe, np, strategy)

    def run(self, restarts=1, verbose=False):
        """Runs the algorithm"""

        xopt = numpy.zeros(self._dim, dtype=ctypes.c_int32)
        conv = numpy.zeros(self._nfe, dtype=ctypes.c_double)

        callback_type = ctypes.PYFUNCTYPE(ctypes.c_double,  # return
                                          ctypes.POINTER(ctypes.c_int32),
                                          ctypes.c_int32)

        self._lib.vitaOptimum_Bus.restype = ctypes.c_double
        self._lib.vitaOptimum_Bus.argtypes = [ctypes.c_bool,
                                              callback_type,
                                              ctypes.c_int32,
                                              ctypes.c_int32,
                                              ctypes.c_int32,
                                              ctypes.c_double,
                                              ctypes.c_int32,
                                              self._array_1d_int,
                                              self._array_1d_double
                                              ]
        best = self._lib.vitaOptimum_Bus(verbose,
                                         callback_type(self._fobj),
                                         self._dim,
                                         self._nfe,
                                         self._np,
                                         self._cr,
                                         self._strategy.value,
                                         xopt,
                                         conv)
        return VitaOptimumBusResult(self._dim, self._fobj_orig, best, xopt,
                                    conv[:int(self._nfe / self._np) * self._np])

    def info(self):
        self._lib.vitaOptimum_Bus_info()

    def _validate(self):
        Validation.cr(self._cr)

    def _fobj_wrapper(self, v, d):
        v = numpy.asarray(v[:d])
        return self._fobj_orig(v)

    def _set_wrapper(self, fobj_orig):
        self._fobj = self._fobj_wrapper
