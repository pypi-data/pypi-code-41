import ctypes
import numpy

from abc import abstractmethod
from enum import Enum
from sys import platform


class Strategy(Enum):
    rand3 = 1
    rand2best = 2
    rand3dir = 3
    rand2bestdir = 4


class StrategyPlus(Enum):
    curr2pbest = 1
    crand2pbest = 2
    rrand2pbest = 3
    cbest2pbest = 4
    bbest2pbest = 5
    curr2pbestdir = 6
    crand2pbestdir = 7
    rrand2pbestdir = 8
    cbest2pbestdir = 9
    bbest2pbestdir = 10


class VitaOptimumBase:
    def __init__(self, fobj):
        self._array_1d_double =\
            numpy.ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=1, flags='F')
        self._array_1d_int =\
            numpy.ctypeslib.ndpointer(dtype=ctypes.c_int32, ndim=1, flags='F')
        self._array_1d_bool = \
            numpy.ctypeslib.ndpointer(dtype=ctypes.c_bool, ndim=1, flags='F')
        self._set_fobj(fobj)
        self._load_vo()
        self._load_vo_plus()

    def _load_vo(self):
        if platform in ["linux", "linux2"]:  # Linux
            shared_object = "libvo.so"
        elif platform == "darwin":  # OS X
            shared_object = "libvo.so"
        elif platform == "win32":  # Windows
            shared_object = "vo.dll"
        else:
            shared_object = "libvo.so"
        self._lib = ctypes.PyDLL(shared_object, mode=ctypes.RTLD_GLOBAL)

    def _load_vo_plus(self):
        if platform in ["linux", "linux2"]:  # Linux
            shared_object = "libvo-plus.so"
        elif platform == "darwin":  # OS X
            shared_object = "libvo-plus.so"
        elif platform == "win32":  # Windows
            shared_object = "vo-plus.dll"
        else:
            shared_object = "libvo-plus.so"
        self._lib_plus = ctypes.PyDLL(shared_object, mode=ctypes.RTLD_GLOBAL)

    @property
    def fobj(self):
        return self._fobj

    @fobj.setter
    def fobj(self, fobj_orig):
        self._set_fobj(fobj_orig)

    def _set_fobj(self, fobj_orig):
        if not fobj_orig:
            raise AttributeError("The objective function is not defined")
        if not callable(fobj_orig):
            raise TypeError("The objective function is not callable")
        self._fobj_orig = fobj_orig
        self._set_wrapper(fobj_orig)

    @abstractmethod
    def _set_wrapper(self, fobj_orig):
        pass

    @abstractmethod
    def info(self):
        pass

    @abstractmethod
    def run(self, restarts, verbose):
        pass

    @abstractmethod
    def _validate(self):
        pass


class Validation:

    @staticmethod
    def nfe(nfe, np):
        if not isinstance(nfe, int):
            raise TypeError("The number of function evaluations nfe must be a positive integer: %s" % nfe)
        if nfe < np:
            raise ValueError("The number of function evaluations nfe must be >= %d" % np)

    @staticmethod
    def np(np):
        if not isinstance(np, int):
            raise TypeError("The population size np must be a positive integer")
        if np < 5:
            raise ValueError("The population size np must be >= 5")


    @staticmethod
    def stagnation(stagnation, np):
        if not isinstance(stagnation, int):
            raise TypeError("The stagnation value must be a positive integer")
        if stagnation < np:
            raise ValueError("The stagnation value must be >= np")

    @staticmethod
    def strategy(strategy):
        if not isinstance(strategy, Strategy):
            raise TypeError("Wrong strategy")

    @staticmethod
    def strategy_plus(strategy):
        if not isinstance(strategy, StrategyPlus):
            raise TypeError("Wrong strategy")

    @staticmethod
    def f(f):
        if not isinstance(f, float):
            raise TypeError("The differentiation parameter must be a floating-point number")
        if f < 0:
            raise ValueError("The differentiation parameter must be >= 0")

    @staticmethod
    def cr(cr):
        if not isinstance(cr, float):
            raise TypeError("The crossover parameter must be a floating-point number")
        if cr < 0 or cr >= 1:
            raise ValueError("The crossover parameter must be in [0, 1)")

    @staticmethod
    def lf(lf, dim):
        if not isinstance(lf, int):
            raise TypeError("The locality factor must be an integer")
        if lf <= 0:
            raise ValueError("The locality factor must be a positive number")
        if lf >= dim:
            raise ValueError("The locality factor must be less than dimension %d", dim)

    @staticmethod
    def dim(dim):
        if not isinstance(dim, int):
            raise TypeError("The dimension must be an integer")
        if dim < 0:
            raise ValueError("The dimension must be >= 0")

    @staticmethod
    def lh(low, high, dim):
        if not isinstance(low, numpy.ndarray):
            raise TypeError("The low boundary is not a multidimensional numpy array: %s", low)
        if len(low) != dim:
            raise ValueError("The low boundary size must be %d", dim)

        if not isinstance(high, numpy.ndarray):
            raise TypeError("The high boundary is not a multidimensional numpy array")
        if len(high) != dim:
            raise ValueError("The high boundary size must be %d", dim)

    @staticmethod
    def ng(ng):
        if not isinstance(ng, int):
            raise TypeError("The inequality constraints dimension ng must be an integer")
        if ng < 0:
            raise ValueError("The inequality constraints dimension ng must be >= 0")

    @staticmethod
    def nh(nh):
        if not isinstance(nh, int):
            raise TypeError("The equality constraints dimension nh must be an integer")
        if nh < 0:
            raise ValueError("The equality constraints dimension nh must be >= 0")

    @staticmethod
    def tol(tol):
        if not isinstance(tol, float):
            raise TypeError("The tolerance must be a float")
        if tol <= 0:
            raise ValueError("The tolerance must be > 0")

    @staticmethod
    def qmeasures(qmeasures):
        if len(qmeasures) != 4:
            raise ValueError("The qmeasures length must be = 4")
        # if not isinstance(qmeasures, float):
        #     raise TypeError("The qmeasures must be a float")
        # for v in qmeasures:
        #     if v < 0.0:
        #         raise ValueError("The qmeasures must be >= 0")
