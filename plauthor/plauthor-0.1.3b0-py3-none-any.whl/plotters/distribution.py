__author__ = 'Shayan Fazeli'
__email__ = 'shayan@cs.ucla.edu'

"""
Plauthor: Distribution Plots
==========

The modules in this file are designed to assist the user in plotting the distribution-related scatter plots
and other variants of graphics demonstration, shedding light on how the data points are located in the system.
"""

# libraries
import os
from typing import List, Dict, Tuple
import numpy
import matplotlib.pyplot as plt
import plotnine as p9
import pandas
from plauthor.utilities import separate_path_and_file


def plot_binned_distribution_per_category(
        distribution_bundle: Dict[str, numpy.ndarray],
        number_of_bins: int = 1000,
        colors: List[str] = ['b', 'g', 'r', 'c', 'y', 'k'],
        alpha: float = 0.5,
        save_to_file: str = None,
        dpi: int = 150,
        show: bool = True
) -> None:
    """
    The :func:`plot_binned_distribution_per_category` is responsible to take in a dictionary of categories, each of
    which including a single-dimensional array of values. These values are the instantiations of that random
    variable, and are used in plotting the binned distributions. The output is either shoing a plot or saving it in a
    figure specified in the `save_to_file` parameter.

    This function can be used to observe multiple distributions at the same time.

    Also, note that the value-range of horizontal axis and the zoom are determined by the data values automatically
    in a way that allows the user to have a clear picture of the entire plot.

    Parameters
    ----------
    distribution_bundle: `Dict[str, numpy.ndarray]`, required
        The main input, which is dictionary of distributions for example:
        ```
        distribution_bundle = {'hr=0': np.array(...), 'hr=2': np.array(...)}
        ```
        Note that in the example above all the shape tuples are of length one.
    number_of_bins: `int`, optional (default=1000)
        Number of bins in each of the histograms determine the resolution and can be fine-tuned by the user in here.
    colors: `List[str]`, optional(default=['b', 'g', 'r', 'c', 'y', 'k'])
        The mapping from histogram index to the colors that we are going to represent them with. The format is the
        format of `matplotlib` colors and should be inserted as a list.
    alpha: `float`, optional (default=0.5)
        Alpha is the transparency factor which can be used in our case.
    save_to_file: `str`, optional (default=None)
        If the user intends to save the plot in a file, this parameter should have a value. The value must be a filepath.
    dpi: `int`, optional (default=150)
        The dpi for saving the plots indicating the image quality.
    show: `bool`, optional (default=True)
        This value is set to true if the user wants to observe the plot as well.

    Returns
    ----------
    This method is saving a file to the storage system, and plots a graph if requested, but it does not return anything.
    """

    plt.ioff()

    legends = list(distribution_bundle.keys())

    for i in range(len(legends)):
        if i == 0:
            min_of_all = distribution_bundle[legends[i]].min()
            max_of_all = distribution_bundle[legends[i]].max()
        else:
            min_of_all = min(min_of_all, distribution_bundle[legends[i]].min())
            max_of_all = max(max_of_all, distribution_bundle[legends[i]].max())

    bins = numpy.linspace(min_of_all, max_of_all, number_of_bins)

    plt.figure()
    for i in range(len(legends)):
        plt.hist(distribution_bundle[legends[i]], bins, alpha=alpha, color=colors[i])
    plt.legend(legends, loc='upper right')

    if save_to_file is not None:
        plt.savefig(os.path.abspath(save_to_file), dpi=dpi)

    if show:
        plt.show()


