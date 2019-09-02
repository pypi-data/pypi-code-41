# ---------------------------------------------------------------------------------------------------------------------
# scientific
import pandas as pd
import numpy as np
# ---------------------------------------------------------------------------------------------------------------------
# plotly
import plotly.graph_objs as go
import plotly
# ---------------------------------------------------------------------------------------------------------------------
# PyQuantum.Tools
from PyQuantum.Tools.Assert import *
# ---------------------------------------------------------------------------------------------------------------------
# warnings
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
# ---------------------------------------------------------------------------------------------------------------------


class PlotBuilderData3D:
    def __init__(self, args):
        for i in [
            'title',
            'x_title', 'y_title', 'z_title',
            'x_range', 'y_range',
            'x_data', 'y_data', 'z_data',
            'width', 'height',
            'ticks',
        ]:
            Assert(i in args, i + ' not in args', FILE(), LINE())

            self.title = args['title']

            self.x_title = args['x_title']
            self.y_title = args['y_title']
            self.z_title = args['z_title']

            # self.x_axis = args['x_axis']
            # self.y_axis = args['y_axis']
            # self.z_axis = args['z_axis']

            self.width = args['width']
            self.height = args['height']

            self.x_data = args['x_data']
            self.y_data = args['y_data']
            self.z_data = args['z_data']

            self.x_range = args['x_range']
            self.y_range = args['y_range']

            self.x_ticktext = args['x_ticktext']
            self.x_tickvals = args['x_tickvals']

            self.y_ticktext = args['y_ticktext']
            self.y_tickvals = args['y_tickvals']
            # self.z_range = args['z_range']

            self.t_coeff = 1

            self.ticks = args['ticks']

            self.to_file = args['to_file'] if 'to_file' in args else None

            if 'scale' in args:
                self.scale = args['scale']
            else:
                self.scale = {
                    'x': 1,
                    'y': 1,
                    'z': 1,
                }

    def prepare(self):
        # ---------------------
        print("Making plot...")
        # ---------------------
        # -------------------------------------------
        x_data = self.x_data
        y_data = self.y_data
        z_data = self.z_data
        # -------------------------------------------

        # ------------------------------------------------
        # x_ticktext = x_data
        # x_tickvals = x_data
        # x_tickvals = list(range(len(x_data)))

        # x_ticktext = [str(i) for i in x_ticktext]

        # x_ticktext = x_ticktext[::50]
        # x_tickvals = x_tickvals[::50]
        # ------------------------------
        # print('x_tickvals:', x_tickvals)
        # print('x_ticktext:', x_ticktext)
        # ------------------------------------------------

        # ------------------------------------------------
        # y_ticktext = y_data
        # y_ticktext = [str(i) for i in y_ticktext]

        # y_tickvals = list(range(len(y_data)))
        # y_tickvals = y_data
        # y_tickvals = np.array(y_tickvals) / self.t_coeff

        # y_ticktext = y_ticktext[::50]
        # y_tickvals = y_tickvals[::50]

        # y_tickvals = y_tickvals[::50]
        # ------------------------------
        # print('y_tickvals:', y_tickvals)
        # print('y_ticktext:', y_ticktext)
        # ------------------------------------------------

        data = [
            # go.Surface(
            #     showlegend=False,
            #     showscale=False,
            #     lighting=dict(diffuse=0.5, specular=.2, fresnel=0.2),
            #     z=z_data,
            #     # colorscale="Portland",
            #     # colorscale='Viridis',
            # )
            go.Surface(
                z=z_data,
                colorscale="Portland",
                contours=go.surface.Contours(
                    z=go.surface.contours.Z(
                        show=True,
                        usecolormap=True,
                        # highlightcolor="#42f462",
                        project=dict(z=True),
                        # colorscale="Portland",
                    )
                )
            )
        ]

        scale = 1
        # scale = int(y_ticktext[-1])

        layout = go.Layout(
            # needed
            # ---------------
            title='<b>' + self.title + '</b>',
            # ---------------

            # -----------------
            width=self.width,
            height=self.height,
            # -----------------

            titlefont=dict(
                family='Lato',
                color="#222",
                size=20,
            ),
            xaxis=dict(
                title=r'$\sqrt{(n_\text{c}(t|{T_\text{early}}))}$'
            ),
            # margin=go.Margin(
            #     l=0,
            #     r=0,
            #     b=0,
            #     t=35,
            #     pad=50,
            # ),

            # zaxis=dict(
            #     tickangle=90
            # ),

            # --------------
            # autosize=False,
            autosize=True,
            # --------------

            plot_bgcolor="#AAA",
            # paper_bgcolor="#AAA",

            scene=go.Scene(
                camera=dict(
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=0.2),
                    eye=dict(x=3.75, y=3.75, z=3.75)
                ),
                xaxis={
                    # --------------------
                    "title": self.x_title,
                    # --------------------

                    # ---------------------
                    # ---------------------

                    "linewidth": 2,

                    "showgrid": False,
                    "showline": False,

                    # -----------------------------------
                    'titlefont': dict(
                        family=self.ticks['family'],
                        color=self.ticks['color'],
                        size=self.ticks['title']['size'],
                    ),
                    'tickfont': dict(
                        family=self.ticks['family'],
                        color=self.ticks['color'],
                        size=self.ticks['size'],
                    ),
                    # -----------------------------------
                    # 'nticks': 5,
                    'tickangle': 0,
                    # 'orientation': 'h',


                    # 'autorange': True,
                    # "ticktext": self.x_tickvals,
                    "tickvals": self.x_tickvals,
                    "ticktext": self.x_ticktext,

                    # "showline":True,
                    # "ticks": "outside",
                    # "showticklabels": True,
                    # "tickvals": list(range(len(x_tickvals))),
                    # "ticktext": list(range(len(x_tickvals))),
                    # "tickangle": 45,
                    # "linecolor": "black",
                    # "linewidth": 2,
                },
                yaxis={
                    # --------------------------------
                    "title": self.y_title,
                    # "title": self.y_title+"\t\t\t\t.",
                    # --------------------------------

                    # ---------------------
                    # "ticktext": self.y_tickvals,
                    "tickvals": self.y_tickvals,
                    "ticktext": self.y_ticktext,
                    # ---------------------

                    "linewidth": 2,
                    # 'nticks': 5,
                    # 'autotick': False,
                    # 'tick0': 0.001,
                    # 'dtick': 0.5,
                    # -----------------------------------
                    'titlefont': dict(
                        family=self.ticks['family'],
                        color=self.ticks['color'],
                        size=self.ticks['title']['size'],
                    ),
                    'tickfont': dict(
                        family=self.ticks['family'],
                        color=self.ticks['color'],
                        size=self.ticks['size'],
                    ),
                    # -----------------------------------
                    'tickangle': 0,


                    # 'autorange': True,

                    # "linecolor": "black",
                },
                zaxis={
                    # --------------------
                    "title": self.z_title,
                    # --------------------

                    "linewidth": 2,
                    # 'nticks': 5,

                    # -----------------------------------
                    'titlefont': dict(
                        family=self.ticks['family'],
                        color=self.ticks['color'],
                        size=self.ticks['title']['size'],
                    ),
                    'tickfont': dict(
                        family=self.ticks['family'],
                        color=self.ticks['color'],
                        size=self.ticks['size'],
                    ),
                    # -----------------------------------
                    'tickangle': 0,

                    'autorange': True,

                    # 'usecolormap': True,
                    # 'highlightcolor': "#42f462",
                    # 'dtick': -20,
                    # "tickangle": 45,
                    # "linecolor": "black",
                    # "range": self.z_range,
                    # "transform": {"rotate": '0'}
                },
                aspectratio={
                    "x": self.scale['x'],
                    "y": self.scale['y'],
                    "z": self.scale['z'],
                },
            ),
            # showlegend=False
        )

        self.fig = go.Figure(data=data, layout=layout)

        if self.to_file:
            py.image.save_as(self.fig, filename=self.to_file)
            return

        return

    # -----------------------------------------------------------------------------------------------------------------
    def make_plot(self, online=False, path='', filename='1.html'):
        self.prepare()

        if online:
            plotly.offline.plot(self.fig, filename=path + filename)
        else:
            plotly.offline.init_notebook_mode()

            plotly.offline.iplot(self.fig)
    # -----------------------------------------------------------------------------------------------------------------


