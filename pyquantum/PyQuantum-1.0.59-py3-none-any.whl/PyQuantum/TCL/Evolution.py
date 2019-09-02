# -------------------------------------------------------------------------------------------------
# system
import csv
from math import sqrt
# -------------------------------------------------------------------------------------------------
# BipartiteGeneralLindblad
from PyQuantum.TCL.Unitary import *
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
import peakutils


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
                    # a[k_from][k_to] = sqrt(ph)
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


def run(ro_0, H, dt, nt, l, config, states=set(), thres=0.1):
    dt = 0.1 / l

    nt = int(config.T / dt)
    # print(nt)
    # ---------------------------------------------------------------------------------------------
    a = get_a(H, config.capacity, config.n_atoms)
    _a = Matrix(H.size, H.size, dtype=np.complex128)
    _a.data = a.data

    _a.states = H.states

    # if __debug__:
    # _a.to_html("a.html")
    _a.to_html("a.html")
    # exit(0)
    # print(a)
    # for i in range(a.shape[0]):
    #     for j in range(a.shape[1]):
    #         if a[i, j]:
    #             print(H.states[j], H.states[i], a[i, j])
    # if __debug__:
    # _a.to_csv(config.a_csv)
    # ---------------------------------------------------------------------------------------------
    a_cross = a.getH()
    _across = Matrix(H.size, H.size, dtype=np.complex128)
    _across.data = a_cross.data
    _across.states = H.states
    _across.to_html("across.html")

    across_a = np.dot(a_cross, a)
    _a_cross_a = Matrix(H.size, H.size, dtype=np.complex128)
    _a_cross_a.data = across_a.data
    _a_cross_a.states = H.states
    _a_cross_a.to_html("acrossa.html")

    # if __debug__:
    # _a_cross_a.to_csv(a_cross_a_csv)
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    U = Unitary(H, dt)

    if __debug__:
        U.to_csv(config.U_csv)

    U_data = U.data

    U_conj = U.conj()
    U_conj_data = U_conj.data
    # U = Unitary(H, dt)

    # if __debug__:
    # U.to_csv(config.U_csv)

    # U_conj = U.conj()

    # U_data = sp.csc_matrix(U.data)
    # U_conj_data = sp.csc_matrix(U_conj.data)
    # ---------------------------------------------------------------------------------------------
    H.states_bin = {}
    for k, v in H.states.items():
        at_state = str(v[1])

        if at_state not in H.states_bin:
            H.states_bin[at_state] = []

        H.states_bin[at_state].append(k)
    # ---------------------------------------------------------------------------------------------
        ro_t = ro_0.data
    # ro_t = sp.csc_matrix(np.array(ro_0.data))
    H.states_bin_keys = H.states_bin.keys()
    p_bin = dict.fromkeys(H.states_bin_keys)

    # print(p_bin)
    # exit(0)
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

    # ---------------------------------------------------------------------------------------------
    # print(H.states_bin)
    # exit(0)
    # ro_0_sqrt = lg.fractional_matrix_power(
    #     ro_0.data[0:5, 0:5], 0.5)

    # print(ro_0_sqrt)

    with open(config.z_csv, "w") as csv_file:
        writer = csv.writer(
            csv_file, quoting=csv.QUOTE_NONE, lineterminator="\n")

        for t in range(0, nt+1):
            print(t, "/", nt)
            # diag = ro_t.diagonal()
            # diag_abs = np.abs(diag)[0, 0]
            # ro_t /= np.linalg.norm(ro_t)
            diag_abs = np.abs(np.diag(ro_t))
            trace_abs = np.sum(diag_abs[0:4])
            # print(diag_abs, np.sum(diag_abs))
            # print(diag_abs, np.sum(diag_abs))
            Assert(abs(1 - np.sum(diag_abs))
                   <= 0.1, "ro is not normed", cf())
            # writer.writerow(["{:.5f}".format(x) for x in p[k1:k2 + 1]])
            for k, v in p_bin.items():
                p_bin[k] = 0

            # peaks = peakutils.indexes(diag_abs, thres=thres)

            # for i in peaks:
            #     # print(i)
            #     # exit(0)
            #     states.add(i)
            # print(diag_abs)
            for k, v in H.states_bin.items():
                for ind in v:
                    # print(k)
                    p_bin[k] += diag_abs[ind]

            v_bin = [p_bin[k] for k in H.states_bin_keys]

            for i, j in enumerate(v_bin):
                # print(i, j)
                if abs(j) > thres:
                    states.add(i)
            # print(p_bin)
            # print(H.states_bin_keys)
            # print(H.states)
            # print(v_bin)
            # exit(1)
            # --------------------------------------------------
            writer.writerow(["{:.5f}".format(x) for x in v_bin])

            # if __debug__:
            # writer_all.writerow(["{:.5f}".format(x) for x in diag_abs])
            # --------------------------------------------------

            L = get_L(ro_t, a, a_cross, across_a)
            # ro_t = U_data.dot(ro_t).dot(U_conj_data)
            # print(ro_t.count_nonzero(), np.shape(H.matrix.data)
            #       [0] * np.shape(H.matrix.data)[1])
            # ro_t = U.data.dot(ro_t).dot(U_conj)
            # ro_t = sp.csc_matrix(np.array(ro_t))
            # ro_t = ro_t + dt * (config.l * L)
            # ro_t = ro_t + dt * (config.l * L)
            # ro_t = ro_t + dt * (config.l * L)
            # /# print(ro_t.trace()[0, 0])

            ro_t = ro_t + dt * (config.l * L)
            # ro_t = ro_t + dt * -1j * (config.l * L)
            ro_t = U_data.dot(ro_t).dot(U_conj)

            ro_t = (ro_t+ro_t.getT())/2.0
            ro_t /= np.sum(np.abs(np.diag(ro_t)))

            # ro_t /= ro_t.trace()[0, 0]

            # fidelity_t = Fidelity(
            #     ro_0_sqrt, ro_t[0:5, 0:5])
            # print(fidelity_t)
            # print(ro_t)
            # exit(0)
            # ro_t /= np.linalg.norm(ro_t)

            print(t, '/', nt, ':', np.abs(np.diag(ro_t)),
                  np.sum(np.abs(np.diag(ro_t))))

            # print()
            # ro_t.normalize()
            # print("t =", t)
            # print("norm = ", np.linalg.norm(ro_t),
            # np.sum(np.abs(np.diag(ro_t))))
            # print(np.sum(np.abs(np.diag(ro_t))))
            # ro_t = ro_t - ro_t.mean()
            # ro_t = ro_t / ro_t.max()

            # ro_t /= np.norm(ro_t)
    # ro_t = U_data.dot(ro_t).dot(U_conj_data) + dt * (config.l * L)
    # ---------------------------------------------------------------------------------------------
    st = dict()
    print(diag_abs, np.sum(diag_abs))

    print(states)

    need_states = []

    for k in H.states.values():
        if k[0] + np.sum(k[1]) == config.capacity:
            need_states.append(k)

    for k in range(len(need_states)):
        if k in states:
            st[k] = str(need_states[k][1])
        else:
            st[k] = ""

    write_xbp(H.states, config.x_csv, ind=st)
    write_t(T_str_v(config.T), config.nt, config.y_csv)
    # ---------------------------------------------------------------------------------------------