def plot_2d_distribution_per_category(
        dataframe: pandas.DataFrame,
        label_column: str,
        coordinates: Tuple[str],
        colors: List[str],
        coloring_style: str = 'manual',
        log_10_scale: bool = False,
        theme: str = 'gray',
        alpha: float = 0.5,
        save_to_file: str = None,
        dpi: int = 150
) -> p9.ggplot:
    """
    The :func:`plot_2d_distribution_per_category` helps with providing the user with a 2-dimensional plot of the
    whole distribution.

    Parameters
    ----------
    dataframe: `pandas.DataFrame`, required
        This is the main parameter that this method is supposed to work with, which is a dataframe with a label column
        (which is to help us determine the column) and coordinates for x and y axes.
    label_column: `str`, required
        The input dataframe must have a label_column (preferably integer starting from 0), the name of that
        column should be input here.
    coordinates: `Tuple[str]`, required
        This is a tuple of column names, the first one being the column in which the `x` values for our 2d plot
        are stored, and the other one corresponds to the `y` axis.
    colors: `List[str]`, required
        Depending on whether or not our `coloring_style` is manual or automatic, this can either be a list of colors
        or a list of two colors indicating a range of color values.
    coloring_style: `str`, optional (default='manual')
        Either `manual` or `gradient` which helps assigning colors to clusters.
    log_10_scale: `bool`, optional (default=False)
        If the user wants to take the logarithm in the basis of 10, this parameter should be set to 1.
    theme: `str`, optional (default='gray')
        This is the `theme` types, the acceped values are: ``['gray', 'dark', 'seaborn', 'light']``, the values
        are consistent with `plotnine` package's format.
    alpha: `float`, optional (default=0.5)
        The transparency intensity can be determined by setting this parameter.
    save_to_file: `str`, optional (default=None)
        If the user intends to save the plot in a file, this parameter should have a value. The value must be a filepath.
    dpi: `int`, optional (default=150)
        The dpi for saving the plots indicating the image quality.
    Returns
    ----------
    The output of this method is of `p9.ggplot` type.
    """
    assert coloring_style in ['manual', 'gradient'], "invalid coloring style"

    if coloring_style == 'gradient':
        assert len(colors) == 2, "you have chosen gradient style coloring, for colors you have to provide a list with the \
            First element being the color for low and the second the color for high."
        pplot = p9.ggplot(data=dataframe, mapping=p9.aes(x=coordinates[0], y=coordinates[1], color=label_column))
        pplot += p9.scale_color_gradient(low=colors[0], high=colors[1])
    elif coloring_style == 'manual':
        assert len(colors) == len(dataframe[label_column].unique()), "You have chosen per category manual coloring, therefore you have to provide the same number of colors"
        pplot = p9.ggplot(data=dataframe, mapping=p9.aes(x=coordinates[0], y=coordinates[1], color='factor(' + label_column + ')'))
        pplot += p9.scale_alpha_manual(colors)

    pplot += p9.geom_point(alpha=alpha)
    pplot += p9.xlab(coordinates[0]) + p9.ylab(coordinates[1])

    if log_10_scale:
        pplot += p9.scale_x_log10()

    if theme == 'gray':
        pplot += p9.theme_gray()
    elif theme == 'dark':
        pplot += p9.theme_dark()
    elif theme == 'seaborn':
        pplot += p9.theme_seaborn()
    elif theme == 'light':
        pplot += p9.theme_light()
    else:
        raise Exception('Theme type not supported, please add.')

    pplot += p9.theme(text=p9.element_text(size=8))

    if save_to_file is not None:
        save_directory, filename = separate_path_and_file(filepath=save_to_file)
        pplot.save(filename=filename, path=save_directory, dpi=dpi)
    else:
        pplot.draw()

    return pplot


