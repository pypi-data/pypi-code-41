import numpy as np
import pandas as pd

import math
import csv

# BEGIN----------------------------------------- PLOTLY ------------------
import plotly

token = [
    {
        'login': 'alexfmsu',
        'key': 'g8ocp0PgQCY1a2WqBpyr'
    },
    {
        'login': 'alexf-msu',
        'key': 'VSOCzkhAhdKQDuV7eiYq'
    },
    {
        'login': 'alexfmsu_anime1',
        'key': 'XvGFBp8VudOGfUBdUxGQ'
    },
    {
        'login': 'alexfmsu_distrib',
        'key': 'NmiOXaqFkIxx1Ie5BNju'
    },
    {
        'login': 'alexfmsu_movies',
        'key': '5kV1qs60mmivbVvXNJW6'
    }
]

token_num = 0


def change_token():
    global token_num
    token_num += 1

    if token_num >= len(token):
        print("LIMIT")
        exit(0)

    plotly.tools.set_credentials_file(
        token[token_num]['login'], token[token_num]['key'])


plotly.tools.set_credentials_file(token[0]['login'], token[0]['key'])

# plotly.tools.set_credentials_file(
# username="alexfmsu", api_key="g8ocp0PgQCY1a2WqBpyr")
# plotly.tools.set_credentials_file(
# username="alexf-msu", api_key="VSOCzkhAhdKQDuV7eiYq")

import plotly.plotly as py
import plotly.graph_objs as go
# END------------------------------------------- PLOTLY ------------------

# from config import *


def PYPLOT2D(data_0, online=True, filename="Plot", scale=1, to_file=''):
    data = []

    for i in data_0["y"]["data"]:
        plot = go.Scatter(
            x=data_0["x"]["data"],
            y=i,
            name="ph_1",

            line=dict(
                # color='blue',
                # color=("rgb(205, 12, 24)"),
                width=2
            )
        )

        data.append(plot)

    # print(data_0["x"])

    layout = dict(
        title=data_0["title"],
        width=1600,
        height=800*float(scale),

        margin=dict(l=180, t=-100, b=150),

        xaxis=dict(
            title=data_0["x"]["title"]+"<br>",
            titlefont=dict(
                color="#222",
                size=45,
            ),

            zeroline=True,

            rangemode='tozero',

            tickprefix=" "*50,
            ticks='outside',
            tickfont=dict(
                color="#000000",

                # color="#222",
                size=40,
            ),
            ticklen=10,

            linewidth=1,

            ticktext=data_0["x"]["ticktext"],
            # ticktext=data_0["x"]["ticktext"][::2],
            # tickvals=data_0["x"]["tickvals"][::2]
            tickvals=data_0["x"]["tickvals"]
        ),

        yaxis=dict(
            title=data_0["y"]["title"],
            titlefont=dict(
                color="#000000",
                # color="#222",
                size=45,
            ),

            zeroline=True,
            rangemode='tozero',

            ticks='outside',
            tickfont=dict(
                color="#000000",
                # color="#222",
                size=40,
            ),
            ticklen=10,
            tickprefix=" "*50,
            linewidth=1,
            # tickcolor='black',

            # ticktext=np.around(np.linspace(0, 1, 6), 1),
            # ticktext=np.around(np.linspace(0, 1, 11), 1),
            # ticktext=np.linspace(0, 1, 11),
            # tickvals=np.linspace(0, 1, 6),

            # range=[0, 1],
        ),
    )

    fig = dict(data=data, layout=layout)

    if online:
        py.plot(fig, filename=filename)
    else:
        if to_file:
            done = False

            while not done:
                try:
                    py.image.save_as(fig, filename=to_file)
                    done = True
                except plotly.exceptions.PlotlyRequestError:
                    change_token()

            return
        # plotly.offline.init_notebook_mode()
        plotly.offline.plot(fig, filename=filename + ".html")


def PYPLOT2DH(data_0, online=True, filename="Plot", scale=1, to_file=''):
    data = []

    for i in data_0["y"]["data"]:
        plot = go.Scatter(
            x=data_0["x"]["data"],
            y=i,
            name="ph_1",

            line=dict(
                # color='blue',
                # color=("rgb(205, 12, 24)"),
                width=2
            )
        )

        data.append(plot)

    # print(data_0["x"])

    layout = dict(
        title=data_0["title"],
        width=1800,
        height=800*float(scale),

        margin=dict(l=180, t=-100, b=150),

        xaxis=dict(
            title=data_0["x"]["title"]+"<br>",
            titlefont=dict(
                color="#222",
                size=40,
            ),

            zeroline=True,

            rangemode='tozero',

            tickprefix=" "*50,
            ticks='outside',
            tickfont=dict(
                color="#000000",

                # color="#222",
                size=35,
            ),
            ticklen=10,

            linewidth=2,

            ticktext=data_0["x"]["ticktext"][::2],
            tickvals=data_0["x"]["tickvals"][::2]
        ),

        yaxis=dict(
            title=data_0["y"]["title"],
            titlefont=dict(
                color="#000000",
                # color="#222",
                size=40,
            ),

            zeroline=True,
            rangemode='tozero',

            ticks='outside',
            tickfont=dict(
                color="#000000",
                # color="#222",
                size=35,
            ),
            ticklen=10,
            tickprefix=" "*50,
            linewidth=2,
            # tickcolor='black',

            # ticktext=np.around(np.linspace(0, 1, 6), 1),
            # ticktext=np.around(np.linspace(0, 1, 11), 1),
            # ticktext=np.linspace(0, 1, 11),
            tickvals=np.linspace(0, 1, 6),

            range=[0, 1],
        ),
    )

    fig = dict(data=data, layout=layout)

    if online:
        py.plot(fig, filename=filename)
    else:
        if to_file:
            done = False

            while not done:
                try:
                    py.image.save_as(fig, filename=to_file)
                    done = True
                except plotly.exceptions.PlotlyRequestError:
                    change_token()

            return
        # plotly.offline.init_notebook_mode()
        plotly.offline.plot(fig, filename=filename + ".html")