# =====================================================================================================================
# def iplot(self, z_csv, x_csv, y_csv, t_coeff=1, online=True, path=".", filename="wt2", to_file=""):
#     self.prepare(z_csv, x_csv, y_csv, t_coeff,
#                  online, path, filename, to_file)

#     plotly.offline.init_notebook_mode(connected=True)
#     plotly.offline.iplot(self.fig)
# =====================================================================================================================
# def plot(self, z_csv, x_csv, y_csv, t_coeff=1, online=True, path=".", filename="wt2", to_file=""):

# def plot(self, online=False, path='', filename='1.html'):
#     self.prepare()

#     plotly.offline.plot(self.fig, filename=path + filename)

#     self.prepare(z_csv, x_csv, y_csv, t_coeff,
#                  online, path, filename, to_file)

#     plotly.offline.plot(self.fig, filename=path + filename + ".html")
# =====================================================================================================================
# fig["layout"].update(scene=dict(aspectmode="data"))

# online = False

# if online:
#     py.iplot(fig, filename=filename)
#     # plotly.offline.init_notebook_mode()
#     # plotly.offline.iplot(fig, filename="wt.html")

#     # plotly.
#     # py.offline.iplot(fig, filename="wt")
# else:
#     # plotly.offline.init_notebook_mode(connected=True)
#     # plotly.offline.init_notebook_mode()
#     plotly.offline.plot(fig, filename=path + filename + ".html")
#     # plotly.offline.iplot(fig, filename=path + filename + ".html")
# =====================================================================================================================
# class PlotBuilder3D:
    #     def __init__(self, args):
    #         for i in [
    #             'title',
    #             'x_title', 'y_title', 'z_title',
    #             'x_range', 'y_range', 'z_range',
    #             'x_csv', 'y_csv', 'z_csv',
    #             'width', 'height',
    #             'y_scale',
    #         ]:
    #             Assert(i in args, i + ' not in args', FILE(), LINE())

    #         self.title = args['title']

    #         self.x_title = args['x_title']
    #         self.y_title = args['y_title']
    #         self.z_title = args['z_title']

    #         # self.x_axis = args['x_axis']
    #         # self.y_axis = args['y_axis']
    #         # self.z_axis = args['z_axis']

    #         self.width = args['width']
    #         self.height = args['height']

    #         self.y_scale = args['y_scale']

    #         self.x_csv = args['x_csv']
    #         self.y_csv = args['y_csv']
    #         self.z_csv = args['z_csv']

    #         self.x_range = args['x_range']
    #         self.y_range = args['y_range']
    #         self.z_range = args['z_range']

    #         self.t_coeff = 1

    #         self.to_file = args['to_file'] if 'to_file' in args else None

    #     def prepare(self):
    #         # ---------------------
    #         print("Making plot...")
    #         # ---------------------

    #         # -------------------------------------------
    #         z_data = pd.read_csv(self.z_csv, header=None)
    #         # -------------------------------------------

    #         # ------------------------------------------------
    #         x = pd.read_csv(self.x_csv, keep_default_na=False)

    #         x_header = list(x)[0]
    #         # x["x"] = list(x["x"])
    #         x_ticktext = list(x['x'])
    #         x_tickvals = list(x['vals'])
    #         # x_tickvals = np.linspace(
    #         # list(x["x"])[0], list(x["x"])[-1], 10)
    #         # x_ticktext = np.linspace(
    #         # list(x["vals"])[0], list(x["vals"])[-1], 10)

    #         # x_ticktext = np.round(x_ticktext, 2)
    #         # print(list(x["x"])[-1])
    #         for i in range(len(x_ticktext)):
    #             x_ticktext[i] = x_ticktext[i]
    #             x_ticktext[i] = str(x_ticktext[i])
    #         # ------------------------------
    #         print('x_tickvals:', x_tickvals)
    #         print('x_ticktext:', x_ticktext)
    #         # ------------------------------------------------

    #         # ------------------------------------------------
    #         y = pd.read_csv(self.y_csv, keep_default_na=False)
    #         y_header = list(y)[0]

    #         # print(list(y["y"]))
    #         # exit(0)
    #         # y["y"] = list(y["y"])
    #         # y["vals"] = list(y["vals"])
    #         # y_tickvals = np.linspace(
    #         # list(y["y"])[0], list(y["y"])[-1], 10)
    #         # y_ticktext = np.linspace(
    #         # list(y["vals"])[0], list(y["vals"])[-1], 10)
    #         # y_ticktext = np.round(y_ticktext, 2)
    #         y_ticktext = list(y["y"])
    #         y_tickvals = list(y["vals"])
    #         y_tickvals = np.array(y_tickvals) / self.t_coeff
    #         # ------------------------------
    #         print('y_tickvals:', y_tickvals)
    #         print('y_ticktext:', y_ticktext)
    #         # ------------------------------------------------

    #         data = [
    #             go.Surface(
    #                 showlegend=False,
    #                 showscale=False,
    #                 lighting=dict(diffuse=0.5, specular=.2, fresnel=0.2),
    #                 z=z_data.values,
    #                 colorscale="Portland",
    #             )
    #         ]

    #         scale = int(y_ticktext[-1])

    #         layout = go.Layout(
    #             # ---------------
    #             title='<b>' + self.title + '</b>',
    #             # ---------------

    #             # -----------------
    #             width=self.width,
    #             height=self.height,
    #             # -----------------

    #             # plot_bgcolor="#000000",
    #             # pap_bgcolor="#000000",

    #             titlefont=dict(
    #                 # --------------------------------
    #                 family='Lato',
    #                 # family="Courier New, monospace",
    #                 # family='Open Sans, sans-serif',
    #                 # --------------------------------

    #                 size=20,

    #                 color="#222"
    #             ),
    #             # margin=go.Margin(
    #             #     l=0,
    #             #     r=0,
    #             #     b=0,
    #             #     t=35,
    #             #     pad=50,
    #             # ),
    #             xaxis=dict(
    #                 ticks='outside',
    #                 tickfont=dict(
    #                     family='Lato',
    #                     color="#222",
    #                     # size=20,
    #                     size=200,
    #                 ),
    #                 # linecolor="black",
    #                 linewidth=2,
    #                 # autotick=False,
    #                 # dtick=1,
    #             ),
    #             yaxis=dict(
    #                 ticks='outside',
    #                 titlefont=dict(
    #                     # ------------------------------
    #                     family='Lato',
    #                     # family="Courier New, monospace",
    #                     # family='Old Standard TT, serif',
    #                     # ------------------------------

    #                     # --------
    #                     size=40,
    #                     # size=14,
    #                     # --------

    #                     # -------------
    #                     color="#222",
    #                     # color="#FFFFFF"
    #                     # -------------
    #                 ),
    #                 linewidth=2,

    #                 # autotick=False,
    #                 # dtick=1,
    #                 # tickangle=45,
    #                 # tickangle=90,

    #                 tickfont=dict(
    #                     family='Lato',
    #                     color="#222",
    #                     # --------
    #                     # size=20,
    #                     size=200,
    #                     # --------
    #                 ),
    #             ),
    #             # zaxis=dict(
    #             #     tickangle=90
    #             # ),

    #             # --------------
    #             autosize=False,
    #             # autosize=True,
    #             # --------------

    #             plot_bgcolor="#AAA",
    #             # paper_bgcolor="#AAA",

    #             scene=go.Scene(
    #                 camera=dict(
    #                     up=dict(x=0, y=0, z=1),
    #                     center=dict(x=0, y=0, z=0.2),
    #                     eye=dict(x=3.75, y=3.75, z=3.75)
    #                 ),
    #                 aspectratio={"x": 1, "y": self.y_scale * \
    #                              y_ticktext[-1], "z": 1},
    #                 xaxis={
    #                     # --------------------
    #                     "title": self.x_title,
    #                     # ---------------------
    #                     "tickvals": x_tickvals,
    #                     "ticktext": x_ticktext,
    #                     # ---------------------

    #                     "showgrid": False,

    #                     "showline": False,
    #                     # "showline":True,

    #                     # "ticks": "outside",
    #                     # "showticklabels": True,
    #                     # "linewidth": 1,

    #                     # "tickvals": list(range(len(x_tickvals))),
    #                     # "ticktext": list(range(len(x_tickvals))),

    #                     'titlefont': dict(
    #                         size=18,
    #                     ),
    #                     'tickfont': dict(
    #                         family='Lato',
    #                         size=14,
    #                     ),
    #                     'autorange': True,

    #                     # "tickangle": 45,
    #                     # "linecolor": "black",
    #                     # "linewidth": 2,
    #                 },
    #                 yaxis={
    #                     # --------------------------------
    #                     "title": self.y_title+"\t\t\t\t.",
    #                     # --------------------------------
    #                     "tickvals": y_tickvals[::2],
    #                     "ticktext": y_ticktext[::2],
    #                     # --------------------------------

    #                     'autorange': True,
    #                     # "linecolor": "black",
    #                     "linewidth": 2,
    #                     'titlefont': dict(
    #                         size=18,
    #                     ),
    #                     'tickfont': dict(
    #                         family='Lato',
    #                         size=14,
    #                     )
    #                 },
    #                 zaxis={
    #                     # --------------------
    #                     "title": self.z_title,
    #                     # "range": self.z_range,
    #                     # --------------------

    #                     'autorange': True,
    #                     # 'dtick': -20,
    #                     # "tickangle": 45,
    #                     # "linecolor": "black",
    #                     "linewidth": 2,
    #                     'titlefont': dict(
    #                         size=18,
    #                     ),
    #                     'tickfont': dict(
    #                         family='Lato',
    #                         size=14,
    #                     )
    #                     # "transform": {"rotate": '0'}
    #                 },
    #             ),

    #             showlegend=False
    #         )

    #         self.fig = go.Figure(data=data, layout=layout)

    #         if self.to_file:
    #             py.image.save_as(self.fig, filename=self.to_file)
    #             return

    #         return

    #     # -----------------------------------------------------------------------------------------------------------------
    #     def plot(self, online=False, path='', filename='1.html'):
    #         self.prepare()

    #         plotly.offline.plot(self.fig, filename=path + filename)
    #     # -----------------------------------------------------------------------------------------------------------------
    # =====================================================================================================================
