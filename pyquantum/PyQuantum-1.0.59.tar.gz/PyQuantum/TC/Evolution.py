# -------------------------------------------------------------------------------------------------
# system
import csv
# -------------------------------------------------------------------------------------------------
# Bipartite
from PyQuantum.TC.Unitary import *
# -------------------------------------------------------------------------------------------------
# Common
from PyQuantum.Common.Tools import *
from PyQuantum.Common.STR import *
from PyQuantum.Common.Fidelity import *
# -------------------------------------------------------------------------------------------------
# scientific
import numpy as np
import scipy.sparse.linalg as lg

# import scipy.linalg as lg
# -------------------------------------------------------------------------------------------------


def run_wf(w_0, H, dt, nt, config, states=set(), fidelity_mode=False, thres=0.1):
    # --------------------------------------------------------
    U = Unitary(H, dt)

    if __debug__:
        U.to_csv(config.U_csv)

    U_data = U.data
    # --------------------------------------------------------
    if fidelity_mode:
        fidelity = []

    w_t = w_0.data
    # ----------------------------------------------------------------------------
    with open(config.z_csv, "w") as csv_file:
        writer = csv.writer(
            csv_file, quoting=csv.QUOTE_NONE, lineterminator="\n")

        for t in range(0, nt+1):
            diag_abs = np.abs(w_t.toarray()[:, 0])**2
            trace_abs = np.sum(diag_abs)

            # print(diag_abs)
            # print(trace_abs)

            for i, j in enumerate(diag_abs):
                if abs(j) > thres:
                    states.add(i)

            Assert(abs(1 - trace_abs) <= 0.1, "ro is not normed", FILE(), LINE())
            # --------------------------------------------------------------------
            # if fidelity_mode:
            #     w_t = np.matrix(w_t)

            #     D = w_0.getH().dot(w_t).reshape(-1)[0, 0]

            #     fidelity_t = round(abs(D), 3)

            #     fidelity_t = "{:>.5f}".format(fidelity_t)

            #     fidelity.append(fidelity_t)

            # print(fidelity)

            writer.writerow(["{:.5f}".format(x)
                             for x in diag_abs])
            # --------------------------------------------------------------------
            w_t = U_data.dot(w_t)
    # ----------------------------------------------------------------------------
    st = dict()

    print(states)
    print(H.states)

    for k in range(len(H.states)):
        if k in states:
            st[k] = str(H.states[k][1])
        else:
            st[k] = ""

    write_xbp(H.states, config.x_csv, ind=st)
    write_t(T_str_v(config.T), config.nt, config.y_csv)
    # ----------------------------------------------------------
    # if fidelity_mode:
    #     list_to_csv(config.fid_csv, fidelity, header=["fidelity"])

    # fidelity = fidelity[::nt_]
    # list_to_csv(config.fid_small_csv, fidelity, header=["fidelity"])

    # ----------------------------------------------------------

# -------------------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------------------
def run_ro(ro_0, H, dt, nt, config, states=set(), fidelity_mode=False, thres=0.1):
    # --------------------------------------------------------
    U = Unitary(H, dt)

    if __debug__:
        U.to_csv(config.U_csv)

    U_data = U.data

    U_conj = U.conj()
    U_conj_data = U_conj.data
    # --------------------------------------------------------
    if fidelity_mode:
        ro_0_sqrt = lg.fractional_matrix_power(ro_0.data, 0.5)

        fidelity = []

    ro_t = ro_0.data

    # ----------------------------------------------------------------------------
    with open(config.z_csv, "w") as csv_file:
        writer = csv.writer(
            csv_file, quoting=csv.QUOTE_NONE, lineterminator="\n")

        for t in range(0, nt+1):
            diag_abs = np.abs(np.diag(ro_t))
            trace_abs = np.sum(diag_abs)

            print(diag_abs)

            Assert(abs(1 - trace_abs) <= 0.1, "ro is not normed", FILE(), LINE())

            writer.writerow(["{:.5f}".format(x) for x in diag_abs])
            # --------------------------------------------------------------------

            if fidelity_mode:
                fidelity_t = round(Fidelity(ro_0_sqrt, ro_t), 5)
                fidelity_t = "{:.5f}".format(fidelity_t)

                fidelity.append(fidelity_t)
            # --------------------------------------------------------------------
            ro_t = U_data.dot(ro_t).dot(U_conj_data)
    # ----------------------------------------------------------------------------
    st = dict()

    for k in range(len(H.states)):
        if k in states:
            st[k] = str(H.states[k][1])
        else:
            st[k] = ""

    write_xbp(H.states, config.x_csv, ind=st)
    write_t(T_str_v(config.T), config.nt, config.y_csv)
    # ----------------------------------------------------------
    if fidelity_mode:
        list_to_csv(config.fid_csv, fidelity, header=["fidelity"])
    # ----------------------------------------------------------

# =====================================================================================================================
# import peakutils

# peaks = peakutils.indexes(diag_abs, thres=thres)


# for i in peaks:
#     states.add(i)
# =====================================================================================================================
