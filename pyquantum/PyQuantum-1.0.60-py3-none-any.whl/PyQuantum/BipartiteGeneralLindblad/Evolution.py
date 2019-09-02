# -------------------------------------------------------------------------------------------------
# system
import csv
from math import sqrt
# -------------------------------------------------------------------------------------------------
# BipartiteGeneralLindblad
from PyQuantum.BipartiteGeneralLindblad.Unitary import *
# -------------------------------------------------------------------------------------------------
# Common
from PyQuantum.Common.Tools import *
from PyQuantum.Common.Fidelity import *
# -------------------------------------------------------------------------------------------------
# scientific
import numpy as np
import scipy.linalg as lg
import scipy.sparse as sp
# -------------------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------------------
def get_a(H, m, n):
    H_size = H.size
    size = H_size

    a = np.array([np.zeros(size) for i in range(size)])

    for k_from, v_from in H.states.items():
        ph = v_from[0]

        if ph > 0:
            # print("ph = ", ph)
            # print("from_state = ", v_from)

            to_state = [ph - 1] + v_from[1:]
            # print("to_state0 = ", to_state)

            for k_to, v_to in H.states.items():
                if to_state == v_to:
                    # print("to_state = ", to_state)
                    a[k_to][k_from] = sqrt(ph)

    return np.matrix(a)
    # return sp.csc_matrix(np.matrix(a))
# -------------------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------------------
def get_L(ro, a, a_cross, across_a):
    L1 = np.dot(a, ro)
    L1 = np.dot(L1, a_cross)

    L2 = np.dot(across_a, ro) + np.dot(ro, across_a)

    ret = np.matrix(L1 - 0.5 * L2)

    return sp.csc_matrix(ret)
# -------------------------------------------------------------------------------------------------


