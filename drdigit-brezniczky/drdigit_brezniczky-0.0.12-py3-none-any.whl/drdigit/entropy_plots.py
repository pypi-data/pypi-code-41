import matplotlib.pyplot as plt
from typing import List


def plot_entropy_distribution(actual_total_ent: float,
                              p: float,
                              entropies: List[float],
                              output_filename=None,
                              is_quiet=False,
                              title=None):
    """
    Plot and/or save an entropy distribution chart: a histogram with a specific
    value indicated with a vertical line and a probability to mention.

    :param actual_total_ent: the actual value
    :param p: estimated probability to display (could be inferred from the
        entropies but estimation specifics are rather left to the caller)
    :param entropies: known entropy values to be displayed as the distribution
    :param output_filename: If specified, the target image filename for saving
        the plot.
    :param is_quiet: whether to suppress any plots
    :return: None
    """
    # welcome to the late night boilerplate horror show ... or not?
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(entropies, bins = 40)
    ax.axvline(x=actual_total_ent, color="red")
    _, disp_y = ax.transAxes.transform((0, 1))
    disp_y -= 20
    x1, y = ax.transData.inverted().transform((10, disp_y))
    x2, _ = ax.transData.inverted().transform((0, disp_y))
    ax.text(actual_total_ent + x1 - x2, y,
            u"P \u2248 %.2f %%" % (p * 100))
    plt.xlabel("Entropy log likelihood")
    plt.ylabel("Frequency in sample")
    if title is not None:
        plt.title(title)
    if output_filename is not None:
        plt.savefig(output_filename)
    if not is_quiet:
        plt.show()
