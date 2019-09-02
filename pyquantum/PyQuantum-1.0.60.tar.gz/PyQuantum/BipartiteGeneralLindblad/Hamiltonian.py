# -------------------------------------------------------------------------------------------------
# scientific
import numpy as np
# -------------------------------------------------------------------------------------------------
# system
from math import sqrt
from PyQuantum.Common.html import *
import webbrowser
import copy
# -------------------------------------------------------------------------------------------------
# Common
from PyQuantum.Common.Matrix import *
from PyQuantum.Common.Assert import *
# -------------------------------------------------------------------------------------------------

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
        self.size = len(self.states)
        # print(len(self.states))
        # exit(1)

        self.get_states_bin()
        # self.print_bin_states()

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

                if i_state == j_state:
                    self.matrix.data[i, j] = self.wc * i_ph
                    # self.matrix_html[i][j] += "wc" + DOT() + str(i_ph) + " "

                    for n_ in range(len(i_at)):
                        self.matrix.data[i, j] += self.wa[n_] * i_at[n_]
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
                            else:
                                k = a_cross(j_ph) * j_at[diff_at_num]

                                self.matrix.data[i,
                                                 j] = self.g[diff_at_num] * k

                            # k = a_cross(i_ph) * i_at[diff_at_num]

                            # self.matrix.data[i, j] = self.g[diff_at_num]

        self.matrix.check_hermiticity()

        return
    # -------------------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------------------
    def print_html(self, filename):
                    # states = self.states""
                    # st = list(states.values())""
                    # for i in range(0, len(st)):"
                    #     st[i] = str(st[i])""
                    # df = pd.DataFrame(self.matrix.data, columns=st,"
                    #                   index=st, dtype=str)""
                    # f = open("Hamiltonian.html", "w")"
                    # style = """"
                    # <style>"
                    #     .dataframe th, td {"
                    #         text-align:center;"
                    #         # min-width:200px;"
                    #         white-space: nowrap;"
                    #         word-break:keep-all;"
                    #     }"        # </style>"""""
                    # f.write(style + df.to_html())"
                    # webbrowser.open("Hamiltonian.html")""
                    # f.close()""
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

        cnt = 0

        f = open("bin", "w")

        for capacity in range(self.capacity, -1, -1):
            state = [capacity, [0] * self.n]
            self.states[cnt] = copy.deepcopy(state)
            cnt += 1

            state[0] -= 1

            while(1):
                inced = False

                for n_ in range(self.n - 1, -1, -1):
                    if state[1][n_] == 1:
                        state[1][n_] = 0

                        continue

                    if state[0] + np.sum(state[1]) > capacity:
                        continue

                    state[1][n_] += 1

                    inced = True

                    state[0] = capacity - np.sum(state[1])

                    if state[0] >= 0:
                        self.states[cnt] = copy.deepcopy(state)
                        # print(self.states[cnt])
                        f.write(''.join(str(i)
                                        for i in self.states[cnt][1]) + "\n")
                        # print(self.states[cnt], str.join(
                        #    "", self.states[cnt][1]))
                        cnt += 1

                    # print("[%2d, " % (v[0]), v[1], "]", sep="")
                    break

                if not inced:
                    break
        f.close()
        # self.states = {}

        # state = [self.capacity, [0] * self.n]

        # cnt = 0

        # # self.states[cnt] = copy.deepcopy(state)

        # self.index1 = cnt

        # cnt += 1

        # state[0] -= 1

        # capacity = self.capacity

        # while(1):
        #     inced = False

        #     for n_ in range(self.n - 1, -1, -1):
        #         if state[1][n_] == 1:
        #             state[1][n_] = 0

        #             continue

        #         if state[0] + np.sum(state[1]) > capacity:
        #             continue

        #         state[1][n_] += 1

        #         inced = True

        #         print("cap ", state, capacity)
        #         state[0] = capacity - np.sum(state[1])

        #         if state[0] >= 0:
        #             self.states[cnt] = copy.deepcopy(state)
        #             print(cnt, self.states[cnt])
        #             cnt += 1

        #         break

        #     if not inced:
        #         if capacity == 0:
        #             self.states[cnt] = [0, [0] * self.n]
        #             cnt += 1

        #             break

        #         if capacity == self.capacity:
        #             self.index2 = cnt - 1

        #         capacity -= 1

        self.check_states()

        return self.states
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

            if v[0] + np.sum(en1) + np.sum(en2) != self.capacity:
                continue
            st = "[" + str(np.sum(en1)) + "," + str(np.sum(en2)) + "]"

            if not st in states_bin.keys():
                states_bin[st] = []

            states_bin[st].append(k)

        self.states_bin = {}
        self.states_bin_keys = []

        for ph in range(self.capacity, -1, -1):
            for k1 in range(int(self.n / 2) + 1):
                for k2 in range(int(self.n / 2) + 1):
                    if ph + k1 + k2 == self.capacity:
                        k = "[" + str(k1) + "," + str(k2) + "]"

                        self.states_bin_keys.append(k)

                        if k in states_bin.keys():
                            self.states_bin[k] = states_bin[k]

        self.states_bin_keys = sorted(self.states_bin_keys)

        return self.states_bin

    # -------------------------------------------------------------------------------------------------
    def check_states(self):
        try:
            Assert(len(self.states) > 0, "len(states) <= 0", cf())

            for state in self.states.values():
                ph = state[0]
                at = state[1]

                Assert(0 <= ph <= self.capacity,
                       "incorrect state " + str(state), cf())
                Assert(ph + np.sum(at) <= self.capacity,
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
        # print("Hamiltonian states:", color="green")

        try:
            for v in self.states.values():
                print("[%2d, " % (v[0]), v[1], "]", sep="")
                # print()
        except:
            print_error("states not set", cf())
            exit(1)

        return
    # -------------------------------------------------------------------------------------------------
