import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.axes import Axes
import matplotlib.ticker as mtick
import scipy.stats as st
from typing import List


def _get_full_filename(fingerprint_dir: str, filename: str):
    if not os.path.exists(fingerprint_dir):
        os.mkdir(fingerprint_dir)
    full_filename = os.path.join(fingerprint_dir, filename)
    return full_filename


def _gaussian_kde_smoothed_points(
    x, y,
    xmin, xmax, nx,
    ymin, ymax, ny,
    weights=None
):
    # based on
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gaussian_kde.html
    # X, Y = np.mgrid([xmin:xmax:(nx)j, ymin:ymax:(ny)j])
    X, Y = np.mgrid[xmin:xmax:(nx)*1j, ymin:ymax:(ny)*1j]
    positions = np.vstack([X.ravel(), Y.ravel()])
    values = np.vstack([x, y])
    kernel = st.gaussian_kde(values, weights=weights)
    Z = np.reshape(kernel(positions).T, X.shape)
    return Z


def _plot_smoothed_hist_2d(x, y, weights=None, axes=None):
    # TODO: add norm_to_unit=False?
    new_plot = axes is None
    if not new_plot:
        dest = axes
    else:
        _, dest = plt.subplots(figsize=[8, 8])

    try:
        x = np.array(x)
        y = np.array(y)
        weights = np.array(weights)

        xmin, ymin = 0, 0
        xmax, ymax = 1, 1

        Z = _gaussian_kde_smoothed_points(
            x, y,
            xmin, xmax, 100,
            ymin, ymax, 100,
            weights=weights
        )

        # some alternative color maps to consider: magma, ocean, bone, coolwarm
        dest.imshow(
            np.rot90(Z), cmap="viridis",
            extent=[xmin, xmax, ymin, ymax]
        )

        if new_plot:
            plt.show()
    finally:
        if new_plot:
            plt.close()


def plot_fingerprint(party_votes: List[int], valid_votes: List[int],
                     registered_voters: List[int],  title: str,
                     filename: str=None, weighted: bool=True,
                     zoom_onto: bool=False, fingerprint_dir: str="",
                     quiet: bool=False, axes: Axes=None,
                     use_kde: bool=True):
    """
    Plot electoral fingerprint (a 2D histogram).
    Originally recommended to be used in conjunction with the winner party.

    :param party_votes: Array like of number of votes cast on the party
        depicted.
    :param valid_votes: Array like of valid votes (ballots) cast.
    :param registered_voters: Array like of all voters eligible to vote.
    :param title: Plot title.
    :param filename: Filename ot save the plot under, None to prevent saving.
        A .png extension seems to work ;)
    :param weighted: Whether to use the number of votes won as a weight on the
        histogram.
    :param zoom_onto: Boolean, allows to magnify the plot by a factor of 5/2
        over the y axis (vote share).
    :param fingerprint_dir: Directory to save the fingerprint plot to.
    :param quiet: Whether to show the resulting plot, False prevents it.
    :param axes: MatPlotLib  axes to plot onto. If left as None, a new plot will
        be generated.
    :param use_kde: Whether to use a default (Gaussian) kernel density
        estimation to smooth the plot. See scipy.stats.gaussian_kde for more.
        No finer grain control is available over the parameters at the minute.
    :return: None
    """
    # TODO: zooming in the KDE case
    bins = [np.arange(0, 1, 0.01), np.arange(0, 1, 0.01)]
    party_votes = np.array(party_votes)
    valid_votes = np.array(valid_votes)
    registered_voters = np.array(registered_voters)

    if zoom_onto:
        bins[1] = 0.4 * bins[1]

    weights = None if not weighted else party_votes

    if axes is not None:
        dest = axes
    else:
        _, dest = plt.subplots()

    try:
        # mainly for the KDE case, which does not tolerate NaNs, but neither is
        # the other case less correct if NaNs are removed, so...
        is_included = valid_votes != 0
        included_valid_votes = valid_votes[is_included]
        x = included_valid_votes / registered_voters[is_included]
        y = party_votes[is_included] / included_valid_votes
        included_weights = weights[is_included]

        if use_kde:
            _plot_smoothed_hist_2d(x, y, weights=included_weights, axes=dest)
        else:
            dest.hist2d(
                x, y,
                bins=bins,
                weights=weights
            )
        dest.set_title(title)

        dest.set_xlabel("Turnout")
        dest.set_ylabel("Vote share")

        perc_fmt = mtick.PercentFormatter(xmax=1)
        # https://stackoverflow.com/questions/31357611/format-y-axis-as-percent
        # (almost :) )
        dest.xaxis.set_major_formatter(perc_fmt)
        dest.yaxis.set_major_formatter(perc_fmt)

        if filename is not None:
            full_filename = _get_full_filename(fingerprint_dir, filename)
            plt.savefig(full_filename)
            if not quiet:
                print("plot saved as %s" % full_filename)
        if not quiet and axes is None:
            plt.show()
    finally:
        if axes is None:
            plt.close()


