import numpy as np
from PyQuantum.Common.Print import *
from PyQuantum.TC.State import *
from PyQuantum.TC.Cavity import *
import copy
from PyQuantum.Common.Matrix import *


def Across(capacity):
    Assert(capacity > 0, "capacity <= 0", cf())

    adiag = np.sqrt(np.arange(1, capacity+1))

    across = np.diagflat(adiag, -1)

    return across


def A(capacity):
    Assert(capacity > 0, "capacity <= 0", cf())

    adiag = np.sqrt(np.arange(1, capacity+1))

    a = np.diagflat(adiag, 1)

    return a


def AcrossA(capacity):
    Assert(capacity > 0, "capacity <= 0", cf())

    across = Across(capacity)
    a = A(capacity)

    acrossa = np.dot(across, a)

    return acrossa


class Hamiltonian:
    # ---------------------------------------------------------------------------------------------
    def __init__(self, capacity, cavity, RWA=True):
        Assert(isinstance(capacity, int), "capacity is not integer", cf())
        Assert(capacity > 0, "capacity <= 0", cf())

        Assert(isinstance(cavity, Cavity), "cavity is not Cavity", cf())

        self.capacity = capacity
        self.cavity = cavity
        self.n = cavity.n

        self.get_states()

        self.size = len(self.states)
        self.matrix = Matrix(self.size, self.size, dtype=np.complex128)

        # ------------------------------------------------------------------------------------------------------------------
        H_field = self.get_H_field()
        H_atoms = self.get_H_atoms()

        H = H_field + H_atoms

        if RWA:
            H += self.get_H_int_RWA()
        else:
            H += self.get_H_int_EXACT()

        self.matrix.data = np.matrix(H)
        # ------------------------------------------------------------------------------------------------------------------

    def get_H_field(self):
        # ------------------------------------------------------------------------------------------------------------------
        acrossa = AcrossA(self.capacity)
        # ------------------------------------------------------------------------------------------------------------------
        H_dim = (self.capacity+1) * pow(2, self.cavity.n)
        # ------------------------------------------------------------------------------------------------------------------
        at_dim = pow(2, self.cavity.n)

        I_at = np.identity(at_dim)
        # ------------------------------------------------------------------------------------------------------------------
        H_field = self.cavity.wc * np.kron(acrossa, I_at)

        # ------------------------------------------------------------------------------------------------------------------
        return H_field

    def get_H_atoms(self):
        # ------------------------------------------------------------------------------------------------------------------
        sigmadiag = [1]

        sigmacross = np.diagflat(sigmadiag, -1)
        sigma = np.diagflat(sigmadiag, 1)
        sigmacrosssigma = np.dot(sigmacross, sigma)
        # ------------------------------------------------------------------------------------------------------------------
        ph_dim = self.capacity+1

        I_ph = np.identity(ph_dim)
        # ------------------------------------------------------------------------------------------------------------------
        H_dim = (self.capacity+1) * pow(2, self.cavity.n)

        H_atoms = np.zeros([H_dim, H_dim])
        # ------------------------------------------------------------------------------------------------------------------
        for i in range(1, self.cavity.n+1):
            elem = sigmacrosssigma

            at_prev = np.identity(pow(2, i-1))
            elem = np.kron(at_prev, elem)

            at_next = np.identity(pow(2, self.cavity.n-i))
            elem = np.kron(elem, at_next)

            H_atoms += self.cavity.wa * np.kron(I_ph, elem)
        # ------------------------------------------------------------------------------------------------------------------
        return H_atoms

    def get_H_int_RWA(self):
        # ------------------------------------------------------------------------------------------------------------------
        across = Across(self.capacity)
        a = A(self.capacity)
        acrossa = AcrossA(self.capacity)
        # ------------------------------------------------------------------------------------------------------------------
        sigmadiag = [1]

        sigmacross = np.diagflat(sigmadiag, -1)
        sigma = np.diagflat(sigmadiag, 1)
        sigmacrosssigma = np.dot(sigmacross, sigma)
        # ------------------------------------------------------------------------------------------------------------------
        H_dim = (self.capacity+1) * pow(2, self.cavity.n)

        H_int = np.zeros([H_dim, H_dim])
        # ------------------------------------------------------------------------------------------------------------------
        for i in range(1, self.cavity.n+1):
            # ------------------------------------------------
            elem = across

            before = np.identity(pow(2, i-1))
            elem = np.kron(elem, before)

            elem = np.kron(elem, sigma)

            after = np.identity(pow(2, self.cavity.n-i))
            elem = np.kron(elem, after)

            H_int += self.cavity.g * elem
            # ------------------------------------------------
            elem = a

            before = np.identity(pow(2, i-1))
            elem = np.kron(elem, before)

            elem = np.kron(elem, sigmacross)

            after = np.identity(pow(2, self.cavity.n-i))
            elem = np.kron(elem, after)

            H_int += self.cavity.g * elem
            # ------------------------------------------------
        # ------------------------------------------------------------------------------------------------------------------
        return H_int

    def get_H_int_EXACT(self):
        # ------------------------------------------------------------------------------------------------------------------
        across = Across(self.capacity)
        a = A(self.capacity)
        acrossa = np.dot(across, a)
        # ------------------------------------------------------------------------------------------------------------------
        sigmadiag = [1]

        sigmacross = np.diagflat(sigmadiag, -1)
        sigma = np.diagflat(sigmadiag, 1)
        sigmacrosssigma = np.dot(sigmacross, sigma)
        # ------------------------------------------------------------------------------------------------------------------
        H_dim = (self.capacity+1) * pow(2, self.cavity.n)

        H_int = np.zeros([H_dim, H_dim], dtype=complex)
        # ------------------------------------------------------------------------------------------------------------------
        for i in range(1, self.cavity.n+1):
            # ------------------------------------------------
            elem = (across + a)

            before = np.identity(pow(2, i-1))
            elem = np.kron(elem, before)

            elem = np.kron(elem, sigmacross + sigma)

            after = np.identity(pow(2, self.cavity.n-i))
            elem = np.kron(elem, after)

            H_int += self.cavity.g * elem
            # ------------------------------------------------
        # ------------------------------------------------------------------------------------------------------------------
        return H_int

    # ---------------------------------------------------------------------------------------------
    def get_states(self):
        state = State(self.capacity, self.cavity.n)

        self.states = {}

        cnt = 0
        self.states[cnt] = copy.copy(state.state())

        while state.inc():
            cnt += 1
            self.states[cnt] = copy.copy(state.state())
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    def print_states(self):
        print("States:", color="green")

        print()

        for k, v in self.states.items():
            print(v)

        print()
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    def print(self):
        print(self.matrix.data)
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    def write_to_file(self, filename):
        self.matrix.write_to_file(filename)
    # ---------------------------------------------------------------------------------------------
