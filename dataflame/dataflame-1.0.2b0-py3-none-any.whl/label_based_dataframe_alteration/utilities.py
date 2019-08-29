__title__ = 'Project DataFlame'
__author__ = 'Shayan Fazeli'
__email__ = 'shayan@cs.ucla.edu'
__credit__ = 'erLab - University of California, Los Angeles'

"""
    DataFlame: Dataframe Utilities
    ==========
    This file includes the utilities that I have designed for dealing with dataframes, from linear and timewise interpolations to 
    a variety of data balancing techniques to be used in our systems (e.g. pyTorch data reading schemes). For a project which
     requiresis working with dataframes for the most part, being able to efficiently deal with them is of paramount importance.
"""

# libraries
from typing import List, Optional

import pandas
import numpy
from sklearn.utils import shuffle as sklearn_shuffler


# transition observation based on the dataframes
def regress_to_class(current_timestamp: int,
                     one_timestamp: int,
                     anticipation_time_window: float) -> float:
    """
    This function checks every timestamp against the timestamp of a class occurrence, and assigns a weight on it.
    Linear interpolation of the label column is what this function does, providing us with a "ramp" instead of having a
    step transition from 0 to 1.
    Parameters
    ----------
    current_timestamp: ``int``, required
        The timestamp of the current row
    one_timestamp: ``int``, required,
        The timestamp to the `1` in the label class that we want to check the current timestamps against.
    anticipation_time_window: ``float``, required
        This parameter determines how "wide" our ramps should be.

    Returns
    ----------
    The output of this method is a float which represents the value of the ramp.
    """
    anticipation_time_window = float(anticipation_time_window)
    if (current_timestamp <= one_timestamp) and (current_timestamp >= (one_timestamp - anticipation_time_window)):
        return (anticipation_time_window - one_timestamp + current_timestamp) / anticipation_time_window


def binary_label_regression_for_prediction(
        dataframe: pandas.DataFrame,
        label_column: str,
        timestamp_column: str,
        anticipation_time_window: float,
        id_column: str,
        number_of_classes: int = 2,
        label_to_assume_if_not_a_number : int = 0
):
    """
    This method is best used whenever we have the following problem:
    We are planning to use a sequence of feature vectors through time to predict a binary label (in case of multi-label, use one-vs-all approach to make it binary).
    This function helps with smoothing the slope from 0.0 (no tag present) to 1.0 (tag is detected).

    Parameters
    ----------
    dataframe: ``pandas.DataFrame``, required
        This function works with a ``pandas.dataframe``.
    label_column: ``str``, required
        The column for the labels (can include `0`, `1`, or `nan` as its values)
    timestamp_column: ``str``, required
        The timestamp column which can include int values or float values
    anticipation_time_window: ``float``, required,
        The time window of anticipation, must be in the same unit as the timestamp column in the df dataframe.
    id_column: ``str``, required
        In case of a machine learning dataset (like if we want to separate them by ``patient_id``) this column is used
        to differentiate in terms of interpolation between those.
    number_of_classes: ``int``, optional (default=2)
        The number of unique labels that you want in the end (the original is binary, and say based on
        your ramp you think you want `5`, then set this to `5`).
    label_to_assume_if_not_a_number: ``int``, optional (default=0)
        Fill the not a number labels in the end with this value

    Returns
    ----------
    The output of this is the dataframe with the label (which was previously a binary value) being regressed
    and then quantized using a ramp, and now has values 0 to `n` accordingly.

    `Remark: if you want a certain timewindow to be 1 too, use twice the timewindow and set the number of classes to 2.`
    """

    # verifications
    assert number_of_classes >= 2, "invalid number of classes, the minimum value is 2."

    # type casting
    dataframe.astype({
        label_column: 'float32',
        timestamp_column: 'int',
    }, inplace=True)

    # sorting the row values based on the timestamp column
    dataframe.sort_values(by=timestamp_column, inplace=True)

    # building the class bins
    class_bins = numpy.linspace(0, 1, number_of_classes)

    # there is a column for identifiers, we will use that to find the list of all the subjects
    subjects = list(dataframe[id_column].unique())

    # this "ramp" designing should be done subject-to-subject
    for subject in subjects:
        # first, we build a list of the timestamps of occurrences of 1s. The advantage of the method that we
        # designed in this is that for every point, which is not 1, the nearest 1 is the one affecting it therefore
        # we will avoid unnecessary damping which might drastically impact our inferences.
        timestamps_of_ones = []

        # finding the subject only
        tmp = dataframe.loc[dataframe[id_column] == subject, [timestamp_column, label_column]]

        # filling the "timestamps_of_ones" per this specific subject
        for i in range(tmp.shape[0]):
            if tmp.iloc[i, :][label_column] == 1:
                timestamps_of_ones.append(tmp.iloc[i, :][timestamp_column])

        # sort them from last to first
        timestamps_of_ones = sorted(timestamps_of_ones, reverse=True)

        # doing the regression in a for loop
        for timestamp_of_one in timestamps_of_ones:
            # for each one we will build an in-line callable
            regressor = lambda x: regress_to_class(x, timestamp_of_one, anticipation_time_window)
            # filling will take place using the in-line callable defined above.
            tmp[label_column] = tmp[timestamp_column].apply(regressor)
        # setting the values for the subject
        dataframe.loc[dataframe[id_column] == subject, [timestamp_column, label_column]] = tmp

    if label_to_assume_if_not_a_number is not None:
        # filling the rest of the labels with "label_to_assume_if_not_a_number"
        dataframe[label_column] = dataframe[label_column].fillna(value=0)

    # the in-line function to assign the class that works based on finding the nearest bin
    assign_to_class = lambda x: numpy.argmin(numpy.abs(x - class_bins))

    # now, doing the assignments
    dataframe[label_column] = dataframe[label_column].apply(assign_to_class)

    # return the resulting dataframe
    return dataframe


