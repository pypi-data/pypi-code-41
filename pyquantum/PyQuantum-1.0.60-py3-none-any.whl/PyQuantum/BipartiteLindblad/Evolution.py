# -------------------------------------------------------------------------------------------------
# system
import csv
from math import sqrt
# -------------------------------------------------------------------------------------------------
# BipartiteLindblad
from PyQuantum.BipartiteLindblad.Unitary import *
# -------------------------------------------------------------------------------------------------
# Common
from PyQuantum.Common.Tools import *
from PyQuantum.Common.STR import *
from PyQuantum.Common.Print import *
from PyQuantum.Common.Fidelity import *
# -------------------------------------------------------------------------------------------------
# scientific
import numpy as np
import scipy.linalg as lg
# -------------------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------------------
def get_a(H, m, n):
    H_size = H.size
    size = H_size

    a = np.array([np.zeros(size) for i in range(0, size)])

    for k_from, v_from in H.states.items():
        ph = v_from[0]

        if ph > 0:
            to_state = [ph - 1] + v_from[1:]

            for k_to, v_to in H.states.items():
                if to_state == v_to:
                    a[k_to][k_from] = sqrt(ph)

    return np.matrix(a)
# -------------------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------------------
def get_L_eng(ro, a, a_cross, across_a, H_states):
    L1 = np.matmul(a, ro)
    L1 = np.matmul(L1, a_cross)

    L2_1 = np.matmul(across_a, ro)
    L2_2 = np.matmul(ro, a_cross)
    L2_2 = np.matmul(L2_2, a)

    return np.matrix(L1 - 0.5 * (L2_1 + L2_2))


# -------------------------------------------------------------------------------------------------
def get_L(ro, a, a_cross, across_a):
    L1 = np.dot(a, ro)
    L1 = np.dot(L1, a_cross)

    L2 = np.dot(across_a, ro) + np.dot(ro, across_a)

    return np.matrix(L1 - 0.5 * L2)
# -------------------------------------------------------------------------------------------------
# def get_L(ro, a, a_cross, across_a, H_states):
#     # a = list(a)
#     # across_a = list(across_a)
#     # ro = np.array(ro)

#     L1 = np.matmul(a, ro)
#     L1 = np.matmul(L1, a_cross)
#     # L1 = np.dot(a, ro).dot(a_cross)
#     # _L1 = Matrix(len(H_states), len(H_states), dtype=np.complex128)
#     # _L1.set_header(H_states)
#     # _L1.data = L1

#     # print("-" * 100)
#     # ------------------------------------------------------------------
#     # _a = Matrix(len(H_states), len(H_states), dtype=np.complex128)
#     # _a.data = a
#     # _a.set_header(H_states)
#     # print("a:\n", color="yellow")
#     # _a.print_pd()
#     # # ------------------------------------------------------------------
#     # _across = Matrix(len(H_states), len(H_states), dtype=np.complex128)
#     # _across.data = a_cross
#     # _across.set_header(H_states)
#     # print("a_cross:\n", color="yellow")
#     # _across.print_pd()
#     # # ------------------------------------------------------------------
#     # _ro = Matrix(len(H_states), len(H_states), dtype=np.complex128)
#     # _ro.data = ro
#     # _ro.set_header(H_states)
#     # print("ro:\n", color="yellow")
#     # _ro.print_pd()
#     # # ------------------------------------------------------------------
#     # print("L1:\n", color="yellow")
#     # print(L1)

#     # exit(1)
#     # print("L1:\n", color="yellow")
#     # _L1.print_pd()
# # -------
# #    L2_1 = np.matmul(across_a, ro)
# #    L2_2 = np.matmul(ro, across_a)
#     # L2 = np.dot(across_a, ro) + np.dot(ro, across_a)
#     # _L2 = Matrix(len(H_states), len(H_states), dtype=np.complex128)
#     # _L2.set_header(H_states)
#     # _L2.data = L2
#     # print("L2:\n", color="yellow")
#     # _L2.print_pd()

# #    L = L1 - 0.5 * (L2_1 + L2_2)

#     # print(L)
#     # print("not null:")
#     # for i in range(L.shape[0]):
#     #     for j in range(L.shape[1]):
#     #         if L[i, j] != 0:
#     #             print(i, j)
#     # exit(0)
# #    return np.matrix(L)
# # ---
#     L1_tmp = np.matmul(a, ro)

#     L1 = np.matmul(L1_tmp, a_cross) - np.matmul(a_cross, L1_tmp)

#     L2_tmp = np.matmul(ro, a_cross)
#     L2 = np.matmul(a, L2_tmp) - np.matmul(L2_tmp, a)
#     # L1_2 = np.matmul(a, ro)
#     # L1_2 = np.matmul(L1_1, a_cross)

#     # L2_2 = np.matmul(ro, a_cross)
#     # L2_2 = np.matmul(a, L2_2)

