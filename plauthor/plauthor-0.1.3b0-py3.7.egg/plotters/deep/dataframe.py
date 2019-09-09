__author__ = 'Shayan Fazeli'
__email__ = 'shayan@cs.ucla.edu'

"""
Plauthor: Dataframe Plots
==========

The modules in this file are designed to assist with plottings that are specially good for dataframes.
"""

import numpy
import pandas
import os
import _pickle as pickle
from typing import List, Dict, Tuple

from plauthor.plotters.deep.tsne import TSNEAgent
from dataflame.label_based_dataframe_alteration import balance_dataframe_by_label_column
from dataflame.statistics.utilities import compute_correlations_in_dataframe
from plauthor.plotters.general import scatter
from plauthor.plotters.matrix import visualize_matrix
from plauthor.plotters.distribution import plot_violinbox_plots_per_category, plot_binned_distribution_per_category, plot_2d_distribution_per_category
from copy import deepcopy
from plauthor.utilities import make_sure_the_folder_exists


def map_to_grouping(value: int, grouping: List[List[int]]) -> int:
    """
    Having the groupings helps with better understanding the between-group distributions. For more information,
    please refer to the instructions of `broadly_visualize_dataframe_with_respect_to_labels`.

    Parameters
    ----------
    value: `int`, required
        The prior value that is to be changed according to the group it belongs to.
    grouping: `List[List[int]]`, required
        The grouping list which is provided to the method

    Returns
    ----------
    It returns the integer value of the group that this variable belongs to.
    """
    for i in range(len(grouping)):
        if value in grouping[i]:
            return i

    raise ValueError


