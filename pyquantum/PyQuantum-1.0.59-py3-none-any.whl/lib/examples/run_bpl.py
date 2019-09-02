# -------------------------------------------------------------------------------------------------
# system
import sys
# -------------------------------------------------------------------------------------------------
# BipartiteLindblad
from PyQuantum.BipartiteLindblad.Cavity import *
from PyQuantum.BipartiteLindblad.Hamiltonian import *

from PyQuantum.BipartiteLindblad.WaveFunction import *
from PyQuantum.BipartiteLindblad.DensityMatrix import *

from PyQuantum.BipartiteLindblad.Evolution import *
# -------------------------------------------------------------------------------------------------
# Common
from PyQuantum.Common.LoadPackage import *
from PyQuantum.Common.STR import *

from PyQuantum.Common.ext import mkdir
from PyQuantum.Common.PyPlot import PyPlot3D
from shutil import copyfile
from numpy.random import rand
# -------------------------------------------------------------------------------------------------
config = load_pkg("config", "../PyQuantum/BipartiteLindblad/config.py")

mkdir(config.path)
copyfile("../PyQuantum/BipartiteLindblad/config.py",
         config.path + '/config.py')
# -------------------------------------------------------------------------------------------------
cavity = Cavity(n=config.n, wc=config.wc, wa=config.wa, g=config.g)

cavity.print()

print("T:", config.T)
print("nt:", config.nt)
print("dt:", config.dt)
# -------------------------------------------------------------------------------------------------
H = Hamiltonian(capacity=config.capacity, cavity=cavity)

H.print_states()

if __debug__:
    print("Hamiltonian states:", color="green")
    # H.print()
    print()

    H.print_states()

    H.write_to_file(filename=config.H_csv)
    # H.print_html(filename=H_html)
# -------------------------------------------------------------------------------------------------
w_0 = WaveFunction(states=H.states, init_state=config.init_state)

if __debug__:
    w_0.print()
# -------------------------------------------------------------------------------------------------
ro_0 = DensityMatrix(w_0)

if __debug__:
    ro_0.write_to_file(filename=config.ro_0_csv)
# -------------------------------------------------------------------------------------------------

run(ro_0, H, dt=config.dt, nt=config.nt,
    l=config.l, config=config, fidelity_mode=True)

# -------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------

y_scale = 1

if config.T == 0.05 * config.mks:
    y_scale = 0.1
if config.T == 0.25 * config.mks:
    y_scale = 0.025
elif config.T == 0.5 * config.mks:
    y_scale = 0.015
elif config.T == 1 * config.mks:
    y_scale = 10
elif config.T == 5 * config.mks:
    y_scale = 1


if not __debug__ or __debug__:
    title = ""
    title += "<b>"
    title += "n = " + str(config.n)
    title += "<br>"
    title += "<br>w<sub>c</sub> = " + wc_str(config.wc)
    title += "<br>w<sub>a</sub> = " + wa_str(config.wa)
    title += "<br>γ = " + g_str(config.l)
    title += "<br> g/hw<sub>c</sub> = " + str(config.g/config.wc)
    title += "<br>"
    title += "<br>"
    title += "</b>"

    if config.T / 1e-6 >= 0.5:
        PyPlot3D(
            title=title,
            z_csv=config.path + "/" + "z.csv",
            x_csv=config.path + "/" + "x.csv",
            y_csv=config.path + "/" + "t.csv",
            # t_coeff=20000 / 1000 * (config.T / 1e-6),
            # t_coeff=20000 / 1000 * (config.T / 1e-6),
            t_coeff=1,
            online=False,
            path=config.path,
            filename="Bipartite",
            xaxis="states",
            yaxis="time, " + T_str_mark(config.T),
            y_scale=y_scale
        )
    else:
        PyPlot3D(
            title=title,
            z_csv=config.path + "/" + "z.csv",
            x_csv=config.path + "/" + "x.csv",
            y_csv=config.path + "/" + "t.csv",
            # t_coeff=20000 / 1000 * (config.T / 1e-6),
            t_coeff=1,
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
    from PyQuantum.py import *
    print('fid')

    def plot_fidelity(filename=config.fid_csv):
        z_data = pd.read_csv(filename)

        t = np.around(np.linspace(0, config.nt, config.nt), 3)

        title = ""

        PYPLOT2D(
            data_0={
                "title": title,
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
    plot_fidelity()
# -------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------
    # title = ""
    # title = "<b>"
    # title += "n = " + str(config.n)
    # if config.capacity - config.n > 0:
    # title += "<br>" + str(config.capacity - config.n) + \
    # " photons in cavity"
    # title += "<br>atoms state: " + str(config.init_state[1:])
    # title += "<br>t = " + T_str(config.T)
    # title += "<br>"
    # title += "<br>w<sub>c</sub> = " + wc_str(config.wc)
    # title += "<br>w<sub>a</sub> = " + wa_str(config.wa)
    # title += "<br>g = " + g_str(config.g)
    # title += "<br>γ = " + g_str(config.l)
    # title += "</b>"

    # print(config.path)
    # PyPlot3D(
    #     title=title,
    #     z_csv=config.path + "/" + "z.csv",
    #     x_csv=config.path + "/" + "x.csv",
    #     y_csv=config.path + "/" + "t.csv",
    #     t_coeff=20000 / 1000 * (config.T / 1e-6),
    #     online=False,
    #     path=config.path,
    #     filename="BipartiteGeneral",
    #     xaxis="states",
    #     yaxis="time, " + T_str_mark(config.T),
    #     y_scale=y_scale
    # )
    # "title": "<b>w<sub>c</sub> = w<sub>a</sub> = 2 PI x 0.5 MHz;\tg / (hw<sub>c</sub>) = 0.001<br>" +
    # "m = g<b>",
    # title += "<span style='font-size:18'>"
    # title += "<b>Fidelity</b>"
    # title += "</span>"
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
