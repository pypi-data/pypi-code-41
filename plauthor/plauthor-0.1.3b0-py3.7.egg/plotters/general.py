__author__ = 'Shayan Fazeli'
__email__ = 'shayan@cs.ucla.edu'

"""
Plauthor: General Plotters
==========

The methods in this module are mainly associated with general and unifying plotters.
"""

import numpy
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
import seaborn as sns
from typing import Tuple, Any, List


def scatter(
        x: numpy.ndarray,
        y: numpy.ndarray,
        figsize: int = 20
) -> Tuple[Any, Tuple[Any, Any], Any, List, int]:
    """
    The :func:`scatter` helps with normal scatter plots.
    Parameters
    -----------
    x: `numpy.ndarray`, required
        The values of x, a 2 dimensional array in which two columns exist.
    y: `numpy.ndarray`, required
        The values of y, or labels.
    figsize: `int`, optional (default=20)
        The figure size.
    Returns
    ----------
    (f, ax, sc, txt, number_of_classes): `Tuple`
        The output is the figure, axes, texts, and number of classes
    """
    plt.ioff()
    # We choose a color palette with seaborn.
    classes = [int(e) for e in numpy.unique(y).tolist()]
    number_of_classes = len(classes)
    palette = numpy.array(sns.color_palette("hls", number_of_classes))
    colors = y
    # We create a scatter plot.
    f = plt.figure(figsize=(figsize, figsize))
    ax = plt.subplot(aspect='equal')
    sc = ax.scatter(x[:, 0], x[:, 1], lw=0, s=40,
                    c=palette[colors])
    plt.xlim(numpy.min(x[:, 0].ravel())-1, numpy.max(x[:, 0].ravel())+1)
    plt.ylim(numpy.min(x[:, 1].ravel())-1, numpy.max(x[:, 1].ravel())+1)
    ax.axis('off')
    ax.axis('tight')
    # We add the labels for each digit.
    txts = []
    for i in range(number_of_classes):
        # Position of each label.
        xtext, ytext = numpy.median(x[colors == i, :], axis=0)
        txt = ax.text(xtext, ytext, str(i), fontsize=2)
        txt.set_path_effects([
            PathEffects.Stroke(linewidth=5, foreground="w"),
            PathEffects.Normal()])
        txts.append(txt)

    return f, ax, sc, txts, number_of_classes