# dataframe visualization
def broadly_visualize_dataframe_with_respect_to_labels(
        dataframe: pandas.DataFrame,
        label_column: str,
        root_directory_for_results: str,
        balance_with_this_number_of_instances_in_each_class: int = None,
        shuffle_in_balancing: bool = True,
        subset_of_features: List[str] = None,
        label_groupings: List[List[List[int]]] = [],
        add_all_versus_all_grouping: bool = True,
        visualizations: List[str] = ['box', 'violin', 'tsne', 'histogram_distribution', '2d_scatter', 'correlations'],
        value_to_substitute_nans_with: float = -1000.0,
        dpi: int = 300,
        store_tsne_points_in_folder: str = None,
        verbose: bool = True
) -> None:
    """
    The :func:`broadly_visualize_dataframe_with_respect_to_labels`, is responsible for thoroughly perusing
    the dataframe and generate the graphics, etc.

    Remark: any interpolation, etc. should be handled independently and outside this method.

    ----------
    dataframe: `pandas.DataFrame`, required
        The main dataframe that this method is supposed to work with.
    label_column: `str`, required
        The title of the label column in the dataframe, which is going to include the `int` labels starting from
        `0` and is used for grouping, etc.
    root_directory_for_results: `str`, required
        The root directory for the results
    balance_with_this_number_of_instances_in_each_class: `int`, optional (default=None)
        If the dataset is imbalanced, for example if we have two million records in one dataset and 1002 from another class,
        it makes sense to want randomly chosen sets of 1000 from each to compare.
    shuffle_in_balancing: `bool`, optional (default=True)
        It is self explanatory I suppose.
    subset_of_features: `List[str]`, optional (None)
        If only a subset of features is requested to be incorporated in the plots, they can be passed in here. For example,
        only heart rate and creatinine.
    label_groupings: `List[List[List[int]]]`, optional (default=[])
        The default of this is 0. For example, assume that we have 4 classes and you want to see what happens if you
        treat calsses 0 and 1 as class 0, and class 2 as class 1. This is merely a renaming, which is important to be
        automatically handled in this case.
    add_all_versus_all_grouping: `bool`, optional (default=True)
        If this is true, an all-vs-all grouping (in which each class is its own) is automatically added.
    visualizations: `List[str]`, optionl (default=['box', 'violin', 'tsne', 'histogram_distribution', '2d_scatter', 'correlations'])
        The types of visualizations that the caller has decided to see can be selected in here.
    value_to_substitute_nans_with: `float`, optional (default=-1000.0)
        The not a number values will be substituted with the value provided in here.
    dpi: `int`, optional (default=300)
        The dpi based on which the images are to be saved. If the caller wants better quality (or more compressed
        results) this can be set.
    store_tsne_points_in_file: `str`, optional (default=None)
        Sometimes it is necessary to store the projected tsne points in files (for example, if you want to demonstrate them
        with a web-based library like d3). Setting this variable to a csv file helps us with that. This variable
        should include the path to the requested folder. It is the caller's responsibility to make sure
        that this path is valid, even though this method makes sure of that too.
    verbose: `bool`, optional (default=True)
        Whether or not the user wants to see the print messages that are output to stdout
    """

    # building the logger
    root_directory_for_results = make_sure_the_folder_exists(root_directory_for_results)
    store_tsne_points_in_folder = make_sure_the_folder_exists(store_tsne_points_in_folder)

    # verifications
    assert label_column in dataframe.columns.tolist(), "The specified label column does not exist."
    classes = dataframe[label_column].unique().tolist()
    assert min(classes) == 0, "The values in the label column should be integers starting from 0."
    assert max(classes) == len(classes) - 1, "The values in the label columns should be generated by the increments of 1"

    if verbose:
        print('status: initial assessments were successful.\n')

    if subset_of_features is not None:
        assert not label_column in subset_of_features, "label column should not exist in the feature subset given to this method."
        dataframe = dataframe.loc[:, subset_of_features + [label_column]]
        if verbose:
            print('status: the subset of features is selected and the rest are removed.\n')

    # handling the nans:
    dataframe.fillna(value_to_substitute_nans_with, inplace=True)
    if verbose:
        print('status: nan values are handled.\n')

    # building groupings
    if add_all_versus_all_grouping:
        # adding the default all versus all to it
        label_groupings.append([[e] for e in classes])
        if verbose:
            print('status: the all versus all mode is added to the groupings.')

    # processing all the groupings and generating the visualizations
    if verbose:
        print('status: going into handling groupings...\n')
    for grouping_index in range(len(label_groupings)):
        if verbose:
            print('status: group index in progress: %d\n' % grouping_index)

        # building the tsne agent to use later
        if verbose:
            tsne_verbose = 1
        else:
            tsne_verbose = 0

        tsne_agent = TSNEAgent(configurations={'tsne.verbose': tsne_verbose, 'tsne.n_components': 2})
        if verbose:
            print('status: tsne agent is built.\n')

        temporary_grouping_root_path = make_sure_the_folder_exists(
            os.path.join(os.path.abspath(root_directory_for_results),
                                                    'grouping_%d' % grouping_index)
        )

        # writing the grouping details
        grouping = label_groupings[grouping_index]
        with open(os.path.join(temporary_grouping_root_path, 'grouping_information.md'), 'w') as handle:
            handle.write('# Grouping information:\n')
            handle.write('- grouping: ' + str(grouping))

        # getting a copy of the dataframe
        temporary_dataframe = deepcopy(dataframe)

        # perform the groupings:
        temporary_dataframe[label_column] = temporary_dataframe[label_column].apply(
            lambda x: map_to_grouping(value=x, grouping=grouping))

        if balance_with_this_number_of_instances_in_each_class is not None:
            temporary_dataframe = balance_dataframe_by_label_column(dataframe=temporary_dataframe,
                                                                    label_column=label_column,
                                                                    sample_count_per_category=balance_with_this_number_of_instances_in_each_class,
                                                                    shuffle=shuffle_in_balancing)

        if 'tsne' in visualizations:
            # - TSNE ----------------------------------------------------------------------------------------------------------------------------------
            if verbose:
                print("preparing t-SNE visualizations...\n")
            y = temporary_dataframe[label_column]
            X = temporary_dataframe.drop(columns=[label_column]).to_numpy()

            # saving them to files
            temporary_path = make_sure_the_folder_exists(os.path.join(temporary_grouping_root_path, 'tsne_plots'))

            tsnes = {}
            for perplexity in [2, 5, 10, 25, 50, 100, 200]:
                if verbose:
                    print('status: handling perplexity={} for tsne visualization.\n'.format(perplexity))
                X_projections = tsne_agent.find_tsne_projections(X, perplexity=perplexity)
                tsnes[perplexity] = {'X_projections': X_projections, 'y': y}
                figure, *_ = scatter(X_projections, y.astype('int'))
                figure.savefig(os.path.join(temporary_path, "perplexity_%d.png" % perplexity), dpi=300)

            tsnes['grouping'] = label_groupings[grouping_index]
            pickle.dump(tsnes, open(os.path.join(store_tsne_points_in_folder, 'tsne_projections_for_grouping_index_of_%d.pkl' % grouping_index), 'wb'))
            # erasing tsne_agent
            tsne_agent = None
            # -----------------------------------------------------------------------------------------------------------------------------------------

        feature_list = temporary_dataframe.columns.tolist()
        feature_list.remove(label_column)

        if 'box' in visualizations:
            # - Box Plots -----------------------------------------------------------------------------------------------------------------------------
            if verbose:
                print('status: initiating box plot creations...\n')
            temporary_path = make_sure_the_folder_exists(os.path.join(temporary_grouping_root_path, 'box_plots'))
            for feature in feature_list:
                try:
                    temporary_plot = plot_violinbox_plots_per_category(
                        df=temporary_dataframe,
                        plot_type='box',
                        target_feature=feature,
                        label_column=label_column,
                        colors=['green', 'red'],
                        coloring_style='gradient',
                        value_skip_list=[value_to_substitute_nans_with],
                        jitter_alpha=0.7,
                        plot_alpha=0.5,
                        log_10_scale=False,
                        theme='gray',
                        save_to_file=os.path.join(temporary_path, '{}_log10scale_off.png'.format(feature)),
                        dpi=dpi
                    )
                    temporary_plot = plot_violinbox_plots_per_category(
                        df=temporary_dataframe,
                        plot_type='box',
                        target_feature=feature,
                        label_column=label_column,
                        colors=['green', 'red'],
                        coloring_style='gradient',
                        value_skip_list=[value_to_substitute_nans_with],
                        jitter_alpha=0.7,
                        plot_alpha=0.5,
                        log_10_scale=True,
                        theme='gray',
                        save_to_file=os.path.join(temporary_path, '{}_log10scale_on.png'.format(feature)),
                        dpi=dpi
                    )
                except:
                    print('warning: feature={} had issues for box plot.\n'.format(feature))

                if verbose:
                    print('status: box plots for feature={} are created.\n'.format(feature))

            # -----------------------------------------------------------------------------------------------------------------------------------------

        if 'violin' in visualizations:
            # - Violin Plots --------------------------------------------------------------------------------------------------------------------------
            if verbose:
                print('status: initiating violin plot creations...\n')
            temporary_path = make_sure_the_folder_exists(os.path.join(temporary_grouping_root_path, 'violin_plots'))
            for feature in feature_list:
                try:
                    temporary_plot = plot_violinbox_plots_per_category(
                        df=temporary_dataframe,
                        plot_type='violin',
                        target_feature=feature,
                        label_column=label_column,
                        colors=['green', 'red'],
                        coloring_style='gradient',
                        value_skip_list=[value_to_substitute_nans_with],
                        jitter_alpha=0.7,
                        plot_alpha=0.5,
                        log_10_scale=False,
                        theme='gray',
                        save_to_file=os.path.join(temporary_path, '{}_log10scale_off.png'.format(feature)),
                        dpi=dpi
                    )
                    temporary_plot = plot_violinbox_plots_per_category(
                        df=temporary_dataframe,
                        plot_type='violin',
                        target_feature=feature,
                        label_column=label_column,
                        colors=['green', 'red'],
                        coloring_style='gradient',
                        value_skip_list=[value_to_substitute_nans_with],
                        jitter_alpha=0.7,
                        plot_alpha=0.5,
                        log_10_scale=True,
                        theme='gray',
                        save_to_file=os.path.join(temporary_path, '{}_log10scale_on.png'.format(feature)),
                        dpi=dpi
                    )
                except:
                    print('warning: feature={} had issues for violin plot.\n'.format(feature))
                if verbose:
                    print('status: violin plots for feature={} are created.\n'.format(feature))

            # -----------------------------------------------------------------------------------------------------------------------------------------

        if '2d_scatter' in visualizations:
            # - 2D Scatter Plots ----------------------------------------------------------------------------------------------------------------------
            if verbose:
                print('status: initiating 2d scatter plot creations...\n')
            temporary_path = make_sure_the_folder_exists(os.path.join(temporary_grouping_root_path, '2d_scatter_plots'))
            count = 0
            total = len(feature_list) * (len(feature_list) - 1)
            for feature1 in feature_list:
                for feature2 in feature_list:
                    if feature1 == feature2:
                        continue
                    else:
                        count += 1
                        try:
                            temporary_plot = plot_2d_distribution_per_category(
                                df=temporary_dataframe,
                                label_column=label_column,
                                coordinates=(feature1, feature2),
                                colors=['green', 'red'],
                                coloring_style='gradient',
                                log_10_scale=False,
                                theme='gray',
                                alpha=0.3,
                                save_to_file=os.path.join(temporary_path, '{}_and_{}.png'.format(feature1, feature2)),
                                dpi=dpi
                            )
                            temporary_plot = plot_2d_distribution_per_category(
                                df=temporary_dataframe,
                                label_column=label_column,
                                coordinates=(feature1, feature2),
                                colors=['green', 'red'],
                                coloring_style='gradient',
                                log_10_scale=True,
                                theme='gray',
                                alpha=0.3,
                                save_to_file=os.path.join(temporary_path, '{}_and_{}.png'.format(feature1, feature2)),
                                dpi=dpi
                            )
                        except:
                            print('warning: feature={} had issues for 2d scatter plot\n'.format(feature1))
                            continue
                        if verbose:
                            print('status: the progress for 2d scatter plots: {}/{}\n'.format(count, total))

            # -----------------------------------------------------------------------------------------------------------------------------------------

        if 'histogram_distribution' in visualizations:
            # - Histogram Distribution Plots ----------------------------------------------------------------------------------------------------------
            if verbose:
                print('status: initiating histogram distribution plot creations...\n')
            if len(grouping) <= 4:
                temporary_path = os.path.join(temporary_grouping_root_path, 'histogram_distribution_plots')
                make_sure_the_folder_exists(temporary_path)
                count = 0
                total = len(feature_list)
                temporary_classes = temporary_dataframe[label_column].unique().tolist()
                for feature in feature_list:
                    count += 1
                    try:
                        distribution_bundle = dict()

                        for label in temporary_classes:
                            distribution_bundle[str(label)] = temporary_dataframe[temporary_dataframe[
                                                                                                label_column] == label].loc[
                                                                        :, feature].to_numpy().ravel()

                        for binsize in [25, 50, 100, 200]:
                            plot_binned_distribution_per_category(
                                distribution_bundle=distribution_bundle,
                                number_of_bins=binsize,
                                colors=['g', 'r', 'b', 'c'],
                                alpha=0.7,
                                save_to_file=os.path.join(temporary_path, '{}_binsize{}.png'.format(feature, binsize)),
                                dpi=dpi
                            )
                    except:
                        print('warning: feature={} had issues for histogram distribution plot'.format(feature))
                        continue

                    if verbose:
                        print('status: histogram distribution plots progress: {}/{}\n'.format(count, total))

            # -----------------------------------------------------------------------------------------------------------------------------------------

        if 'correlations' in visualizations:
            # - Correlations Plots --------------------------------------------------------------------------------------------------------------------
            if verbose:
                print('status: initiating correlation plots...\n')
            temporary_path = os.path.join(temporary_grouping_root_path, 'correlation_plots')
            make_sure_the_folder_exists(temporary_path)

            for method in ['pearson', 'spearman', 'kendall']:
                correlations_matrix, correlation_labels = compute_correlations_in_dataframe(temporary_dataframe,
                                                                                            correlation_method=method)

                temp_figure = visualize_matrix(
                    matrix=correlations_matrix,
                    column_names=correlation_labels,
                    save_to_file=os.path.join(temporary_path, '{}_correlations.png'.format(method)),
                    round_to_this_decimal_places=2
                )
                if verbose:
                    print('status: correlation plots for method={} is done\n'.format(method))

            # -----------------------------------------------------------------------------------------------------------------------------------------
