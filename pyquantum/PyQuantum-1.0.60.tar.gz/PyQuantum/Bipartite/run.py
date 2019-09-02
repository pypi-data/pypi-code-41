# -------------------------------------------------------------------------------------------------
# system
from PyQuantum.Common.STR import *
import sys
# -------------------------------------------------------------------------------------------------
# Bipartite
from PyQuantum.Bipartite.Cavity import *
from PyQuantum.Bipartite.Hamiltonian import *

from PyQuantum.Bipartite.WaveFunction import *
from PyQuantum.Bipartite.DensityMatrix import *

from Evolution import *
# -------------------------------------------------------------------------------------------------
# Common
from PyQuantum.Common.LoadPackage import *

from PyQuantum.Common.ext import mkdir
from PyQuantum.Common.PyPlot import PyPlot3D
from shutil import copyfile
from numpy.random import rand
# -------------------------------------------------------------------------------------------------
config = load_pkg("config", "Bipartite/config.py")

mkdir(config.path)
copyfile("Bipartite/config.py", config.path + '/config.py')
# -------------------------------------------------------------------------------------------------
cavity = Cavity(n=config.n, wc=config.wc, wa=config.wa, g=config.g)

print("Cavity:", color="green")

print()

cavity.print_n()
cavity.print_wc()
cavity.print_wa()
cavity.print_g()

print("T:", config.T)
print("nt:", config.nt)
print("dt:", config.dt)
# -------------------------------------------------------------------------------------------------
H = Hamiltonian(capacity=config.capacity, cavity=cavity)

if __debug__:
    print("Hamiltonian states:", color="green")

    print()

    H.print_states()

    H.write_to_file(filename=config.H_csv)
    # H.print_html(filename=H_html)
# -------------------------------------------------------------------------------------------------
w_0 = WaveFunction(states=H.states, init_state=config.init_state)

# w_0.set_ampl(state=config.init_state, amplitude=1)


# w_0.set_ampl(state=config.init_state, amplitude=0)
# A = rand(2, 2)
# A_comp = A.view(dtype=np.complex128)

# w_0.set_ampl(state=st1, ampl=1)
# w_0.set_ampl(state=st2, ampl=1)
# st1 = [0, 1*config.n]
# st2 = [1*config.n, 0]
# print(st1, st2)
# w_0.set_ampl(state=st1, amplitude=A_comp[0][0])
# w_0.set_ampl(state=st2, amplitude=A_comp[1][0])

# B = rand(len(H.states), 2)
# B_comp = B.view(dtype=np.complex128)
# print(w_0.states)
# for k, v in w_0.states.items():
#     # print(v, v==)
#     w_0.set_ampl(state=v, amplitude=1)
# w_0.set_ampl(state=v, amplitude=B_comp[k][0])

w_0.normalize()
w_0.print()

if __debug__:
    print("Wave Function:", color="green")

    print()

    w_0.print()
# -------------------------------------------------------------------------------------------------
# ro_0 = DensityMatrix(w_0)

# if __debug__:
#     ro_0.write_to_file(filename=config.ro_0_csv)
# -------------------------------------------------------------------------------------------------

# run(ro_0, H, dt=config.dt, nt=config.nt, config=config, fidelity_mode=True)
run_w(w_0, H, dt=config.dt, nt=config.nt, config=config, fidelity_mode=True)
# run(ro_0, H, dt=config.dt, nt=config.nt, config=config, fidelity_mode=False)

# -------------------------------------------------------------------------------------------------

y_scale = 1

if config.T < 0.25 * config.mks:
    y_scale = 0.1
elif config.T <= 0.5 * config.mks:
    y_scale = 0.025
elif config.T == 0.5 * config.mks:
    y_scale = 0.01
elif config.T == 1 * config.mks:
    y_scale = 7.5
    # y_scale = 10
elif config.T == 5 * config.mks:
    y_scale = 1