# balancing dataframe by a special column
def balance_dataframe_by_label_column(
        dataframe: pandas.DataFrame,
        label_column: str,
        sample_count_per_category: Optional[int] = 1000,
        shuffle: bool = True,
        list_of_accepted_outputs: List[str] = None,
        consider_this_number_of_frequent_labels_only: int = None
) -> pandas.DataFrame:
    """
    This method balances the dataframe by label column

    Parameters
    ----------
    dataframe: ``pandas.DataFrame``, required
        The data frame of our examples (assuming that we are working with a dataset in
        which examples an fit into RAM).
    label_column: ``str``, required
        The title of the column of categories is inserted as this variable.
    sample_count_per_category: ``Optional[int]``, optional (default=1000)
        In the output dataset, we have this number of examples in each category. Set this to None
        to use the maximum occurrences as this value.
    shuffle: ``bool``, optional (default=`True`)
        The value of this variable determines whether or not do you want to shuffle the dataframe
    list_of_accepted_outputs: ``List[str]``, optional (default=`None`)
        In case only a certain set of labels is to be accepted, they will be given to this.
    consider_this_number_of_frequent_labels_only: ``int``, optional (default=`None`)

    Returns
    ----------
    The output of this method is the now balanced dataframe.
    """

    # first, if we do not have a list of outputs that we accept nothing but them, and if
    # at the same time we want say 10 most frequent data, we need to use this function to choose those only.
    if list_of_accepted_outputs is None:
        if consider_this_number_of_frequent_labels_only is not None:
            # find the table of label counts
            counts_per_labels = dataframe.groupby(label_column).count()
            # choose a column (they are identical now)
            tmp_column = counts_per_labels.columns[0]
            # sort the couhnts and pick the dominant labels
            list_of_accepted_outputs = counts_per_labels.sort_values(by=tmp_column, ascending=False).index.tolist()[
                                       :consider_this_number_of_frequent_labels_only]
            dataframe = dataframe[dataframe[label_column].isin(list_of_accepted_outputs)]

    # otherwise:
    elif list_of_accepted_outputs is not None:
        # create a special filter and apply it to keep only those classes
        dataframe = dataframe[dataframe[label_column].isin(list_of_accepted_outputs)]

    # find the counts of the dataframe
    counts_dataframe = dataframe.groupby(label_column).count()

    # now we need to check if we need to have a specific sample count per category, otherwise will find the maximum and
    # take that as the number of examples that we want in the final output. This variable is mainly useful if we
    # are dealing with a terribly skewed dataframe, say, we have 1000000 of class A and 10 of class B, it is better
    # to have 10 of each in the final class than to have 1000000 of A and 1000000 of B.
    if sample_count_per_category is not None:
        sample_count_per_category = counts_dataframe[counts_dataframe.columns[0]].max()

    # labels are to be found
    labels = list(dataframe[label_column].unique())

    # now we will find the dataframes and do the sampling with replacement
    dataframe_list = []
    for label in labels:
        if not pandas.isna(label):
            dataframe_list.append(
                dataframe[dataframe[label_column] == label].sample(sample_count_per_category, replace=True)
            )

    # to conserve memory:
    dataframe = None

    # everything comes together now:
    output_dataframe = pandas.concat(dataframe_list)

    # if shuffling is active, the sci-kit learn dataframe shuffler comes to play
    if shuffle:
        output_dataframe = sklearn_shuffler(output_dataframe)

    # it is ready now, and will be returned.
    return output_dataframe