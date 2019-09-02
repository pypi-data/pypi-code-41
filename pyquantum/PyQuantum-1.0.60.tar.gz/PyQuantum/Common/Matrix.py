import numpy as np
import pandas as pd
from PyQuantum.Tools.Assert import *
from PyQuantum.Common.STR import *
from scipy.sparse import lil_matrix, csc_matrix

precision = 5
eps = 1.0 / (10 ** precision)


class Matrix:
    # ---------------------------------------------------------------------------------------------

    def __init__(self, m, n, dtype):
        Assert(m > 0, "m <= 0", FILE(), LINE())
        Assert(n > 0, "n <= 0", FILE(), LINE())

        self.m = m
        self.n = n

        self.dtype = dtype

        self.data = lil_matrix((m, n), dtype=dtype)

        # self.data = np.matrix(
        #     np.zeros([m, n]),
        #     dtype=dtype
        # )
    # ---------------------------------------------------------------------------------------------

    def print(self, precision=3):
        for i in range(self.m):
            for j in range(self.n):
                print(np.round(abs(self.data[i, j]), precision), end='\t')
                # print(np.round(abs((config.l * L)[i, j]), 3), end='\t')

            print()
    # ---------------------------------------------------------------------------------------------

    def conj(self):
        conj_matrix = Matrix(m=self.m, n=self.n, dtype=self.dtype)
        conj_matrix.data = self.data.getH()

        return conj_matrix
    # ---------------------------------------------------------------------------------------------

    def is_hermitian(self):
        return np.all(ro == ro.getH())
    # ---------------------------------------------------------------------------------------------

    def check_hermiticity(ro):
        Assert(self.is_hermitian(), "not hermitian", FILE(), LINE())
    # ---------------------------------------------------------------------------------------------

    def abs_trace(self):
        return np.sum(np.abs(self.data.diagonal()))
    # ---------------------------------------------------------------------------------------------
    # def print(self):
    #     print(self.data)

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
    def to_csv(self, filename, precision=5):
        if self.dtype == np.complex128:
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
        else:
            with open(filename, "w") as f:
                for i in range(0, self.m):
                    for j in range(0, self.n):
                        value = self.data[i, j]

                        if abs(value) < eps:
                            re = format(+0, "." + str(precision) + "f")
                        else:
                            re = format(value, "." + str(precision) + "f")

                        f.write(re)

                        if j != self.n - 1:
                            f.write(",")

                    f.write("\n")
        return
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    def check_hermiticity(self):
        Assert(np.all(abs(self.data - self.data.getH()) < eps),
               "matrix is not hermitian", FILE(), LINE())
    # ---------------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------------------
    def check_unitarity(self):
        data = self.data
        data_H = self.data.getH()

        I = np.eye(len(data))

        Assert(np.all(abs(data.dot(data_H) - I) < eps)
               and np.all(abs(data_H.dot(data) - I) < eps), "matrix is not unitary", FILE(), LINE())

        return
    # -------------------------------------------------------------------------------------------------

    def normalize(self):
        self.data /= np.norm(self.data)

    def iprint(self, metric=None):
        df = pd.DataFrame()

        for i in range(self.m):
            for j in range(self.n):
                if metric is None:
                    df.loc[i, j] = str(int(abs(self.data[i, j])))
                    # df.loc[i, j] = str(12)
                    # df.loc[i, j] = int(abs(self.data[i, j]))
                    # if df.loc[i, j] == int(df.loc[i, j]):
                    # df.loc[i, j] = int(df.loc[i, j])
                else:
                    df.loc[i, j] = wc_str(abs(self.data[i, j]))

        # df.index = df.columns = self.states_str
        if self.states is not None:
            df.index = df.columns = [str(v) for v in self.states.values()]

        self.df = df

    def to_html(self, filename):
        self.iprint()
        self.df.to_html(filename)

    # def sub_row(self, i, j):
        # i -= j

    def remove_empty_rows(self):
        for i in range(self.m-1, -1, -1):
            if np.all(self.data[i] == np.zeros(self.n)):
                self.data = np.delete(self.data, i, axis=0)
                # gray.remove(gray[i])
                self.m -= 1

    def remove_empty_cols(self):
        # pass
        self.data = np.transpose(self.data)
        self.m, self.n = self.n, self.m
        self.remove_empty_rows()
        self.m, self.n = self.n, self.m
        # print(self.m, self.n)
        self.data = np.transpose(self.data)

        # matrix = np.transpose(self.data)

    # def swap_cols(self, j1, j2):
    #     print('m=', self.m)
    #     for i in range(self.m):
    #         self.data[i, j1], self.data[i,
    #                                     j2] = self.data[i, j2], self.data[i, j1]

    def swap_rows(self, i, j):
        # self.data[[i]] = self.data[[j]]
        self.data[[i]], self.data[[j]] = self.data[[j]], self.data[[i]]

        return

    def swap_cols(self, j1, j2):
        for i in range(self.m):
            self.data[i][j1], self.data[i][j2] = self.data[i][j2], self.data[i][j1]

        return

    def remove_row(self, k):
        # print(self.data[k])
        self.data = np.delete(self.data, k, axis=0)

    def steps(self):
        I = 0
        J = 0

        while I < self.m and J < self.n:
            # print(I, J)
            found = False

            if self.data[I][J] == 0:
                for i1 in range(I, self.m):
                    if self.data[i1][J] != 0:
                        # print('swap', i1, I)
                        self.swap_rows(i1, I)
                        self.gray[i1], self.gray[I] = self.gray[I], self.gray[i1]
                        # self.print()
                        # exit(0)
                        found = True
                        break

                if not found:
                    J += 1
                    continue

            k = self.data[I][J]
            for j1 in range(self.n):
                self.data[I][j1] /= k

            for i1 in range(self.m):
                if i1 != I:
                    self.data[i1] -= self.data[I] * self.data[i1][J]

            I += 1
            J += 1
            if I == self.m or J == self.n:
                break

        for t in range(self.m-1, I-1, -1):
            self.data = np.delete(self.data, t, axis=0)
            # print(t, len(gray), gray[t], len(gray), gray[t] in gray)
            self.gray = np.delete(self.gray, t, axis=0)
            self.m -= 1

        return

    def row2_rank(self):
        i = 0
        j = 0

        while i < self.m and j < self.n:
            if self.data[i][j] == 0:
                found = False

                for i1 in range(self.m):
                    if i1 != i and self.data[i1, j] != 0:
                        self.data[[i1, i]] = self.data[[i, i1]]
                        found = True
                        break

                if not found:
                    j += 1
                    continue

            # if j >= n_-1:
                # break

            self.data[i] /= self.data[i][j]

            for i1 in range(self.m):
                if i1 != i:
                    self.data[[i1]] -= self.data[[i1]] * self.data[i1, j]

            # for j1 in range(j+1, self.n):
            #     for t in range(self.m):
            #         self.data[t, j1] -= self.data[t, j] * self.data[i, j1]
            # self.print()
            # print('swap', i, j)
            self.swap_cols(i, j)
            # self.print()
            # exit(0)
            i += 1
            j += 1

        self.remove_empty_rows()
        # self.remove_empty_cols()
