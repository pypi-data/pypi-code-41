import numpy as np
import pandas as pd

from PyQuantum.Common.Matrix import *
from PyQuantum.TC.FullBase import *
from PyQuantum.TC.Hamiltonian import Hamiltonian as H


class Hamiltonian:
    def __init__(self, capacity, cavity, RWA=True, reduced=True):
        self.capacity = capacity
        self.cavity = cavity

        self.size = 0

        HC = {}

        size_start = 0

        self.states = {}

        for c in range(capacity, -1, -1):
            print("c=", c)
            Hc = H(capacity=c, cavity=cavity,
                   RWA=RWA, reduced=reduced)
            HC[c] = Hc

            for k, v in Hc.states.items():
                self.states[size_start + k] = v

            size_start += HC[c].size

            self.size += Hc.size
        print("_H done")
        I = np.zeros([self.size, self.size], dtype=np.complex128)

        size_start = 0

        for c in range(capacity, -1, -1):
            I[size_start:size_start+HC[c].size,
                size_start:size_start+HC[c].size] = HC[c].matrix.data
            size_start += HC[c].size

        self.matrix = Matrix(self.size, self.size, dtype=np.complex128)
        self.matrix.data = I

    def print_states(self):
        for k, v in self.states.items():
            print(k, ": ", v, sep="")

    # def iprint(self):
        # self.matrix.ipri
    # def iprint(self):
    # #     df = pd.DataFrame()

    # #     for i in range(self.size):
    # #         for j in range(self.size):
    # #             df.loc[i, j] = wc_str(abs(self.matrix.data[i, j]))

    # #     # df.index = df.columns = self.states_str
    # #     df.index = df.columns = [str(v) for v in self.states.values()]

    # #     self.df = df

    def to_html(self, filename):
        self.matrix.states = self.states
        self.matrix.to_html(filename)

    #     self.df.to_html(filename)
