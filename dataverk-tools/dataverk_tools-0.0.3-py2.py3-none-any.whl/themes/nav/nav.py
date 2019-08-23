from .._colormaps import _linear3color
from .colors import *


sequential = _linear3color(navRod, navLysBla, navBla)
diverging = _linear3color(navRod, navLysBla, navBla)
sequentialminus = _linear3color(navRod, navLysBla, navBla)

colorscale = [[i/10,color] for i, color in enumerate(sequential)]
colorscale_diverging = [[i/10,color] for i, color in enumerate(sequential)]
colorscale_sequential = [[i/10,color] for i, color in enumerate(sequential)]
colorscale_sequentialminus = [[i/10,color] for i, color in enumerate(sequential)]


discrete = [navRod, navOransje, navLimeGronn, navGronn, navLilla, navDypBla,
            navBla, navLysBla, navMorkGra, navGra40]


font_family = 'Helvetica Neue'
font_color  = '#2a3f5f'

linecolor = navGra20
gridcolor = navGra20
fillcolor = navRod

bgcolor = "white"

plotly_template = {
  "data": {
    "bar": [{"marker": {"line": {"color": bgcolor, "width": 0.5}}, "type": "bar"}],
    "barpolar": [{"marker": {"line": {"color": bgcolor, "width": 0.5}}, "type": "barpolar"}],
    "carpet": [
      {
        "aaxis": {
          "endlinecolor": "#2a3f5f",
          "gridcolor": gridcolor,
          "linecolor": gridcolor,
          "minorgridcolor": gridcolor,
          "startlinecolor": "#2a3f5f"
        },
        "baxis": {
          "endlinecolor": "#2a3f5f",
          "gridcolor": gridcolor,
          "linecolor": gridcolor,
          "minorgridcolor": gridcolor,
          "startlinecolor": "#2a3f5f"
        },
        "type": "carpet"
      }
    ],
    "choropleth": [
      {
        "colorbar": {
          "outlinewidth": 0,
          "ticks": ""
        },
        "type": "choropleth"
      }
    ],
    "contour": [
      {
        "colorbar": {
          "outlinewidth": 0,
          "ticks": ""
        },
        "colorscale": colorscale,
        "type": "contour"
      }
    ],
    "contourcarpet": [
      {
        "colorbar": {
          "outlinewidth": 0,
          "ticks": ""
        },
        "type": "contourcarpet"
      }
    ],
    "heatmap": [
      {
        "colorbar": {
          "outlinewidth": 0,
          "ticks": ""
        },
        "colorscale": colorscale,
        "type": "heatmap"
      }
    ],
    "heatmapgl": [
      {
        "colorbar": {
          "outlinewidth": 0,
          "ticks": ""
        },
        "type": "heatmapgl"
      }
    ],
    "histogram": [
      {
        "marker": {
          "colorbar": {
            "outlinewidth": 0,
            "ticks": ""
          }
        },
        "type": "histogram"
      }
    ],
    "histogram2d": [
      {
        "colorbar": {
          "outlinewidth": 0,
          "ticks": ""
        },
        "colorscale": colorscale,
        "type": "histogram2d"
      }
    ],
    "histogram2dcontour": [
      {
        "colorbar": {
          "outlinewidth": 0,
          "ticks": ""
        },
        "colorscale": colorscale,
        "type": "histogram2dcontour"
      }
    ],
    "mesh3d": [
      {
        "colorbar": {
          "outlinewidth": 0,
          "ticks": ""
        },
        "type": "mesh3d"
      }
    ],
    "parcoords": [
      {
        "line": {
          "colorbar": {
            "outlinewidth": 0,
            "ticks": ""
          }
        },
        "type": "parcoords"
      }
    ],
    "scatter": [
      {
        "marker": {
          "colorbar": {
            "outlinewidth": 0,
            "ticks": ""
          }
        },
        "type": "scatter"
      }
    ],
    "scatter3d": [
      {
        "marker": {
          "colorbar": {
            "outlinewidth": 0,
            "ticks": ""
          }
        },
        "type": "scatter3d"
      }
    ],
    "scattercarpet": [
      {
        "marker": {
          "colorbar": {
            "outlinewidth": 0,
            "ticks": ""
          }
        },
        "type": "scattercarpet"
      }
    ],
    "scattergeo": [
      {
        "marker": {
          "colorbar": {
            "outlinewidth": 0,
            "ticks": ""
          }
        },
        "type": "scattergeo"
      }
    ],
    "scattergl": [
      {
        "marker": {
          "colorbar": {
            "outlinewidth": 0,
            "ticks": ""
          }
        },
        "type": "scattergl"
      }
    ],
    "scattermapbox": [
      {
        "marker": {
          "colorbar": {
            "outlinewidth": 0,
            "ticks": ""
          }
        },
        "type": "scattermapbox"
      }
    ],
    "scatterpolar": [
      {
        "marker": {
          "colorbar": {
            "outlinewidth": 0,
            "ticks": ""
          }
        },
        "type": "scatterpolar"
      }
    ],
    "scatterpolargl": [
      {
        "marker": {
          "colorbar": {
            "outlinewidth": 0,
            "ticks": ""
          }
        },
        "type": "scatterpolargl"
      }
    ],
    "scatterternary": [
      {
        "marker": {
          "colorbar": {
            "outlinewidth": 0,
            "ticks": ""
          }
        },
        "type": "scatterternary"
      }
    ],
    "surface": [
      {
        "colorbar": {
          "outlinewidth": 0,
          "ticks": ""
        },
        "type": "surface"
      }
    ],
    "table": [
      {
        "cells": {
          "fill": {
            "color": linecolor
          },
          "line": {
            "color": bgcolor
          }
        },
        "header": {
          "fill": {
            "color": gridcolor
          },
          "line": {
            "color": bgcolor
          }
        },
        "type": "table"
      }
    ]
  },
  "layout": {
    "annotationdefaults": {
      "arrowcolor": "#506784",
      "arrowhead": 0,
      "arrowwidth": 1
    },
    "colorscale": {
      "diverging": colorscale_diverging,
      "sequential": colorscale_sequential,
      "sequentialminus": colorscale_sequentialminus,
    },
    "colorway": discrete,
    "font": {
      "color": font_color,
      "family": font_family
    },
    "geo": {
      "bgcolor": bgcolor,
      "lakecolor": "white",
      "landcolor": "white",
      "showlakes": True,
      "showland": True,
      "subunitcolor": gridcolor
    },
    "hoverlabel": {
      "align": "left"
    },
    "hovermode": "closest",
    "mapbox": {
      "style": "light"
    },
    "paper_bgcolor": bgcolor,
    "plot_bgcolor": bgcolor,
    "polar": {
      "angularaxis": {
        "gridcolor": linecolor,
        "linecolor": linecolor,
        "ticks": ""
      },
      "bgcolor": bgcolor,
      "radialaxis": {
        "gridcolor": linecolor,
        "linecolor": linecolor,
        "ticks": ""
      }
    },
    "scene": {
      "xaxis": {
        "backgroundcolor": bgcolor,
        "gridcolor": gridcolor,
        "gridwidth": 2,
        "linecolor": linecolor,
        "showbackground": True,
        "ticks": "",
        "zerolinecolor": linecolor
      },
      "yaxis": {
        "backgroundcolor": bgcolor,
        "gridcolor": gridcolor,
        "gridwidth": 2,
        "linecolor": linecolor,
        "showbackground": True,
        "ticks": "",
        "zerolinecolor": linecolor
      },
      "zaxis": {
        "backgroundcolor": bgcolor,
        "gridcolor": gridcolor,
        "gridwidth": 2,
        "linecolor": linecolor,
        "showbackground": True,
        "ticks": "",
        "zerolinecolor": linecolor
      }
    },
    "shapedefaults": {
      "fillcolor": fillcolor,
      "line": {
        "width": 0
      },
      "opacity": 0.4
    },
    "ternary": {
      "aaxis": {
        "gridcolor": gridcolor,
        "linecolor": "#A2B1C6",
        "ticks": ""
      },
      "baxis": {
        "gridcolor": gridcolor,
        "linecolor": "#A2B1C6",
        "ticks": ""
      },
      "bgcolor": bgcolor,
      "caxis": {
        "gridcolor": gridcolor,
        "linecolor": "#A2B1C6",
        "ticks": ""
      }
    },
    "title": {
      "x": 0.05
    },
    "xaxis": {
      "automargin": True,
      "gridcolor": linecolor,
      "linecolor": linecolor,
      "ticks": "",
      "zerolinecolor": linecolor,
      "zerolinewidth": 2
    },
    "yaxis": {
      "automargin": True,
      "gridcolor": linecolor,
      "linecolor": linecolor,
      "ticks": "",
      "zerolinecolor": linecolor,
      "zerolinewidth": 2
    }
  }
}


