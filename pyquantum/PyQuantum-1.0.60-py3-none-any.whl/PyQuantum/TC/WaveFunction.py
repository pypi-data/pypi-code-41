# -------------------------------------------------------------------------------------------------
# scientific
import numpy as np
# -------------------------------------------------------------------------------------------------
# Common
from PyQuantum.Common.Assert import *
from PyQuantum.Common.Matrix import *
# -------------------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------------------
class WaveFunction(Matrix):

    # ---------------------------------------------------------------------------------------------
    def __init__(self, states, init_state, amplitude=1):
        Assert(isinstance(states, dict), "states is not dict", cf())
        Assert(isinstance(init_state, list), "init_state is not list", cf())

        Assert(len(states) > 1, "w_0 is not set", cf())

        self.states = states

        k_found = None

        # print(states)
        # print(init_state)
        for k, v in states.items():
            if init_state == v:
                k_found = k

                break

        Assert(k_found is not None, "w_0 is not set", cf())

        super(WaveFunction, self).__init__(
            m=len(states), n=1, dtype=np.complex128)

        self.data[k_found] = amplitude
    # ---------------------------------------------------------------------------------------------

    def set_ampl(self, state, amplitude=1):
        k_found = None

        for k, v in self.states.items():
            print(state, v)
            if state == v:
                k_found = k

                break

        Assert(k_found is not None, "w_0 is not set", cf())
        self.data[k_found] = amplitude

    # ---------------------------------------------------------------------------------------------
    def normalize(self):
        norm = np.linalg.norm(self.data)

        Assert(norm > 0, "norm <= 0", cf())

        self.data /= norm
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    def print(self):
        for k, v in self.states.items():
            print(v, np.asarray(self.data[k]).reshape(-1)[0])
    # ---------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------
