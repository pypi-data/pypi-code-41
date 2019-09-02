import numpy as np
import pandas as pd

from PyQuantum.Common.Matrix import *
from PyQuantum.TC.FullBase import *


class HamiltonianL:
    def set_base(self, base):
        self.base = base

    def __init__(self, capacity, cavity, RWA=True, reduced=True):
        self.capacity = capacity
        self.cavity = cavity

        self.size = 0

        HC = {}

        size_start = 0

        self.states = {}

        for c in range(capacity, -1, -1):
            Hc = Hamiltonian(capacity=c, cavity=cavity,
                             RWA=RWA, reduced=reduced)
            HC[c] = Hc

            for i in Hc.base.base:
                # for i in Hc.states.values():
                print(i)
            print()
            for k, v in Hc.states.items():
                self.states[size_start + k] = v

            size_start += HC[c].size
            # self.states += Hc.states
            # print(Hc.states)
            self.size += Hc.size

        # for i in self.states.values():
        #     print(i)

        I = np.zeros([self.size, self.size], dtype=np.complex128)
        # print(self.states)

        size_start = 0

        for c in range(capacity, -1, -1):
            # print("c=", c)
            # print(HC[c])
            # print(HC[c].size)
            # print(HC[c].states)
            # print(HC[c].matrix.data)
            I[size_start:size_start+HC[c].size,
                size_start:size_start+HC[c].size] = HC[c].matrix.data
            size_start += HC[c].size

        self.matrix = Matrix(self.size, self.size, dtype=np.complex128)
        self.matrix.data = I

        # exit(0)

    def iprint(self):
        df = pd.DataFrame()

        for i in range(self.size):
            for j in range(self.size):
                df.loc[i, j] = wc_str(abs(self.matrix.data[i, j]))

        # df.index = df.columns = self.states_str
        df.index = df.columns = [str(v) for v in self.states.values()]

        self.df = df
        # print(I)
        # exit(0)
        # for c in range(capacity):
        #     I[0:size_1, 0:size_1] = H0

        #     I[size_1:size_1+size_2, size_1:size_1+size_2] = H1

        #     I[size_1+size_2:size, size_1+size_2:size] = H2

        # self.matrix = Matrix(self.size, self.size, dtype=np.complex128)

        # H2 = Hamiltonian(capacity-1, cavity, RWA, reduced).matrix.data
        # H3 = Hamiltonian(capacity-2, cavity, RWA, reduced).matrix.data

        # print(self.size)
        # H_field = get_Hfield(capacity, cavity.n_atoms, cavity.n_levels,
        #                      cavity.wc, cavity.wa, cavity.g)

        # H_atoms = get_Hatoms(capacity, cavity.n_atoms, cavity.n_levels,
        #                      cavity.wc, cavity.wa, cavity.g)

        # if RWA:
        #     H_int = get_Hint_RWA(
        #         capacity, cavity.n_atoms, cavity.n_levels, cavity.wc, cavity.wa, cavity.g)
        # else:
        #     H_int = get_Hint_EXACT(
        #         capacity, cavity.n_atoms, cavity.n_levels, cavity.wc, cavity.wa, cavity.g)

        # Assert(np.shape(H_field) == np.shape(H_atoms), "size mismatch", cf())
        # Assert(np.shape(H_atoms) == np.shape(H_int), "size mismatch", cf())

        # H = np.matrix(H_field + H_atoms + H_int)

        # self.size = np.shape(H)[0]

        # self.matrix = Matrix(self.size, self.size, dtype=np.complex128)
        # self.matrix.data = H

        # at = AtomicBasis(count=cavity.n_atoms, n_levels=cavity.n_levels)
        # base = Base(capacity, at)

        # self.set_base(base)

        # if reduced:
        #     self.reduce()

        # print(self.matrix.data)

        # exit(1)

        # self.set_states()