#     return np.matrix((L2 + L2) / 2)
# # -------------------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------------------
def run(ro_0, H, dt, nt, l, config, fidelity_mode=False):
    # --------------------------------------------------------
    a = get_a(H, H.capacity, H.n)
    _a = Matrix(H.size, H.size, dtype=np.complex128)
    _a.data = a.data
    # _a.to_csv('a')
    # print(a)
    # if __debug__:
    # _a.to_csv(a_csv)

    a_cross = a.getH()
    across_a = np.dot(a_cross, a)
    _a_cross_a = Matrix(H.size, H.size, dtype=np.complex128)
    _a_cross_a.data = across_a.data

    # print(a)
    # exit(1)
    # print("H:\n", color="yellow")
    # H.matrix.set_header(H.states)
    # H.matrix.print_pd()

    # _a.set_header(H.states)
    # print("a:\n", color="yellow")
    # _a.print_pd()

    # _a_cross_a.set_header(H.states)
    # print("acrossa:\n", color="yellow")
    # _a_cross_a.print_pd()

    # for i in range(a.shape[0]):
    #     for j in range(a.shape[1]):
    #         if a[i, j]:
    #             print(H.states[i], H.states[j], a[i, j])

    # exit(1)
    # print(np.matrix(a))
    # if __debug__:
    # _a_cross_a.to_csv(a_cross_a_csv)
    # --------------------------------------------------------
    U = Unitary(H, dt)

    # if __debug__:
    # U.to_csv(config.U_csv)

    U_conj = U.conj()
    # --------------------------------------------------------

    ro_t = ro_0.data

    for k, v in H.states.items():
        if v == [H.capacity, 0, 0]:
            index1 = k
        if v == [0, H.n, 0]:
            index2 = k

    if fidelity_mode:
        ro_0_sqrt = lg.fractional_matrix_power(
            ro_0.data[index1:index2 + 1, index1:index2 + 1], 0.5)

        fidelity = []

    # print(np.round(np.diag(ro_t), 3))
    # print()

    # print("ρ(0):\n", color="yellow")
    # ro_0.set_header(H.states)
    # ro_0.print_pd()
    H.print_states()

    # ----------------------------------------------------------------------------
    with open(config.z_csv, "w") as csv_file:
        writer = csv.writer(
            csv_file, quoting=csv.QUOTE_NONE, lineterminator="\n")

        for t in range(0, nt+1):
            # print(t, nt)
            # diag_abs = np.abs(np.diag(ro_t)[index1:index2 + 1])

            # trace_abs = np.sum(diag_abs)
            diag = np.diag(ro_t)

            p = np.abs(diag[index1:index2 + 1])
            # p = np.asarray(p).reshape(-1)
            # p = np.around(p, precision)

            norm = np.sum(np.abs(diag))
            # print(t, "norm:", norm)
            Assert(abs(1 - norm) <= 0.1, str(t) + " " +
                   str(norm) + ": ro is not normed", cf())
            # Assert(abs(1 - trace_abs) <= 0.1, "ro is not normed", cf())

            writer.writerow(["{:.3f}".format(x) for x in p])
            # writer.writerow(["{:.5f}".format(x) for x in diag_abs])
            # --------------------------------------------------------------------
            if fidelity_mode:
                fidelity_t = Fidelity(
                    ro_0_sqrt, ro_t[index1:index2 + 1, index1:index2 + 1])
                # print(fidelity_t)
                fidelity.append(fidelity_t)
            # --------------------------------------------------------------------
            # for i in np.diag(ro_t):
            #     v = str(np.round(i, 3))
            #     # v = str(np.round(i, 3))
            #     print(v.rjust(5, ' '), end=' ')

            # v = str(np.round(np.sum(np.abs(diag[:-1])), 3))

            # print(v)

            L = get_L(ro_t, a, a_cross, across_a)
            ro_t = U.data.dot(ro_t).dot(U_conj) + dt * (config.l * L)

    # ----------------------------------------------------------------------------
    states = {}
    # print(np.round(np.diag(ro_t), 3))
    # ro_0.data = ro_t
    # ro_0.set_header(H.states)
    # print("ρ(t):\n", color="yellow")
    # ro_0.print_pd()

    # ro_0.data = L
    # print("L(t):\n", color="yellow")
    # ro_0.to_csv("L")
    # ro_0.print_pd()

    # exit(1)
    cnt = 0

    for k in range(index1, index2 + 1):
        states[cnt] = (H.states[k])[1:]
        cnt += 1
    print(states)
    write_xbp(states, config.x_csv, ind=[[0, H.n], [H.n, 0]])
    write_t(T_str_v(config.T), config.nt, config.y_csv)
    # write_t(config.T / config.mks / 1e-2, config.nt, config.y_csv)
    # ----------------------------------------------------------
    if fidelity_mode:
        list_to_csv(config.fid_csv, fidelity, header=["fidelity"])
    # ----------------------------------------------------------

# -------------------------------------------------------------------------------------------------