def run(ro_0, H, dt, nt, l, config):
    # ---------------------------------------------------------------------------------------------
    a = get_a(H, config.capacity, config.n)
    _a = Matrix(H.size, H.size, dtype=np.complex128)
    _a.data = a.data
    # print(a)
    # for i in range(a.shape[0]):
    #     for j in range(a.shape[1]):
    #         if a[i, j]:
    #             print(H.states[j], H.states[i], a[i, j])
    # if __debug__:
    # _a.to_csv(config.a_csv)
    # ---------------------------------------------------------------------------------------------
    a_cross = a.getH()
    across_a = np.dot(a_cross, a)
    _a_cross_a = Matrix(H.size, H.size, dtype=np.complex128)
    _a_cross_a.data = across_a.data

    # if __debug__:
    # _a_cross_a.to_csv(a_cross_a_csv)
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    U = Unitary(H, dt)

    # if __debug__:
    # U.to_csv(config.U_csv)

    U_conj = U.conj()

    U_data = sp.csc_matrix(U.data)
    U_conj_data = sp.csc_matrix(U_conj.data)
    # ---------------------------------------------------------------------------------------------
    # ro_t = ro_0.data
    ro_t = sp.csc_matrix(np.array(ro_0.data))
    p_bin = dict.fromkeys(H.states_bin_keys)

    # print(ro_t)
    # exit(0)
    # ro_t = sp.csc_matrix(ro_t)
    # U_data = sp.csc_matrix(U.data)
    # U_conj_data = sp.csc_matrix(U_conj.data)
    # H.print_states()
    # exit(0)

    # print("bin:")

    # H.print_bin_states()
    # print(p_bin)
    # ---------------------------------------------------------------------------------------------
    st = {}

    for k, v in H.states.items():
        if v == [2, [0, 0, 0, 0]]:
            # if v == [3, [0, 0, 0, 0, 0, 0]]:
            # if v == [int(H.n / 2), [0 * int(H.n / 2)] + [0 * int(H.n / 2)]]:
            k1 = k
        if v == [0, [1, 1, 0, 0]]:

            # if v == [0, [0 * int(H.n / 2)], 0]:
            k2 = k

    # for k, v in H.states.items():
    #     if v[0] + np.sum(v[1]) == H.capacity:
    #         st[k] = v

    #         st_keys = list(st.keys())

    #         k1 = st_keys[0]
    #         k2 = st_keys[-1]
    # ---------------------------------------------------------------------------------------------
    with open(config.z_csv, "w") as csv_file:
        writer = csv.writer(
            csv_file, quoting=csv.QUOTE_NONE, lineterminator="\n")

        for t in range(0, nt):
            # print(t, nt)
            # print(t, nt)
            # diag_abs = np.abs(np.diag(ro_t))
            # diag = np.diag(ro_t)
            # diag = np.diag(ro_t.todense())
            diag = ro_t.diagonal()
            diag_abs = np.abs(diag)
            trace_abs = np.sum(diag_abs)

            Assert(abs(1 - trace_abs) <= 0.1, "ro is not normed", cf())

            # writer.writerow(["{:.5f}".format(x) for x in p[k1:k2 + 1]])
            for k, v in p_bin.items():
                p_bin[k] = 0

            # print(["{:.10f}".format(np.abs(x)) for x in np.diag(ro_t)])
            # print(H.states.items())
            # exit(0)
            # print(H.states[], diag_abs[k])
            # d = []

            # if t > nt * 0.8:
            #     print("{:.5f}".format(np.imag(diag[3])), "\t", "{:.5f}".format(np.imag(diag[5])), "\t", "{:.5f}".format(np.imag(diag[6])), "\t",
            #           "{:.5f}".format(np.imag(diag[8])), "\t", "{:.5f}".format(
            #               np.imag(diag[9])), "\t",
            #           "{:.5f}".format(np.imag(diag[10])), "\t")
                # H.states[10], ":", "{:.5f}".format(np.imag(diag[10])))
                # print(H.states[3], ":", "{:.5f}".format(np.imag(diag[3])), "\t",
                # H.states[10], ":", "{:.5f}".format(np.imag(diag[10])))

                # print(H.states[5], ":", "{:.5f}".format(np.imag(diag[5])), "\t",
                # H.states[6], ":", "{:.5f}".format(np.imag(diag[6])))

                # print(H.states[], ":", "{:.5f}".format(np.imag(diag[5])), "\t",
                # H.states[6], ":", "{:.5f}".format(np.imag(diag[6])))
                # print(H.states[3], ":", "{:.5f}".format(np.imag(diag[3])), "\t",
                # H.states[10], ":", "{:.5f}".format(np.imag(diag[10])))

            # for k, v in H.states.items():
            # print(v)
            # if v == [0, [0, 0, 1, 1]] or v == [0, [1, 1, 0, 0]]:
            # print(v, diag_abs[k])

            for k, v in H.states_bin.items():
                for ind in v:
                    p_bin[k] += diag_abs[ind]

            v_bin = [p_bin[k] for k in H.states_bin_keys]
            # print(v_bin)
            # exit(1)
            # --------------------------------------------------
            writer.writerow(["{:.10f}".format(x) for x in v_bin])

            # if __debug__:
            # writer_all.writerow(["{:.5f}".format(x) for x in diag_abs])
            # --------------------------------------------------

            # L = get_L(ro_t, a, a_cross, across_a)
            ro_t = U_data.dot(ro_t).dot(U_conj_data)
            print(ro_t.count_nonzero(), np.shape(H.matrix.data)
                  [0] * np.shape(H.matrix.data)[1])
            # ro_t = U.data.dot(ro_t).dot(U_conj)
            # ro_t = sp.csc_matrix(np.array(ro_t))
            # ro_t = U.data.dot(ro_t).dot(U_conj) + dt * (config.l * L)
    # ro_t = U_data.dot(ro_t).dot(U_conj_data) + dt * (config.l * L)
    # ---------------------------------------------------------------------------------------------
    states = {}
    n2 = int(H.n / 2)
    cnt = 0
    # ---------------------------------------------------------------------------------------------
    states = {}
    cnt = 0

    # for k in range(k1, k2 + 1):
    #     states[cnt] = "[" + str(np.sum(H.states[k][1][:2])) + \
    #         ", " + str(np.sum(H.states[k][1][2:])) + "]"
    #     cnt += 1
    # print(H.states_bin)
    # print(st)

    for k, v in st.items():
        if k >= k1 and k <= k2:
            if v == [H.capacity - n2, [0] * n2 + [1] * n2] or \
                    v == [H.capacity - n2, [1] * n2 + [0] * n2]:
                states[cnt] = "[" + str(np.sum(v[1][:n2])) + \
                    ", " + str(np.sum(v[1][n2:])) + "]"
            else:
                states[cnt] = ""
                cnt += 1
    # ---------------------------------------------------------------------------------------------
    # print("states:", states)
    # write_x(states, config.x_csv)
    # write_xx(states, config.x_csv)
    # print(states.items())
    # write_x(states, config.x_csv, ind_1='[0, 2]', ind_2='[2, 0]')
    write_t(T_str_v(config.T), config.nt, config.y_csv)

    # ---------------------------------------------------------------------------------------------
