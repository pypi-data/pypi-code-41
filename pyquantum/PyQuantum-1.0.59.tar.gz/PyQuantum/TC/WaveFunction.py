# -------------------------------------------------------------------------------------------------
# scientific
import numpy as np
import copy
# -------------------------------------------------------------------------------------------------
# Common
from PyQuantum.Tools.Assert import *
from PyQuantum.Common.Matrix import *
# -------------------------------------------------------------------------------------------------
from scipy.sparse.linalg import norm

# -------------------------------------------------------------------------------------------------


class WaveFunction(Matrix):

    # ---------------------------------------------------------------------------------------------
    def __init__(self, states, init_state, amplitude=1):
        # Assert(isinstance(states, dict), "states is not dict", FILE(), LINE())
        Assert(isinstance(init_state, list), "init_state is not list", FILE(), LINE())

        Assert(len(states) > 1, "w_0 is not set", FILE(), LINE())

        self.states = states
        self.init_state = init_state
        self.amplitude = amplitude

        k_found = None

        # print(states)
        # print(init_state)
        for k, v in enumerate(states):
            # for k, v in states.items():
            if init_state == v:
                k_found = k

                break

        Assert(k_found is not None, "w_0 is not set", FILE(), LINE())

        super(WaveFunction, self).__init__(m=len(states), n=1, dtype=np.complex128)
        # print("k_found =", k_found)

        self.data[k_found, 0] = amplitude
    # ---------------------------------------------------------------------------------------------

    def set_ampl(self, state, amplitude=1):
        k_found = None

        for k, v in enumerate(self.states):
            # print(state, v)
            if state == v:
                # k_found = k
                print("k_found =", k_found)
                break

        Assert(k_found is not None, "w_0 is not set", FILE(), LINE())
        self.data[k_found, 0] = amplitude

    # ------------------------------------------------------------------------------------------
    def normalize(self):
        nnorm = norm(self.data)
        Assert(nnorm > 0, "norm <= 0", FILE(), LINE())

        self.data /= nnorm
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    def print(self):
        # print(self.data)
        # print()
        for k, v in enumerate(self.states):
            print(v, self.data[k, 0])
            # print(v, np.asarray(self.data[k]).reshape(-1)[0])
    # ---------------------------------------------------------------------------------------------

    def __sub__(self, other):
        wf = copy.copy(self)

        wf.data -= other.data

        return wf

    def __add__(self, other):
        wf = copy.copy(self)

        wf.data += other.data

        return wf

    def __mul__(self, coeff):
        wf = copy.deepcopy(self)
        wf.data *= coeff
        # wf.print()
        # print()
        # self.print()
        # exit(0)
        return wf


# -------------------------------------------------------------------------------------------------