class Hamiltonian:
    def set_base(self, base):
        self.base = base

    def __init__(self, capacity, cavity, RWA=True, reduced=True):
        self.capacity = capacity
        self.cavity = cavity

        H_field = get_Hfield(capacity, cavity.n_atoms, cavity.n_levels,
                             cavity.wc, cavity.wa, cavity.g)

        H_atoms = get_Hatoms(capacity, cavity.n_atoms, cavity.n_levels,
                             cavity.wc, cavity.wa, cavity.g)

        if RWA:
            H_int = get_Hint_RWA(
                capacity, cavity.n_atoms, cavity.n_levels, cavity.wc, cavity.wa, cavity.g)
        else:
            H_int = get_Hint_EXACT(
                capacity, cavity.n_atoms, cavity.n_levels, cavity.wc, cavity.wa, cavity.g)

        Assert(np.shape(H_field) == np.shape(H_atoms), "size mismatch", cf())
        Assert(np.shape(H_atoms) == np.shape(H_int), "size mismatch", cf())

        H = np.matrix(H_field + H_atoms + H_int)

        self.size = np.shape(H)[0]

        self.matrix = Matrix(self.size, self.size, dtype=np.complex128)
        self.matrix.data = H

        at = AtomicBasis(count=cavity.n_atoms, n_levels=cavity.n_levels)
        base = Base(capacity, at)

        self.set_base(base)

        if reduced:
            self.reduce()

        # print(self.matrix.data)

        # exit(1)

        self.set_states()

    # ---------------------------------------------------------------------------------------------

    def iprint(self):
        df = pd.DataFrame()

        for i in range(self.size):
            for j in range(self.size):
                df.loc[i, j] = wc_str(abs(self.matrix.data[i, j]))

        # df.index = df.columns = self.states_str
        # df.index = df.columns = self.base.base_str

        self.df = df

    def to_html(self, filename):
        self.iprint()

        self.df.to_html("basis.html")

    # ---------------------------------------------------------------------------------------------

    def reduce(self):
        for k, v in list(enumerate(self.base.base))[::-1]:
            if v[0] + np.sum(v[1]) != self.capacity:
                self.matrix.data = np.delete(self.matrix.data, k, axis=0)
                self.matrix.data = np.delete(self.matrix.data, k, axis=1)
                self.base.base.remove(v)
                self.base.base_str.remove(str(v))

        self.size = np.shape(self.matrix.data)[0]

    def set_states(self):
        self.states = {}

        for k, v in enumerate(self.base.base):
            self.states[k] = v


def get_Hfield(capacity, at_count, n_levels, wc, wa, g):
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

    I_at = np.identity(at_dim)
    # ------------------------------------------------------------------------------------------------------------------
    H_field = wc * np.kron(acrossa, I_at)
    # ------------------------------------------------------------------------------------------------------------------
    return H_field


def get_Hatoms(capacity, at_count, n_levels, wc, wa, g):
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

        at_prev = np.identity(pow(n_levels, i-1))
        elem = np.kron(at_prev, elem)

        at_next = np.identity(pow(n_levels, at_count-i))
        elem = np.kron(elem, at_next)

        H_atoms += wa * np.kron(I_ph, elem)
    # ------------------------------------------------------------------------------------------------------------------
    return H_atoms


def get_Hint_RWA(capacity, at_count, n_levels, wc, wa, g):
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

        before = np.identity(pow(n_levels, i-1))
        elem = np.kron(elem, before)

        elem = np.kron(elem, sigma)

        after = np.identity(pow(n_levels, at_count-i))
        elem = np.kron(elem, after)

        H_int += g * elem
        # ------------------------------------------------
        elem = a

        before = np.identity(pow(n_levels, i-1))
        elem = np.kron(elem, before)

        elem = np.kron(elem, sigmacross)

        after = np.identity(pow(n_levels, at_count-i))
        elem = np.kron(elem, after)

        H_int += g * elem
        # ------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    return H_int


def get_Hint_EXACT(capacity, at_count, n_levels, wc, wa, g):
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

    H_int = np.zeros([H_dim, H_dim], dtype=complex)
    # ------------------------------------------------------------------------------------------------------------------
    for i in range(1, at_count+1):
        # ------------------------------------------------
        elem = (across + a)

        before = np.identity(pow(n_levels, i-1))
        elem = np.kron(elem, before)

        elem = np.kron(elem, sigmacross + sigma)

        after = np.identity(pow(n_levels, at_count-i))
        elem = np.kron(elem, after)

        H_int += g * elem
        # ------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    return H_int
