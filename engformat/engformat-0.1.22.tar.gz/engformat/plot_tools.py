__author__ = 'maximmillen'
from matplotlib.collections import LineCollection
import matplotlib.transforms
import numpy as np

from bwplot import cbox


def trim_ticks(sub_plot, **kwargs):
    balance = kwargs.get('balance', False)
    xlims = sub_plot.get_xlim()
    xticks = list(sub_plot.get_xticks())
    pts = len(xticks)
    for i in range(pts - 1, 0, -1):
        if xticks[i] < xlims[0] or xticks[i] > xlims[1]:
            xticks.pop(i)
    sub_plot.set_xticks(xticks)

    ylims = sub_plot.get_ylim()
    yticks = list(sub_plot.get_yticks())
    pts = len(yticks)
    for i in range(pts - 1, 0, -1):
        if yticks[i] < ylims[0] or yticks[i] > ylims[1]:
            yticks.pop(i)
    if balance and (yticks[0] / -yticks[-1]) - 1.0 > 0.001:
        max_end = np.max([abs(yticks[0]), abs(yticks[-1])])
        tick_delta = abs(yticks[1] - yticks[0])
        yticks = np.arange(-max_end, max_end + tick_delta, tick_delta)
    sub_plot.set_yticks(yticks)


def revamp_legend(sub_plot, ncol=1, **kwargs):
    loc = kwargs.get('loc', 'upper right')
    single = kwargs.get('single', True)
    bbox_to_anchor = kwargs.get('bbox_to_anchor', False)
    prop = kwargs.get('prop', None)
    add_handles = kwargs.get("add_handles", [])

    if single:
        handles, labels = sub_plot.get_legend_handles_labels()
        labs = []
        hands = []
        for qq in range(len(labels)):
            if labels[qq] not in labs:
                labs.append(labels[qq])
                hands.append(handles[qq])
        for hand in add_handles:
            labs.append(hand.get_label())
            hands.append(hand)

    else:
        hands, labs = sub_plot.get_legend_handles_labels()

    if bbox_to_anchor != False:
        sub_plot.legend(hands, labs, numpoints=1, handlelength=1, handletextpad=0.5, labelspacing=0.3, scatterpoints=1,
                        loc=loc, ncol=ncol, bbox_to_anchor=bbox_to_anchor, prop=prop)
    else:
        sub_plot.legend(hands, labs, numpoints=1, handlelength=1, handletextpad=0.5, labelspacing=0.3, scatterpoints=1,
                        loc=loc, ncol=ncol, prop=prop)
    # borderpad    the fractional whitespace inside the legend border
    # shadow    if True, draw a shadow behind legend
    # framealpha    If not None, alpha channel for the frame.
    # ncol    number of columns
    # labelspacing    the vertical space between the legend entries
    # handlelength    the length of the legend handles
    # handletextpad    the pad between the legend handle and text
    leg = sub_plot.get_legend()


    try:  # check if plot has a legend
        frame = leg.get_frame()
    except AttributeError:
        return

    # leg.set_fancybox(True)
    ltext = leg.get_texts()  # all the text.Text instance in the legend
    # llines = leg.get_lines()  # all the lines.Line2D instance in the legend
    frame.set_lw(0.5)
    frame.set_facecolor('0.99')
    frame.set_edgecolor('0.3')
    frame.set_alpha(kwargs.get('alpha', 1.0))
    for tt in ltext:
        tt.set_color('0.1')
        # tt.set_size(7)
    return leg


def restyle_lines(sub_plot, style="bw", **kwargs):
    """
    Change the color and line style based on the bw_plot style.
    """

    if style == "bw":
        from bwplot.colours import cbox as cs
    elif style == "spectra":
        from bwplot.colours import spectra as cs

    lines = sub_plot.lines
    labs = {}
    cc_box = 0
    for i in range(len(lines)):
        label = lines[i].get_label()
        if "_line" == label[:5]:
            continue  # Don't recolor unlabelled lines

        if label not in labs:  # unique color for each label
            labs[label] = cc_box
            cc_box += 1
        lines[i].set_color(cs(labs[label]))


def letter_code(subplots, loc="upper left"):
    """
    Adds a letter from a to z to the corner of each subplot.
    """
    subplots = np.array(subplots)

    if loc == "upper left":
        x = 0.03
        y = 0.95
    elif loc == "upper right":
        x = 0.9
        y = 0.95
    elif loc == "lower left":
        x = 0.03
        y = 0.1
    elif loc == "lower right":
        x = 0.1
        y = 0.5
    elif isinstance(loc, tuple):
        x = loc[0]
        y = loc[1]
    else:
        raise ValueError("loc must be position string or a tuple.")
    letters = "abcdefghijklmnopqrstuvwxyz"
    flat_plots = subplots.flatten()
    for i in range(len(subplots)):
        flat_plots[i].text(x, y, '(%s)' % letters[i],
            verticalalignment='top', horizontalalignment='left',
            transform=flat_plots[i].transAxes,
            color='black', fontsize=9)


def clean_chart(ax):
    """
    Removes extra lines of axes and tick marks from chart.
    """
    edges = ['top', 'bottom', 'right', 'left']
    ax.tick_params(color=cbox('dark gray'))
    for edge in edges:
        ax.spines[edge].set_color(cbox('dark gray'))
        ax.spines[edge].set_linewidth(0.4)
    ax.yaxis.label.set_color(cbox('dark gray'))
    ax.xaxis.label.set_color(cbox('dark gray'))
    ax.tick_params(axis='y', colors='black', width=0, which='top')


def plot_multicolor_line(splot, x, y, z, cmap=None, vmin=None, vmax=None, lw=None, label=None, off_x=0, off_y=0):
    # Based on the matplotlib example: https://matplotlib.org/gallery/lines_bars_and_markers/multicolored_line.html
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    xo = np.ones(len(segments)) * off_x
    yo = np.ones(len(segments)) * off_y
    # xyo = list(zip(xo, yo))
    xyo = np.array([xo, yo]).T
    lc = LineCollection(segments, cmap=cmap, offsets=xyo, transOffset=matplotlib.transforms.IdentityTransform())
    lc.set_array(z)
    lc.set_clim(vmin=vmin, vmax=vmax)
    if lw is not None:
        lc.set_linewidth(lw)
    if label is not None:
        lc.set_label(label)
    return splot.add_collection(lc)
