import plotly.plotly as py
import plotly.graph_objs as go

from PyQuantum.Tools.PlotBuilder2D import *

import plotly


# -------------------------------
def sup(s):
    if not isinstance(s, str):
        s = str(s)

    return '<sup>' + s + '</sup>'
# -------------------------------


# -------------------------------
def sub(s):
    if not isinstance(s, str):
        s = str(s)

    return '<sub>' + s + '</sub>'
# -------------------------------


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


class PlotBuilder2D:
    def __init__(self, args):
        self.title = args['title']

        self.x_title = args['x_title']
        self.y_title = args['y_title']

        self.data = args['data']

        self.html = args['html']

        self.to_file = args['to_file']if 'to_file' in args else None
        self.online = args['online'] if 'online' in args else None

    def make_plot(self):
        layout = dict(
            titlefont=dict(
                # --------------------------------
                family='Lato',
                # family="Courier New, monospace",
                # family='Open Sans, sans-serif',
                # --------------------------------

                size=20,

                color="#222"
            ),
            title='<b>' + self.title + '</b>',
            xaxis={
                'title': self.x_title,
                'linewidth': 2,
                'ticks': 'outside',
                'zeroline': False,
                'titlefont': dict(
                    family='Lato',
                    #     color="#000000",
                    color="#222",
                    size=18,
                ),
                'tickfont': dict(
                    family='Lato',
                    #     color="#000000",
                    color="#222",
                    size=16,
                ),
            },
            yaxis={
                'title': self.y_title,
                'tickangle': 0,
                'linewidth': 2,
                'ticks': 'outside',
                'zeroline': False,
                'titlefont': dict(
                    family='Lato',
                    #     color="#000000",
                    color="#222",
                    size=18,
                ),
                'tickfont': dict(
                    family='Lato',
                    #     color="#000000",
                    color="#222",
                    size=16,
                ),
            },
        )

        fig = dict(data=self.data, layout=layout)

        if self.online:
            py.plot(fig, filename=self.html)
        # py.plot(fig, filename=filename)
        else:
            if self.to_file:
                done = False

                while not done:
                    try:
                        py.image.save_as(fig, filename=self.to_file)
                        done = True
                    except plotly.exceptions.PlotlyRequestError:
                        change_token()
                        break
            else:
                plotly.offline.plot(fig, filename=self.html)
            # plotly.offline.init_notebook_mode()
