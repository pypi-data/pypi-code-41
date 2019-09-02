import plotly.graph_objs as go
import plotly.plotly as py
import numpy as np
import pandas as pd

import math
import csv

# BEGIN--------------------------------------------------- PLOTLY -----------------------------------------------------
import plotly

# plotly.tools.set_credentials_file(username="alexfmsu", api_key="g8ocp0PgQCY1a2WqBpyr")
plotly.tools.set_credentials_file(
    username="alexf-msu", api_key="VSOCzkhAhdKQDuV7eiYq")

# END----------------------------------------------------- PLOTLY -----------------------------------------------------


# ---------------------------------------------------------------------------------------------------------------------
def PyPlot3D(title, z_csv, x_csv, y_csv, t_coeff=1, online=True, path=".", filename="wt2", xaxis="states", yaxis="time", to_file="", y_scale=1):
    print("Making plot...")
    # Z----------------------------------------------
    z_data = pd.read_csv(z_csv, header=None)
    # Z----------------------------------------------

    # X----------------------------------------------
    x = pd.read_csv(x_csv, keep_default_na=False)
    x.replace(r'\[(.+)\]', r'≺\1≻', regex=True, inplace=True)

    x_header = list(x)[0]
    x["x"] = list(x["x"])
    print(x["x"])
    print(x["vals"])
    # x_ticktext = list(x["x"])
    x_tickvals = np.linspace(
        list(x["x"])[0], list(x["x"])[-1], 6)
    # x_ticktext = np.linspace(0, len(x["x"]), 5)
    x_ticktext = np.linspace(0, list(x["vals"])[-1], 6)
    x_ticktext = np.round(x_ticktext, 2)
    x_ticktext /= 100
    # print(list(x["x"])[-1])
    # for i in range(len(x_ticktext)):
    # x_ticktext[i] = x_ticktext[i]
    # x_ticktext[i] = str(x_ticktext[i])
    # print(x["x"])
    print('x_ticktext:', x_ticktext)
    print('x_tickvals:', x_tickvals)
    # exit(0)
    # X----------------------------------------------

    # Y----------------------------------------------
    y = pd.read_csv(y_csv, keep_default_na=False)
    y_header = list(y)[0]

    # print(list(y["y"]))
    # exit(0)
    y["y"] = list(y["y"])
    y["vals"] = list(y["vals"])
    y_tickvals = np.linspace(list(y["y"])[0], list(y["y"])[-1], 5)
    y_ticktext = np.linspace(list(y["vals"])[0], list(y["vals"])[-1], 5)
    # y_ticktext = [1] + list(np.arange(10, y["vals"]+1, 10))
    # y_tickvals = np.linspace(
    #     list(y["y"])[0], list(y["y"])[-1], 5)
    # y_ticktext = np.linspace(
    #     list(y["vals"])[0], list(y["vals"])[-1], 5)
    # y_ticktext = np.round(y_ticktext, 2)
    # y_ticktext = list(y["y"])
    # y_tickvals = list(y["vals"])
    # y_tickvals = np.array(y_tickvals) / t_coeff
    print('y_ticktext:', y_ticktext)
    print('y_tickvals:', y_tickvals)
    # exit(0)
    # Y----------------------------------------------

    data = [
        go.Surface(
            showlegend=False,
            showscale=False,
            lighting=dict(diffuse=0.5, specular=.2, fresnel=0.2),
            z=z_data.as_matrix(),
            colorscale="Portland",
        )
    ]

    scale = int(y_ticktext[-1])

    layout = go.Layout(
        # plot_bgcolor="#000000",
        # pap_bgcolor="#000000",
        title=title,
        titlefont=dict(
            # family="Courier New, monospace",
            # family='Open Sans, sans-serif',
            family='Lato',

            size=20,
            color="#222"),
        # margin=go.Margin(
        #     l=0,
        #     r=0,
        #     b=0,
        #     t=35,
        #     pad=50,
        # ),
        xaxis=dict(
            # linecolor="black",
            # linewidth=2,
            autotick=False,
            # dtick=1,
            ticks='outside',
            tickfont=dict(
                # size=20,
                size=200,
            ),
        ),

        yaxis=dict(
            # tickangle=45,

            title="y Axis",
            titlefont=dict(
                family="Courier New, monospace",
                # family='Old Standard TT, serif',
                size=40,
                # size=14,
                color="#FFFFFF"),
            autotick=False,
            # dtick=1,
            ticks='outside',
            tickfont=dict(
                # size=20,
                size=200,
            ),
        ),
        # zaxis=dict(
        #     tickangle=90
        # ),


        autosize=False,
        # autosize=True,
        width=1200,
        height=650,
        plot_bgcolor="#AAA",
        # paper_bgcolor="#AAA",

        scene=go.Scene(
            camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0.2),
                eye=dict(x=3.75, y=3.75, z=3.75)
            ),
            aspectratio={"x": 1, "y": 1, "z": 1},
            # aspectratio={"x": 1, "y": y_scale * y_ticktext[-1], "z": 1},
            xaxis={
                "title": xaxis,
                "showgrid": False,
                "showline": False,
                # "showline":True,
                # "ticks": "outside",
                # "showticklabels": True,
                # "linewidth": 1,
                # "tickvals": list(range(len(x_tickvals))),
                # "ticktext": list(range(len(x_tickvals))),
                "tickvals": x_tickvals,
                "ticktext": x_ticktext,
                'titlefont': dict(
                    size=18,
                ),
                'tickfont': dict(
                    size=14,
                ),
                'autorange': True,

                # "tickangle": 45,
                # "linecolor": "black",
                # "linewidth": 2,
            },
            yaxis={
                'autorange': True,

                "title": yaxis+"\t\t\t\t.",
                "ticktext": y_ticktext,
                "tickvals": y_tickvals,
                # "linecolor": "black",
                "linewidth": 1,
                'titlefont': dict(
                    size=18,
                ),
                'tickfont': dict(
                    size=14,
                )
            },
            zaxis={
                'autorange': True,
                "range": [0, 1],
                "title": "",
                # "title": "prob.\t\t\t\t\t\t.",
                "title": "max(hp) / max(p(t))                                             .",
                # 'dtick': -20,
                # "tickangle": 45,
                # "linecolor": "black",
                "linewidth": 1,
                'titlefont': dict(
                    size=18,
                ),
                'tickfont': dict(
                    size=14,
                )
                # "transform": {"rotate": '0'}
            },
        ),

        showlegend=False
    )

    fig = go.Figure(data=data, layout=layout)

    if to_file:
        py.image.save_as(fig, filename=to_file)
        return
# fig["layout"].update(scene=dict(aspectmode="data"))
# online=False
    if online:
        py.plot(fig, filename=filename)
        # plotly.offline.init_notebook_mode()
        # plotly.offline.iplot(fig, filename="wt.html")

        # plotly.
        # py.offline.iplot(fig, filename="wt")
    else:
        # plotly.offline.init_notebook_mode()
        plotly.offline.plot(fig, filename=path + filename + ".html")

    return
# ---------------------------------------------------------------------------------------------------------------------