def plot_explanatory_fingerprint_responses(filename: str=None, quiet: bool=False,
                                           fontsize=12):
    """
    Plot a fingerprint explanation chart, optionally save/don't show it.
    Election fingerprints may be difficult to take in at first.

    :param filename: The figure is saved under this filename as an image if
        specified.
    :param quiet: Whether to avoid showing the plot.
    :param fontsize: Experimentally found that 15 is a good fit for a plot of
        pyplot.rcparams["figure.figsize"] = [9, 7], the default value seemed to
        work with the default plot size.
    :return:
    """
    fig, ax = plt.subplots()
    try:
        ax.set_title("Some responses of the election\n"
                     "fingerprint of a party to impacts",
                     fontsize=fontsize)
        ax.set_xlabel("Turnout")
        ax.set_ylabel("Vote share")
        perc_fmt = mtick.PercentFormatter(xmax=1)
        ax.xaxis.set_major_formatter(perc_fmt)
        ax.yaxis.set_major_formatter(perc_fmt)

        ax.text(0.75, 0.65,
                "+ votes\nof this\n"
                "\u21D2\n"
                "+ share\n+ turnout",
                fontsize=fontsize)
        ax.text(0.75, 0.15,
                "+ votes\nof other(s)\n"
                "\u21D2\n"
                "- share\n+ turnout",
                fontsize=fontsize)
        ax.text(0.1, 0.65,
                "- votes\nof other(s)\n"
                "\u21D2\n"
                "+ share\n- turnout",
                fontsize=fontsize)
        ax.text(0.1, 0.15,
                "- votes\nof this\n"
                "\u21D2\n"
                "- share\n- turnout",
                fontsize=fontsize)

        ax.text(0.40, 0.8, "\\\u263A/ party", fontsize=fontsize * 1.2)
        ax.text(0.40, 0.2, "/\u2639\\ party", fontsize=fontsize * 1.2)

        for dx in[-0.1, 0.1]:
            for dy in [-0.1, 0.1]:
                ax.arrow(0.5 + dx / 2, 0.5 + dy / 2, dx, dy,
                         head_width=0.025, head_length=0.025)

        if filename is not None:
            plt.savefig(filename)
            if not quiet:
                print("plot saved as %s" % filename)
        if not quiet:
            plt.show()
    finally:
        plt.close()



def plot_animated_fingerprints(party_votes: List[int],
                               valid_votes: List[int],
                               registered_voters: List[int],
                               frame_inclusions: List[List[bool]],
                               title: str,
                               filename: str=None,
                               weighted: bool=True,
                               zoom_onto: bool=False,
                               fingerprint_dir: str="", quiet: bool=False,
                               interval: int=200,
                               frame_title_exts: List[str]=None):

    """
    Can be used to plot an animated .gif showing how the distribution of votes
    changes over various subsets of the electoral wards involved. Technically,
    if party_votes, valid_votes, registered_voters are considered columns, the
    subsets boil down to various selections of the rows, specified by the
    frame_inclusions parameter.

    For the description of the rest of the parameters see plot_fingerprint().

    :param frame_inclusions: An array-like of row filters, each specifying a
        frame. Each row filter is just an array-like of booleans telling to
        include the nth row whenever the nth value is True.
    :param axes: axes to plot to, None to create a new plot.
    :param interval: animation interval to elapse between frames, in millisecs.
    :param frame_title_exts: Optional array-like of frame-specific text to
        display on each frame, such as a frame index. Currently it appears in
        the top left hand corner.
        This parameter is experimental and might change.
    :return: None
    """

    """ 
    based on 
    https://eli.thegreenplace.net/2016/drawing-animated-gifs-with-matplotlib/
    """
    fig, ax = plt.subplots()  # type: object, Axes

    def update(frame_index):
        include = frame_inclusions[frame_index]
        plot_fingerprint(
            party_votes[include], valid_votes[include],
            registered_voters[include], title,
            weighted=weighted, zoom_onto=zoom_onto,
            quiet=True, axes=ax
        )
        if frame_title_exts is not None:
            t = ax.text(0.1, 0.9, frame_title_exts[frame_index], color="white")
            t.set_bbox(dict(facecolor='black', alpha=1, edgecolor='black'))

    fig.set_tight_layout(True)
    anim = FuncAnimation(fig, update,
                         frames=list(range(len(frame_inclusions))),
                         interval=interval)
    if filename != "":
        full_filename = _get_full_filename(fingerprint_dir, filename)
        anim.save(full_filename, dpi=80, writer='imagemagick')
    if not quiet:
        plt.show()


if __name__ == "__main__":
    rv = np.random.uniform(20, 40, 300)
    vv = rv * np.random.uniform(0.6, 0.8, 300)
    pv = vv * np.random.uniform(0.6, 0.7, 300)
    plot_fingerprint(
        party_votes=pv,
        valid_votes=vv,
        registered_voters=rv,
        title="title1",
        use_kde=True,
    )
