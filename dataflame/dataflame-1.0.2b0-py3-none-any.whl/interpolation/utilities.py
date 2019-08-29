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


# time interpolating the dataframe
def interpolate_dataframe(
        dataframe: pandas.DataFrame,
        id_column: str,
        features: List[str],
        nan_fill_value: Optional[float] = -10.0,
        interpolation_method: str = 'time',
        limit: int = 1000,
        limit_direction: str = 'both'
) -> pandas.DataFrame:
    """
    The method `interpolate_dataframe` is used whenever we have the following problem:
    We are planning to use a sequence of feature vectors through time to predict a binary label
    (in case of multi-label use one-vs-all approach to make it binary).
    This function helps with smoothening the slope from 0.0 (no tag present) to 1.0 (tag is detected).

    Parameters
    ----------
    dataframe: ``pandas.DataFrame``, required
        This variable is the pandas dataframe that we are working with.

    id_column: ``str``, required
        The value of this variable determines the `identifier` which is to be used, since the interpolation
        has to take place with regard to the ids.

    features: ``List[str]``, required
        This is the list of numerical features that you are going to apply the interpolation over.

    nan_fill_value: ``Optional[float]``, optional (default=-10.0)
        In the dataframe which is the subset given by the list of previously given features, this value will
        be filled as a substitution to the not a number values.

    interpolation_method: ``str``, optional (default="time")
        The value of this parameter is used for pandas interpolation scheme, note that if you are using the
        default version which is "time" you need to have a `Datetime` column as well, having the `Datetime` values.

    limit: ``int``, optional (default=1000)
        This parameter is to be used in ``pandas`` interpolation method.

    limit_direction: ``str``, optional (default=1000)
        This parameter is to be used in ``pandas`` interpolation method.

    Returns
    ----------
    The output of this method is the altered dataframe, in which according to the specified parameters
    interpolation has taken place.
    """

    # first, extracting the subjects because this too has to take place subject by subject
    subjects = list(dataframe[id_column].unique())

    # now for each subject, the computation takes place
    for subject in subjects:
        # first, segment the features and the subject
        tmp = dataframe.loc[dataframe[id_column] == subject, features]
        # do the interpolation
        tmp.interpolate(method=interpolation_method, limit=limit, limit_direction=limit_direction, inplace=True)
        if nan_fill_value is not None:
            # fill the nan values
            tmp.fillna(value=nan_fill_value, inplace=True)

        # setting the values (giving them back ot the original dataframe
        dataframe.loc[dataframe[id_column] == subject, features] = tmp

    # returning the original dataframe
    return dataframe
