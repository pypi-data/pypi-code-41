import numpy as np
import plotnine as gg

from lazytools.to_dataframe import *

def matrix_heatmap(matrix, pole = None):
    """
    Returns a matrix heatmap, either centered around a pole or unidirectional
    (if pole is 'None', the default option).
    """
    assert matrix.ndim == 2
    df_matrix = array_to_dataframe(matrix)
    heatmap = (gg.ggplot(df_matrix, gg.aes(x = 'dim1', y = 'dim0', fill = 'array')) + 
              gg.geom_tile() + 
              gg.theme_void() + 
              gg.scale_y_reverse() + 
              gg.labs(fill = None))
    if pole is None:
        heatmap += gg.scale_fill_gradient(low = 'white', high = 'black')
    else:
        heatmap += gg.scale_fill_gradient2(low = 'blue', mid = 'white', high = 'red', midpoint = pole)
    return heatmap