if not __debug__:
    title = ""
    title += "<b>"
    title += "n = " + str(config.n)
    if config.capacity - config.n > 0:
        title += "<br>" + str(config.capacity - config.n) + \
            " фотонов в полости"
    # else:
    # title += "<br>" + "empty cavity"

    # title += "<br>atoms state: |Ψ<sub>0</sub> i = |11...1>A<sub>0</sub> |00...0>A<sub>1</sub> |vaki<sub>p</sub>" + \
    #     str(config.init_state)
    title += "<br>"
    title += "<br>w<sub>c</sub> = " + wc_str(config.wc)
    title += "<br>w<sub>a</sub> = " + wa_str(config.wa)
    title += "<br> g/hw<sub>c</sub> = " + str(config.g/config.wc)
    title += "<br>"
    title += "<br>"
    title += "</b>"

    PyPlot3D(
        title=title,
        z_csv=config.path + "/" + "z.csv",
        x_csv=config.path + "/" + "x.csv",
        y_csv=config.path + "/" + "t.csv",
        # t_coeff=20000 / 1000 * (config.T / 1e-6),
        online=False,
        path=config.path,
        filename="Bipartite",
        xaxis="states",
        yaxis="time, " + T_str_mark(config.T),
        y_scale=y_scale
    )
# -------------------------------------------------------------------------------------------------

fid_plot = True
# fid_plot = False

if fid_plot:
    from py import *

    def plot_fidelity(filename=config.fid_csv):
        z_data = pd.read_csv(filename)

        t = np.around(np.linspace(0, config.nt, config.nt), 3)

        title = ""
        title += "<span style='font-size:18'>"
        title += "<b>Fidelity</b>"
        title += "</span>"
        # title += "<br>"
        # title += "<span style='font-size:11'>"
        # title += "n = " + str(config.n)
        # title += "<br>init. state: " + str(config.init_state)
        # # title += "<br>t = " + T_str(config.T)
        # title += "<br>"
        # title += "<br>w<sub>c</sub> = " + wc_str(config.wc)
        # title += "<br>w<sub>a</sub> = " + wa_str(config.wa)
        # title += "<br>g = " + g_str(config.g)
        # title += "</span>"

        PYPLOT2D(
            data_0={
                "title": title,
                # "title": "<b>w<sub>c</sub> = w<sub>a</sub> = 2 PI x 0.5 MHz;\tg / (hw<sub>c</sub>) = 0.001<br>" +
                # "m = g<b>",
                "x": {
                    "title": "Time, " + T_str_mark(config.T),
                    "data": t,

                    "ticktext": np.around(np.linspace(0, T_str_v(config.T), 11), 3),
                    "tickvals": np.around(np.linspace(0, config.nt, 11), 3)
                },
                "y":
                {
                    "title": "Fidelity",
                    "data": [
                        z_data["fidelity"],
                    ]
                },
            },
            online=False,
            filename=config.path + "/" + "Fidelity"
        )

        return
        # --------------------------------

    def plot_fidelity_small(filename=config.fid_csv):
        z_data = pd.read_csv(filename)

        t = np.around(np.linspace(0, config.nt, config.nt), 3)

        title = ""
        title += "<span style='font-size:18'>"
        title += "<b>Fidelity</b>"
        title += "</span>"
        # title += "<br>"
        # title += "<span style='font-size:11'>"
        # title += "n = " + str(config.n)
        # title += "<br>init. state: " + str(config.init_state)
        # # title += "<br>t = " + T_str(config.T)
        # title += "<br>"
        # title += "<br>w<sub>c</sub> = " + wc_str(config.wc)
        # title += "<br>w<sub>a</sub> = " + wa_str(config.wa)
        # title += "<br>g = " + g_str(config.g)
        # title += "</span>"

        # PYPLOT2D(
        #     data_0={
        #         "title": title,
        #         # "title": "<b>w<sub>c</sub> = w<sub>a</sub> = 2 PI x 0.5 MHz;\tg / (hw<sub>c</sub>) = 0.001<br>" +
        #         # "m = g<b>",
        #         "x": {
        #             "title": "Time, " + T_str_mark(config.T),
        #             "data": t,

        #             "ticktext": np.around(np.linspace(0, T_str_v(config.T), 11), 3),
        #             "tickvals": np.around(np.linspace(0, config.nt, 11), 3)
        #         },
        #         "y":
        #         {
        #             "title": "Fidelity",
        #             "data": [
        #                 z_data["fidelity"],
        #             ]
        #         },
        #     },
        #     online=False,
        #     filename=config.path + "/" + "Fidelity_small"
        # )

        return
        # --------------------------------
    # plot_fidelity(config.fid_csv)
    # plot_fidelity(config.fid_small_csv)
    # plot_fidelity_small(config.fid_small_csv)
