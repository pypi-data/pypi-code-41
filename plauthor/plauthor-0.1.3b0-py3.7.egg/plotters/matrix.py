__author__ = 'Shayan Fazeli'
__email__ = 'shayan@cs.ucla.edu'

import numpy
import matplotlib.pyplot as plt
from typing import List
import os, sys


# matrix visualization
def visualize_matrix(
        matrix: numpy.ndarray,
        column_names: List[str],
        row_names: List[str] = None,
        figure_size: float = 35.0,
        color_tone: str = 'red',
        save_to_file: str = None,
        round_to_this_decimal_places: int = 2,
        show: bool = True
):
    """
    The :meth:`visualize_matrix` helps with visualizing matrices in a grid.

    Parameters
    -----------
    matrix: `numpy.ndarray`, required
        The matrix to be visualized (must be 2 dimensional)
    column_names: `List[str]`, required
        The legends for the plot are found in this parameter's values, for each element.
    row_names: `List[str]`, required
        The legends for the plot are found in this parameter's values, for each element.
    figure_size: `float`, optional (default=35.0)
        The size of the output figure is determined in this parameter.
    color_tone: `str`, optional (default='red')
        The overall color tone for the plot is determined in this parameter.
    save_to_file: `str, optional (default=None)
        If a value is specified for this parameter, the figure will be saved in it.
    round_to_this_decimal_places: `int`, optional (default=2)
        This parameter denotes to how many decimal places should we show the values.
    show: `bool`, optional (default=True)
        Whether or not the user wants to see the plot as well is decided in this parameter.

    Returns
    -----------
    This method does not return anything.
    """
    plt.ioff()
    assert len(matrix.shape) == 2, "A 2D matrix is required in the input"

    if (column_names is not None) and (row_names is None) and (matrix.shape[0] == matrix.shape[1]):
        row_names = column_names
    elif (column_names is None) and (row_names is not None) and (matrix.shape[0] == matrix.shape[1]):
        column_names = row_names

    if column_names is not None:
        assert len(column_names) == matrix.shape[1], "check the labels and matrix dimensions again."
    if row_names is not None:
        assert len(row_names) == matrix.shape[0], "check the labels and matrix dimensions again."

    figure, axis = plt.subplots(figsize=(figure_size, figure_size))

    if color_tone == 'red':
        color_map = plt.cm.Reds
    elif color_tone == 'blue':
        color_map = plt.cm.Blues
    else:
        raise Exception('color tone is not recognized')

    axis.matshow(matrix, cmap=color_map)
    axis.set_xticks(numpy.arange(len(column_names))-0.5)
    axis.set_yticks(numpy.arange(len(row_names) + 1)-0.5)

    if column_names is not None:
        axis.set_xticklabels(column_names)
    if row_names is not None:
        axis.set_yticklabels(row_names)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            rounded_value = round(matrix[j, i], round_to_this_decimal_places)
            axis.text(i, j, str(rounded_value), va='center', ha='center')

    if save_to_file is not None:
        figure.savefig(os.path.abspath(save_to_file))

    if show:
        plt.show()
