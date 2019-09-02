# -------------------------------------------------------------------------------------------------
# system
import csv
# -------------------------------------------------------------------------------------------------
# Bipartite
from PyQuantum.Bipartite.Unitary import *
# -------------------------------------------------------------------------------------------------
# Common
from PyQuantum.Common.Tools import *
from PyQuantum.Common.STR import *
from PyQuantum.Common.Fidelity import *
# -------------------------------------------------------------------------------------------------
# scientific
import numpy as np
import scipy.linalg as lg
# -------------------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------------------
def run(ro_0, H, dt, nt, config, fidelity_mode=False):
    # --------------------------------------------------------
    U = Unitary(H, dt)

    if __debug__:
        U.to_csv(config.U_csv)

    U_conj = U.conj()
    # --------------------------------------------------------
    if fidelity_mode:
        ro_0_sqrt = lg.fractional_matrix_power(ro_0.data, 0.5)

        fidelity = []
    import scipy.sparse as sp

    ro_t = sp.csc_matrix(ro_0.data)
    U_data = sp.csc_matrix(U.data)
    U_conj_data = sp.csc_matrix(U_conj.data)

    # ----------------------------------------------------------------------------
    with open(config.z_csv, "w") as csv_file:
        writer = csv.writer(
            csv_file, quoting=csv.QUOTE_NONE, lineterminator="\n")

        for t in range(0, nt):
            diag_abs = np.abs(np.diag(ro_t))

            trace_abs = np.sum(diag_abs)

            Assert(abs(1 - trace_abs) <= 0.1, "ro is not normed", cf())

            writer.writerow(["{:.5f}".format(x) for x in diag_abs])
            # --------------------------------------------------------------------
            if fidelity_mode:
                fidelity_t = round(Fidelity(ro_0_sqrt, ro_t), 5)
                fidelity_t = "{:.5f}".format(fidelity_t)

                fidelity.append(fidelity_t)
            # --------------------------------------------------------------------
            # ro_t = U.data.dot(ro_t).dot(U_conj)
            ro_t = U_data.dot(ro_t).dot(U_conj_data)
    # ----------------------------------------------------------------------------
    states = H.states

    write_x(states, config.x_csv, ind_1=[0, H.n], ind_2=[H.n, 0])
    write_t(T_str_v(config.T), config.nt, config.y_csv)
    # ----------------------------------------------------------
    if fidelity_mode:
        list_to_csv(config.fid_csv, fidelity, header=["fidelity"])
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
    dt_ = nt / (config.T/config.mks) / 20000 * 1000
    nt_ = int(nt/dt_)

    z_0 = []
    z_1 = []
    z_max = []

    ind_0 = None
    ind_1 = None

    for k, v in H.states.items():
        if v == [0, H.cavity.n]:
            ind_0 = k
        elif v == [H.cavity.n, 0]:
            ind_1 = k

    with open(config.z_csv, "w") as csv_file:
        writer = csv.writer(
            csv_file, quoting=csv.QUOTE_NONE, lineterminator="\n")

        for t in range(0, nt+1):
            w_t_arr = w_t.reshape(1, -1)[0]

            diag_abs = np.abs(w_t_arr)**2
            trace_abs = np.sum(diag_abs)

            Assert(abs(1 - trace_abs) <= 0.1, "ro is not normed", cf())
            # --------------------------------------------------------------------
            if fidelity_mode:
                w_t = np.matrix(w_t)

                D = w_0.getH().dot(w_t).reshape(-1)[0, 0]

                fidelity_t = round(abs(D), 3)

                fidelity_t = "{:>.5f}".format(fidelity_t)

                fidelity.append(fidelity_t)
                # print(fidelity)
            z_0.append("{:.5f}".format(diag_abs[ind_0]))
            z_1.append("{:.5f}".format(diag_abs[ind_1]))

            zmax = 0

            # print(diag_abs)
            for i_ in range(0, len(diag_abs)):
                if i_ != ind_0 and i_ != ind_1 and diag_abs[i_] > zmax:
                    # exit(1)
                    zmax = diag_abs[i_]

            z_max.append(zmax)

            # z_1.append(round(diag_abs[ind_1], config.precision))
            # z_1.append(float(diag_abs[ind_1]))

            # if t % nt_ == 0:
            writer.writerow(["{:.5f}".format(x)
                             for x in diag_abs])
            # --------------------------------------------------------------------
            w_t = np.array(U.data.dot(w_t))
    # ----------------------------------------------------------------------------
    states = H.states

    write_xbp(states, config.x_csv, ind=[[0, H.cavity.n], [H.cavity.n, 0]])
    write_t(T_str_v(config.T), config.nt, config.y_csv)
    # ----------------------------------------------------------
    if fidelity_mode:
        list_to_csv(config.fid_csv, fidelity, header=["fidelity"])

        # fidelity = fidelity[::nt_]
        # list_to_csv(config.fid_small_csv, fidelity, header=["fidelity"])

    list_to_csv(config.path + 'z_max.csv', z_max, header=["fidelity"])
    list_to_csv(config.path + 'z_0.csv', z_0, header=["fidelity"])
    list_to_csv(config.path + 'z_1.csv', z_1, header=["fidelity"])
    # ----------------------------------------------------------

# -------------------------------------------------------------------------------------------------
