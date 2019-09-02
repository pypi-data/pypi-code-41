# -------------------------------------------------------------------------------------------------
# scientific
import numpy as np
# -------------------------------------------------------------------------------------------------
# system
from math import sqrt
from PyQuantum.Common.html import *
import copy
# -------------------------------------------------------------------------------------------------
# Common
from PyQuantum.Common.Matrix import *
from PyQuantum.Common.Assert import *
from PyQuantum.Common.Print import *
from PyQuantum.Common.Tools import print_error
# -------------------------------------------------------------------------------------------------
import html


def a_cross(ph):
    return sqrt(ph + 1)


def a(ph):
    return sqrt(ph)

# -------------------------------------------------------------------------------------------------


class Hamiltonian:

    def __init__(self, capacity, cavity):
        Assert(isinstance(capacity, int), "capacity is not integer", cf())
        Assert(capacity > 0, "capacity <= 0", cf())

        # Assert(isinstance(cavity, "BipartiteGeneral.Cavity.Cavity"), "capacity is not integer", cf())

        self.capacity = capacity
        self.cavity = cavity

        self.n = cavity.n

        self.wc = cavity.wc
        self.wa = cavity.wa
        self.g = cavity.g

        self.states = self.get_states()
        self.get_states_bin()
        # self.print_states()

        self.size = len(self.states)

        self.matrix = Matrix(self.size, self.size, dtype=np.complex128)
        # self.matrix_html = np.empty([self.size, self.size], dtype=">U900")

        for i in range(self.size):
            i_state = self.states[i]

            i_ph = i_state[0]
            i_at = i_state[1]

            for j in range(self.size):
                j_state = self.states[j]

                j_ph = j_state[0]
                j_at = j_state[1]

                # self.matrix_html[i, j] = ""

                if i_state == j_state:
                    self.matrix.data[i, j] = self.wc * i_ph
                    # if(self.matrix_html[i][j] != ""):
                    # self.matrix_html[i][j] += "+"
                    # self.matrix_html[i][j] += "wc" + DOT() + str(i_ph) + " "

                    for n_ in range(len(i_at)):
                        if i_at[n_] != 0:
                            self.matrix.data[i, j] += self.wa[n_] * i_at[n_]

                            # if(self.matrix_html[i][j] != ""):
                            # self.matrix_html[i][j] += "+"
                            # self.matrix_html[i][j] += "wa" + SUB(n_) + DOT() + str(i_at[n_]) + " "
                else:
                    d_ph = j_ph - i_ph

                    if abs(d_ph) == 1:
                        diff_at_cnt = 0

                        for n_ in range(len(i_at)):
                            d_at = j_at[n_] - i_at[n_]

                            if d_ph + d_at == 0:
                                diff_at_cnt += 1
                                diff_at_num = n_
                            elif d_at != 0:
                                diff_at_cnt = 0
                                break

                            if diff_at_cnt > 1:
                                break

                        if diff_at_cnt == 1:
                            if d_ph > 0:
                                k = a_cross(i_ph) * i_at[diff_at_num]

                                self.matrix.data[i,
                                                 j] = self.g[diff_at_num] * k
                                # self.matrix_html[i][j] = "g" + SUB(diff_at_num) + DOT() + A_CROSS(i_ph) + \
                                # """<math display="block"><mrow><msqrt><mn> &middot; """ + \
                                # A_CROSS(i_ph) + """</mn></msqrt><mo>=</mo></mrow></math>"""
                            else:
                                k = a_cross(j_ph) * j_at[diff_at_num]

                                self.matrix.data[i,
                                                 j] = self.g[diff_at_num] * k
                                # self.matrix_html[i][j] = "g" + SUB(diff_at_num) + DOT() + A_CROSS(j_ph)

        self.matrix.check_hermiticity()

        return
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    def print_html(self, filename):
        states = self.states

        # st = list(states.values())

        # for i in range(0, len(st)):
        #     st[i] = str(st[i])

        # pd.options.display.max_colwidth = 999

        # df = pd.DataFrame(self.matrix_html, columns=st, index=st, dtype=str)
        # f = open(filename, "w")

        # style = """
        # <style >
        #     .dataframe th, td {
        #         padding: 10px;
        #         text - align: center;
        #         # min-width:200px;
        #         white - space: nowrap;
        #         word-break: keep-all;}
        # < / style > """

        # script = """
        # <script type = "text/javascript" src = "http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML" > < / script >
        # """

        # f.write(style + script + df.to_html(escape=False))
        # webbrowser.open(filename)

        # f.close()

        return
    # -------------------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------------------
    def to_csv(self, filename):
        self.matrix.to_csv(filename)

        return
    # -------------------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------------------
    def get_states(self):
        self.states = {}

        state = [self.capacity, [0] * self.n]
        cnt = 0

        self.states[cnt] = copy.deepcopy(state)
        cnt += 1

        state[0] -= 1

        while(1):
            inced = False

            for n_ in range(self.n - 1, -1, -1):
                if state[1][n_] == 1:
                    state[1][n_] = 0

                    continue

                if state[0] + np.sum(state[1]) > self.capacity:
                    continue

                state[1][n_] += 1

                inced = True

                state[0] = self.capacity - np.sum(state[1])

                if state[0] >= 0:
                    self.states[cnt] = copy.deepcopy(state)
                    cnt += 1

                break

            if not inced:
                break

        self.check_states()

        return self.states
    # -------------------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------------------
    def check_states(self):
        try:
            Assert(len(self.states) > 0, "len(states) <= 0", cf())

            for state in self.states.values():
                ph = state[0]
                at = state[1]

                Assert(0 <= ph <= self.capacity,
                       "incorrect state " + str(state), cf())
                Assert(ph + np.sum(at) == self.capacity,
                       "incorrect state " + str(state), cf())
                for n_ in range(len(at)):
                    Assert(0 <= at[n_] <= 1,
                           "incorrect state " + str(state), cf())
        except:
            print_error("incorrect states generation", cf())
            exit(1)

        return
    # -------------------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------------------
    def print_states(self):
        print("Hamiltonian states", color="green")

        try:
            for v in self.states.values():
                print("[%2d, " % (v[0]), v[1], "]", sep="")

            print()
        except:
            print_error("states not set", cf())
            exit(1)

        return
    # -------------------------------------------------------------------------------------------------

    def print_bin_states(self):
        for k, v in self.states_bin.items():
            print(k, v)

    def get_states_bin(self):
        states_bin = {}

        for k, v in self.states.items():
            at_state = v[1]

            en1 = at_state[: int(self.n / 2)]
            en2 = at_state[int(self.n / 2):]

            st = "[" + str(np.sum(en1)) + "," + str(np.sum(en2)) + "]"

            if not st in states_bin.keys():
                states_bin[st] = []

            states_bin[st].append(k)

        self.states_bin = {}
        self.states_bin_keys = []

        for k1 in range(int(self.n / 2) + 1):
            for k2 in range(int(self.n / 2) + 1):
                if k1 + k2 > self.capacity:
                    break

                k = "[" + str(k1) + "," + str(k2) + "]"

                self.states_bin_keys.append(k)

                if k in states_bin.keys():
                    self.states_bin[k] = states_bin[k]

        self.states_bin_keys = sorted(self.states_bin_keys)
        return self.states_bin
