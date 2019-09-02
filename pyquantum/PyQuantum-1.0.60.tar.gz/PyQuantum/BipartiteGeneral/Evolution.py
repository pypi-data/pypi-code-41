# -------------------------------------------------------------------------------------------------
# system
import csv
# -------------------------------------------------------------------------------------------------
# BipartiteGeneral
from PyQuantum.BipartiteGeneral.Unitary import *
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
def run(ro_0, H, dt, nt, config, fidelity_mode=False):
    # --------------------------------------------------------
    U = Unitary(H, dt)

    if __debug__:
        U.to_csv(config.U_csv)

    U_conj = U.conj()

    # ro_t = sp.csc_matrix(ro_0.data)
    # U_data = sp.csc_matrix(U.data)
    # U_conj_data = sp.csc_matrix(U_conj.data)
    # --------------------------------------------------------
    if fidelity_mode:
        ro_0_sqrt = lg.fractional_matrix_power(ro_0.data, 0.5)

        fidelity = []

    ro_t = ro_0.data
    # ----------------------------------------------------------------------------
    p_bin = dict.fromkeys(H.states_bin_keys)
    # --------------------------------------------------------
    with open(config.z_csv, "w") as csv_file:
        writer = csv.writer(
            csv_file, quoting=csv.QUOTE_NONE, lineterminator="\n")

        with open(config.z_all_csv, "w") as csv_all_file:
            writer_all = csv.writer(
                csv_all_file, quoting=csv.QUOTE_NONE, lineterminator="\n")

            for t in range(0, nt):
                diag_abs = np.abs(np.diag(ro_t))

                trace_abs = np.sum(diag_abs)

                Assert(abs(1 - trace_abs) <= 0.1, "ro is not normed", cf())

                for k, v in p_bin.items():
                    p_bin[k] = 0

                for k, v in H.states_bin.items():
                    for ind in v:
                        p_bin[k] += diag_abs[ind]

                v_bin = [p_bin[k] for k in H.states_bin_keys]
                # --------------------------------------------------
                writer.writerow(["{:.5f}".format(x) for x in v_bin])

                # if __debug__:
                # writer_all.writerow(["{:.5f}".format(x) for x in diag_abs])
                # --------------------------------------------------
                if fidelity_mode:
                    fidelity_t = Fidelity(ro_0_sqrt, ro_t)
                    fidelity.append(fidelity_t)
                # --------------------------------------------------
                ro_t = U.data.dot(ro_t).dot(U_conj)
                # ro_t =ro_t = sp.csc_matrix(ro_0.data)
    U_data = sp.csc_matrix(U.data)
    U_conj_data = sp.csc_matrix(U_conj.data)
    U_data.dot(ro_t).dot(U_conj_data)
    # --------------------------------------------------------------
    states_bin = {}

    cnt = 0

    for k in H.states_bin_keys:
        if k == "[" + str(0) + "," + str(int(config.n / 2)) + "]" or k == "[" + str(int(config.n / 2)) + "," + str(0) + "]":

            states_bin[cnt] = str(k)
        else:
            states_bin[cnt] = ""
        cnt += 1
    # ----------------------------------------------------------
    states = {}

    cnt = 0

    for v in H.states_bin_keys:
        states[cnt] = v

        cnt += 1
    # ----------------------------------------------------------
    write_x(states, config.x_csv)
    write_t(config.T / config.mks, config.nt, config.y_csv)
    # ----------------------------------------------------------
    if fidelity_mode:
        list_to_csv(fid_csv, fidelity, header=["fidelity"])
    # ----------------------------------------------------------

# -------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------


def run_wf(w_0, H, dt, nt, config, fidelity_mode=False):
    # --------------------------------------------------------
    U = Unitary(H, dt)

    if __debug__:
        U.to_csv(config.U_csv)

    U_conj = U.conj()
    # --------------------------------------------------------
    if fidelity_mode:
        fidelity = []

    w_0 = np.matrix(w_0.data)
    w_t = np.array(w_0.data)
    # ----------------------------------------------------------------------------
    p_bin = dict.fromkeys(H.states_bin_keys)
    # --------------------------------------------------------
    z_0 = []
    z_1 = []

    ind_0 = None
    ind_1 = None

    i = 0
    for v in H.states_bin_keys:
        print(v)
        if v == '[0,'+str(int(H.n/2))+']':
            ind_0 = i
        elif v == '['+str(int(H.n/2))+',0]':
            ind_1 = i

        i += 1

    # print(ind_0)
    # print(ind_1)

    with open(config.z_csv, "w") as csv_file:
        writer = csv.writer(
            csv_file, quoting=csv.QUOTE_NONE, lineterminator="\n")

        with open(config.z_all_csv, "w") as csv_all_file:
            writer_all = csv.writer(
                csv_all_file, quoting=csv.QUOTE_NONE, lineterminator="\n")

            dt_ = nt / (config.T/config.mks) / 20000 * 1000
            nt_ = int(nt/dt_)

            for t in range(0, nt):
                w_t_arr = w_t.reshape(1, -1)[0]

                diag_abs = np.abs(w_t_arr)**2
                trace_abs = np.sum(diag_abs)

                Assert(abs(1 - trace_abs) <= 0.1, "ro is not normed", cf())

                for k, v in p_bin.items():
                    p_bin[k] = 0

                for k, v in H.states_bin.items():
                    for ind in v:
                        p_bin[k] += diag_abs[ind]

                v_bin = [p_bin[k] for k in H.states_bin_keys]
                # --------------------------------------------------
                # if t % nt_ == 0:
                writer.writerow(["{:.5f}".format(x) for x in v_bin])

                z_0.append(round(v_bin[ind_0], 5))
                z_1.append(round(v_bin[ind_1], 5))
                # print(z_0)
                # print(z_1)
                # exit(1)
                # if __debug__:
                # writer_all.writerow(["{:.5f}".format(x) for x in diag_abs])
                # --------------------------------------------------
                if fidelity_mode:
                    w_t = np.matrix(w_t)

                    D = w_0.getH().dot(w_t).reshape(-1)[0, 0]

                    fidelity_t = round(abs(D), 3)

                    fidelity_t = "{:.5f}".format(fidelity_t)

                    fidelity.append(float(fidelity_t))
                # --------------------------------------------------
                w_t = np.array(U.data.dot(w_t))
    # --------------------------------------------------------------
    states_bin = {}

    cnt = 0

    for k in H.states_bin_keys:
        if k == "[" + str(0) + "," + str(int(config.n / 2)) + "]" or k == "[" + str(int(config.n / 2)) + "," + str(0) + "]":

            states_bin[cnt] = str(k)
        else:
            states_bin[cnt] = ""
        cnt += 1
    # ----------------------------------------------------------
    states = {}

    cnt = 0

    for v in H.states_bin_keys:
        states[cnt] = v

        cnt += 1
    # ----------------------------------------------------------
    write_xbpg(states, config.x_csv, ind=[[0, int(H.n/2)], [int(H.n/2), 0]])
    write_t(T_str_v(config.T), config.nt, config.y_csv)
    # ----------------------------------------------------------
    if fidelity_mode:
        list_to_csv(config.fid_csv, fidelity, header=["fidelity"])

        fidelity = fidelity[::nt_]
        list_to_csv(config.fid_small_csv, fidelity, header=["fidelity"])

        list_to_csv(config.path + 'z_0.csv', z_0, header=["fidelity"])
        list_to_csv(config.path + 'z_1.csv', z_1, header=["fidelity"])
    # ----------------------------------------------------------

# -------------------------------------------------------------------------------------------------
