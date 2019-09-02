import numpy as np
import pandas as pd

from PyQuantum.Common.Matrix import *
from PyQuantum.Tools.Hz import *
from PyQuantum.TC.Basis import Basis
from scipy.sparse import identity, kron


class Hamiltonian(Matrix):
    def __init__(self, capacity, cavity, RWA=True):
        self.capacity = capacity
        self.cavity = cavity

        basis = Basis(capacity, cavity.n_atoms, cavity.n_levels)

        self.states = basis.basis

        # self.print_states()
        # -------------------------------------------------------------------------------------------------------------
        H_field = self.get_Hfield(capacity, cavity.n_atoms, cavity.n_levels, cavity.wc, cavity.wa, cavity.g)

        H_atoms = self.get_Hatoms(capacity, cavity.n_atoms, cavity.n_levels, cavity.wc, cavity.wa, cavity.g)

        if RWA:
            H_int = self.get_Hint_RWA(capacity, cavity.n_atoms, cavity.n_levels, cavity.wc, cavity.wa, cavity.g)
        else:
            H_int = self.get_Hint_EXACT(capacity, cavity.n_atoms, cavity.n_levels, cavity.wc, cavity.wa, cavity.g)

        Assert(np.shape(H_field) == np.shape(H_atoms), "size mismatch", FILE(), LINE())
        Assert(np.shape(H_atoms) == np.shape(H_int), "size mismatch", FILE(), LINE())

        H = H_field + H_atoms + H_int

        self.size = np.shape(H)[0]

        # print(self.size, len(self.states))

        Assert(self.size == len(self.states), "size mismatch", FILE(), LINE())

        super(Hamiltonian, self).__init__(m=self.size, n=self.size, dtype=np.longdouble)

        self.data = H

        self.get_states_bin()

    def get_states_bin(self):
        states_bin = {}

        for k, v in enumerate(self.states):
            en = v[0] + np.sum(v[1])

            if en not in states_bin:
                states_bin[en] = []

            states_bin[en].append(k)

        self.states_bin = states_bin

    def get_Hfield(self, capacity, at_count, n_levels, wc, wa, g):
        # ------------------------------------------------------------------------------------------------------------------
        adiag = np.sqrt(np.arange(1, capacity+1))

        across = np.diagflat(adiag, -1)
        a = np.diagflat(adiag, 1)
        acrossa = np.dot(across, a)
        # ------------------------------------------------------------------------------------------------------------------
        H_dim = (capacity+1) * pow(n_levels, at_count)
        # ------------------------------------------------------------------------------------------------------------------
        # at_dim = pow(2, at_count)
        at_dim = pow(n_levels, at_count)

        I_at = identity(at_dim)
        # ------------------------------------------------------------------------------------------------------------------
        H_field = wc * kron(acrossa, I_at)
        # ------------------------------------------------------------------------------------------------------------------
        return H_field

    def get_Hatoms(self, capacity, at_count, n_levels, wc, wa, g):
        # ------------------------------------------------------------------------------------------------------------------
        sigmadiag = range(1, n_levels)
        sigmacross = np.diagflat(sigmadiag, -1)
        sigma = np.diagflat(sigmadiag, 1)
        sigmacrosssigma = np.dot(sigmacross, sigma)
        # ------------------------------------------------------------------------------------------------------------------
        ph_dim = capacity+1

        I_ph = np.identity(ph_dim)
        # ------------------------------------------------------------------------------------------------------------------
        H_dim = (capacity+1) * pow(n_levels, at_count)

        H_atoms = np.zeros([H_dim, H_dim])
        # ------------------------------------------------------------------------------------------------------------------
        for i in range(1, at_count+1):
            elem = sigmacrosssigma

            at_prev = identity(pow(n_levels, i-1))
            elem = kron(at_prev, elem)

            at_next = identity(pow(n_levels, at_count-i))
            elem = kron(elem, at_next)

            H_atoms += wa * kron(I_ph, elem)
        # ------------------------------------------------------------------------------------------------------------------
        return H_atoms

    def get_Hint_RWA(self, capacity, at_count, n_levels, wc, wa, g):
        # ------------------------------------------------------------------------------------------------------------------
        adiag = np.sqrt(np.arange(1, capacity+1))

        across = np.diagflat(adiag, -1)
        a = np.diagflat(adiag, 1)
        acrossa = np.dot(across, a)
        # ------------------------------------------------------------------------------------------------------------------
        sigmadiag = range(1, n_levels)

        sigmacross = np.diagflat(sigmadiag, -1)
        sigma = np.diagflat(sigmadiag, 1)
        sigmacrosssigma = np.dot(sigmacross, sigma)
        # ------------------------------------------------------------------------------------------------------------------
        H_dim = (capacity+1) * pow(n_levels, at_count)

        H_int = np.zeros([H_dim, H_dim])
        # ------------------------------------------------------------------------------------------------------------------
        for i in range(1, at_count+1):
            # ------------------------------------------------
            elem = across

            before = identity(pow(n_levels, i-1))
            elem = kron(elem, before)

            elem = kron(elem, sigma)

            after = identity(pow(n_levels, at_count-i))
            elem = kron(elem, after)

            H_int += g * elem
            # ------------------------------------------------
            elem = a

            before = identity(pow(n_levels, i-1))
            elem = kron(elem, before)

            elem = kron(elem, sigmacross)

            after = identity(pow(n_levels, at_count-i))
            elem = kron(elem, after)

            H_int += g * elem
            # ------------------------------------------------
        # ------------------------------------------------------------------------------------------------------------------
        return H_int

    # -----------------------------------------------------------------------------------------------------------------
    def print_states(self):
        print("Basis:\n", color="green")

        for i in self.states:
            print(i)

        print()
    # -----------------------------------------------------------------------------------------------------------------

    def print(self):
        for i in range(self.size):
            for j in range(self.size):
                print(round(self.data[i, j] / self.cavity.wc, 3), end='\t')
                # print(to_Hz(self.data[i, j]), end='\t')

            print()

