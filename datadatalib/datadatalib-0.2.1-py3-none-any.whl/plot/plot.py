from typing import List, Union
import pandas as pd
from pandas import Series, Index, DatetimeIndex

import numpy as np
from numpy import ndarray

from plotly.offline import iplot, init_notebook_mode
import plotly.offline as py
import plotly.graph_objs as go
import plotly.express as px

import enum
import colorlover as cl


class Colorscale(enum.Enum):
    RD_YL_GN = [
        [
            i / 10,
            cl.scales['11']['div']['RdYlGn'][i]
        ]
        for i in range(11)
    ]


def __plot_figure(
    traces: List[go.Scattergl],
    layout: go.Layout,
    filename: str,
    inline:bool = False
):

    data = traces
    fig = go.Figure(data=data, layout=layout)

    if inline:
        init_notebook_mode(connected=True)
        iplot(
            fig,
            filename=filename
        )
    else:
        py.plot(
            fig,
            filename=filename,
            auto_open=False
        )


def plot_scatters(
    xs: Union[List[Series], List[ndarray], List[Index], List[DatetimeIndex]],
    ys: Union[ndarray, List[pd.Series], List[ndarray]],
    title: str = 'Scatters',
    line_names: List[str] = None,
    modes: List[str] = None,
    x_label: str = 'x_label',
    y_label: str = 'y_label',
    filename: str = './temp_plot.html',
    inline: bool = False
):
    """
        Plot lines with plotly.

        Inputs:
        - x: List of indices.
        - ys: List of y coordinates.
        - title: Title of the plot.
        - line_names: Name for every line in ys. If None default names will be used. 
          That names will be used for legend.
        - modes: Any mode available for plotly.go.Scatter. Default - 'lines'.
        - x_label: Label of x axis.
        - y_label: Label of y axis.
        - filename: File name.
        - inline: If True plot graph inline. For using inside jupyter notebook.
    """

    # Check input data
    # assert isinstance(xs, List), f'xs: expected type is List, got {type(xs)} instead'
    # assert isinstance(ys, ndarray) or isinstance(ys, List), f'ys: expected type is ndarray, got {type(ys)} instead'
    # if ys.ndim == 1:
    #     ys = [ys.T]
    # elif ys.shape[1] != len(xs[0]):
    #     ys = ys.T
    

    traces: List[go.Scattergl] = []

    # Set lines names
    if line_names is None:
        line_names = [f'line{i}' for i in range(len(ys))]

    # Set lines modes
    if modes is None:
        modes = ['lines'] * len(ys)
    
    # Create traces
    if len(xs) == 1:
        xs = xs * len(ys)
    
    for i, line in enumerate(zip(xs, ys)):
        traces.append(
            go.Scattergl(
                x=line[0],
                y=line[1],
                name=line_names[i],
                mode=modes[i],
                showlegend=True
            )
        )

    layout = go.Layout(
        title=title,
        xaxis=dict(
            title=x_label,
            titlefont=dict(
                family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            )
        ),
        yaxis=dict(
            title=y_label,
            titlefont=dict(
                family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            )
        )
    )

    __plot_figure(
        traces, 
        layout, 
        filename,
        inline
    )


def plot_heatmap(
        df: pd.DataFrame,
        filename: str = './temp_heatmap.html',
        colorscale: Colorscale = Colorscale.RD_YL_GN,
        title: str = 'Heatmap',
        x_label: str = None,
        y_label: str = None,
        inline: bool = True
):
    """
        Plot heatmap with plotly.

        Inputs:
        - df: Matrix to plot.
        - filename: File name.
        - colorscale: Colorscale to use.
        - title: Title of the plot.
        - x_label: Label of x axis.
        - y_label: Label of y axis.
        - inline: If True plot graph inline. For using inside jupyter notebook.
    """

    trace = [
        go.Heatmap(
            x=df.columns,
            y=df.index,
            z=df.values,
            colorscale=colorscale.value
        )
    ]

    layout = go.Layout(
        title=title,
        yaxis=dict(
            title=y_label,
            scaleanchor="x"
        ),
        xaxis=dict(
            title=x_label
        )
    )

    __plot_figure(
        trace,
        layout,
        filename,
        inline
    )



