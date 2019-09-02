import numpy as np
import pandas as pd
from PyQuantum.Common.Assert import *
from PyQuantum.Common.STR import *

precision = 5
eps = 1.0 / (10 ** precision)


class Matrix:
    # ---------------------------------------------------------------------------------------------

    def __init__(self, m, n, dtype):
        Assert(m > 0, "m <= 0", cf())
        Assert(n > 0, "n <= 0", cf())

        self.m = m
        self.n = n

        self.data = np.matrix(
            np.zeros([m, n]),
            dtype=dtype
        )
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    def conj(self):
        return self.data.getH()
    # ---------------------------------------------------------------------------------------------

    def is_hermitian(self):
        return np.all(ro == ro.getH())
    # ---------------------------------------------------------------------------------------------

    def check_hermiticity(ro):
        Assert(self.is_hermitian(), "not hermitian", cf())
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    def print(self):
        print(self.data)

        return
    # ---------------------------------------------------------------------------------------------

    def set_header(self, header):
        self.header = header

    def print_pd(self):
        size = len(str(self.header[0])) + 1

        print(' ' * (len(str(self.header[0])) + 1), end='')

        for k, v in self.header.items():
            print(v, end=' ')

        print()

        for i in range(self.m):
            print(self.header[i], end=' ')

            for j in range(self.n):
                s = wc_str_v(self.data[i, j].real, 3)

                print(s.rjust(size - 1, ' '), end=' ')

            print()

        print()

    # ---------------------------------------------------------------------------------------------
    def to_csv(self, filename):
        with open(filename, "w") as f:
            for i in range(0, self.m):
                for j in range(0, self.n):
                    value = self.data[i, j]

                    if abs(value.real) < eps:
                        re = format(+0, "." + str(precision) + "f")
                    else:
                        re = format(value.real, "." + str(precision) + "f")

                    if abs(value.imag) < eps:
                        im = format(+0, "." + str(precision) + "f")
                    else:
                        im = format(value.imag, "." + str(precision) + "f")

                    f.write("(" + re + "," + im + ")")

                    if j != self.n - 1:
                        f.write(",")

                f.write("\n")

        return
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    def check_hermiticity(self):
        Assert(np.all(abs(self.data - self.data.getH()) < eps),
               "matrix is not hermitian", cf())
    # ---------------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------------------
    def check_unitarity(self):
        data = self.data
        data_H = self.data.getH()

        I = np.eye(len(data))

        Assert(np.all(abs(data.dot(data_H) - I) < eps)
               and np.all(abs(data_H.dot(data) - I) < eps), "matrix is not unitary", cf())

        return
    # -------------------------------------------------------------------------------------------------

    def normalize(self):
        self.data /= np.norm(self.data)

    def iprint(self):
        df = pd.DataFrame()

        for i in range(self.m):
            for j in range(self.n):
                df.loc[i, j] = wc_str(abs(self.data[i, j]))

        # df.index = df.columns = self.states_str
        df.index = df.columns = [str(v) for v in self.states.values()]

        self.df = df

    def to_html(self, filename):
        self.iprint()

        self.df.to_html(filename)