def plot_violinbox_plots_per_category(
        dataframe: pandas.DataFrame,
        plot_type: str,
        target_feature: str,
        label_column: str,
        colors: List[str],
        coloring_style: str,
        value_skip_list: List = [],
        jitter_alpha: float = 0.7,
        plot_alpha: float = 0.5,
        log_10_scale: bool = False,
        theme: str = 'gray',
        save_to_file: str = None,
        dpi: int = 150,
        show: bool = True
) -> p9.ggplot:
    """
        The :func:`plot_violinbox_plots_per_category` helps with providing the user with nicely plotted violin and
        box plots of the distribution of data points.

        Parameters
        ----------
        dataframe: `pandas.DataFrame`, required
            This is the main parameter that this method is supposed to work with, which is a dataframe that has
            a label column in which we have integer values starting from 0, and a float feature column the distribution
            of which we tend to monitor.
        plot_type: `str`, required
            This value, either `box` or `violin`, determines the type of plot.
        target_feature: `str`, required
            This parameter is the column name of the features that we want to monitor.
        label_column: `str`, required
            The input dataframe must have a label_column (preferably integer starting from 0), the name of that
            column should be input here.
        colors: `List[str]`, required
            Depending on whether or not our `coloring_style` is manual or automatic, this can either be a list of colors
            or a list of two colors indicating a range of color values.
        coloring_style: `str`, optional (default='manual')
            Either `manual` or `gradient` which helps assigning colors to clusters.
        value_skip_list: `List`, optional (default=[])
            If some values in the feature column are to be skipped, they should be put in here so that they
            are ignored in the plots. For example, if for some reason some values are -10000000, they can be taken care
            of in here.
        jitter_alpha: `float`, optional (default=0.7)
            The jitter value transparency is set in this parameter.
        plot_alpha: `float`, optional (default=0.5)
            The transparency intensity can be determined by setting this parameter.
        log_10_scale: `bool`, optional (default=False)
            If the user wants to take the logarithm in the basis of 10, this parameter should be set to 1.
        theme: `str`, optional (default='gray')
            This is the `theme` types, the acceped values are: ``['gray', 'dark', 'seaborn', 'light']``, the values
            are consistent with `plotnine` package's format.
        save_to_file: `str`, optional (default=None)
            If the user intends to save the plot in a file, this parameter should have a value. The value must be a filepath.
        dpi: `int`, optional (default=150)
            The dpi for saving the plots indicating the image quality.
        show: `bool`, optional (default=True)
            Whether or not the plot is to be shown is set in this parameter.
        Returns
        ----------
        The output of this method is of `p9.ggplot` type.
        """
    if len(value_skip_list) > 0:
        df = dataframe[~dataframe[target_feature].isin(value_skip_list)]

    if coloring_style == 'gradient':
        assert len(colors) == 2, "you have chosen gradient style coloring, for colors you have to provide a list with the \
            First element being the color for low and the second the color for high."
        pplot = p9.ggplot(data=dataframe, mapping=p9.aes(x='factor(' + label_column + ')', y=target_feature, color=label_column))
        pplot += p9.scale_color_gradient(low=colors[0], high=colors[1])
    elif coloring_style == 'manual':
        assert len(colors) == len(df[label_column].unique()), "You have chosen per category manual coloring, therefore you have to provide the same number of colors"
        pplot = p9.ggplot(data=dataframe, mapping=p9.aes(x='factor(' + label_column + ')', y=target_feature, color='factor(' + label_column + ')'))
        pplot += p9.scale_alpha_manual(colors)

    pplot += p9.geom_jitter(alpha=jitter_alpha)

    if plot_type == 'box':
        pplot += p9.geom_boxplot(alpha=plot_alpha)
    elif plot_type == 'violin':
        pplot += p9.geom_violin(alpha=plot_alpha)
    else:
        raise Exception('unknown plot type, it must be violin or box.')

    if theme == 'gray':
        pplot += p9.theme_gray()
    elif theme == 'dark':
        pplot += p9.theme_dark()
    elif theme == 'seaborn':
        pplot += p9.theme_seaborn()
    elif theme == 'light':
        pplot += p9.theme_light()
    else:
        raise Exception('Theme type not supported, please add.')

    if log_10_scale:
        pplot += p9.scale_x_log10()

    if save_to_file is not None:
        save_directory, filename = separate_path_and_file(filepath=save_to_file)
        pplot.save(filename=filename, path=save_directory, dpi=dpi)

    if show:
        pplot.draw()

    return pplot