# =====================================================================================================================
# class Hamiltonian:
#     def __init__(self, capacity, cavity, RWA=True, reduced=True):
#         self.capacity = capacity
#         self.cavity = cavity

#         self.size = 0

#         HC = {}

#         size_start = 0

#         self.states = {}
#         self.states_dim = []

#         for c in range(capacity, -1, -1):
#             print("c=", c)
#             Hc = H(capacity=c, cavity=cavity,
#                    RWA=RWA, reduced=reduced)
#             HC[c] = Hc
#             self.states_dim.append(len(Hc.states))
#             # print(Hc.states)
#             for k, v in Hc.states.items():
#                 self.states[size_start + k] = v

#             size_start += HC[c].size

#             self.size += Hc.size

#         # self.print_states()
#         # return
#         I = lil_matrix((self.size, self.size), dtype=np.double)
#         # I = np.zeros([self.size, self.size], dtype=np.double)

#         size_start = 0

#         for c in range(capacity, -1, -1):
#             I[size_start:size_start+HC[c].size,
#                 size_start:size_start+HC[c].size] = HC[c].matrix.data
#             size_start += HC[c].size

#         self.matrix = Matrix(self.size, self.size, dtype=np.double)
#         self.matrix.data = I
#         print("H done ...")

#     def print_states(self):
#         for k, v in self.states.items():
#             print(k, ": ", v, sep="")

#     # def iprint(self):
#     # #     df = pd.DataFrame()

#     # #     for i in range(self.size):
#     # #         for j in range(self.size):
#     # #             df.loc[i, j] = wc_str(abs(self.matrix.data[i, j]))

#     # #     # df.index = df.columns = self.states_str
#     # #     df.index = df.columns = [str(v) for v in self.states.values()]

#     # #     self.df = df

#     def to_html(self, filename):
#         self.matrix.states = self.states
#         self.matrix.to_html(filename)

#     #     self.df.to_html(filename)
# =====================================================================================================================
