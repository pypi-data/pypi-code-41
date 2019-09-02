# -------------------------------------------------------------------------------------------------
# scientific
import numpy as np
# -------------------------------------------------------------------------------------------------
# system
from math import sqrt
from PyQuantum.Common.html import *
from PyQuantum.Bipartite.Cavity import Cavity
import copy
# -------------------------------------------------------------------------------------------------
# Common
from PyQuantum.Common.Matrix import *
from PyQuantum.Common.Assert import *
from PyQuantum.Common.Print import *
# -------------------------------------------------------------------------------------------------
import pandas as pd


class Hamiltonian:
    # ---------------------------------------------------------------------------------------------
    def __init__(self, capacity, cavity):
        Assert(isinstance(cavity, Cavity), "cavity is not Cavity", cf())
        Assert(isinstance(capacity, int), "capacity is not int", cf())
        Assert(capacity > 0, "capacity <=0", cf())

        self.cavity = cavity

        self.D = {}

        # ------------
        n = cavity.n

        wc = cavity.wc
        wa = cavity.wa
        g = cavity.g
        # ------------

        _min = min(capacity, n)

        self.states = {}

        # ---------------------------------------
        self.init_states(capacity, n)
        # ---------------------------------------

        self.size = len(self.states)
        self.matrix = Matrix(self.size, self.size, dtype=np.complex128)

        i = 1

        for i1 in range(0, _min + 1):
            for i2 in range(0, min(n, capacity - i1) + 1):
                j = 1

                for j1 in range(0, _min + 1):
                    for j2 in range(0, min(n, capacity - j1) + 1):
                        if i1 != j1:
                            p = [i1, j1]
                        elif i2 != j2:
                            p = [i2, j2]
                        else:
                            p = [1, 2]

                        mi = min(p[0], p[1])

                        kappa = sqrt((n - mi) * (mi + 1))

                        if abs(i1 - j1) + abs(i2 - j2) == 1:
                            _max = max(capacity - i1 - i2, capacity - j1 - j2)
                            self.matrix.data[i - 1, j - 1] = g * \
                                sqrt(max(capacity - i1 - i2,
                                         capacity - j1 - j2)) * kappa
                        elif abs(i1 - j1) + abs(i2 - j2) == 0:
                            self.matrix.data[i - 1, j -
                                             1] = (capacity - (i1 + i2)) * wc + (i1 + i2) * wa
                        else:
                            self.matrix.data[i - 1, j - 1] = 0

                        j += 1

                i += 1
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    def get_index(self, state):
        for k, v in self.states.items():
            if v == state:
                return k
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    def to_csv(self, filename):
        self.matrix.to_csv(filename)
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    def get_states(self):
        return self.states

    def init_states(self, capacity, n):
        _min = min(capacity, n)

        count = 0

        for i1 in range(0, _min + 1):
            for i2 in range(0, min(n, capacity - i1) + 1):
                self.states[count] = [i1, i2]

                count += 1

    # ---------------------------------------------------------------------------------------------
    def print_states(self, title="States:"):
        print(title, color="green")

        print()

        for k, v in self.states.items():
            print(v)

        print()
    # ---------------------------------------------------------------------------------------------


class St:

    def __init__(self, cv):
        self.capacity = cv.capacity
        self.n = cv.n

        self.n1 = 0
        self.n2 = 0

    def inc(self):
        if self.n2 < self.n and self.n1 + self.n2 < self.capacity:
            self.n2 += 1
        else:
            self.n2 = 0

            if self.n1 < self.n and self.n1 + self.n2 < self.capacity:
                self.n1 += 1
            else:
                return False

        return True

    def print(self):
        print("[" + str(self.n1) + "," + str(self.n2) + "]")
