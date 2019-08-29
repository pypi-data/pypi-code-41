__title__ = 'Project DataFlame'
__author__ = 'Shayan Fazeli'
__email__ = 'shayan@cs.ucla.edu'
__credit__ = 'erLab - University of California, Los Angeles'
"""
    DataFlame: Dataframe Utilities
    ==========
    This file includes the utilities that I have designed for dealing with dataframes, from linear and time-wise interpolations to 
    a variety of data balancing techniques to be used in our systems (e.g. pyTorch data reading schemes). For a project which
    requires working with dataframes for the most part, being able to efficiently deal with them is of paramount importance.
    Remark: This module includes the methods that we use to reformat the labels. For example taking in a sequence tags and output an array (binary vector).
"""

from typing import List, Any, Dict
import numpy


def get_vector_given_sequence(
        tag_sequence: List[Any],
        layout: List[Any]
) -> numpy.ndarray:
    """
    This method is mainly useful for when we are to represent a sequence as a vector.

    Parameters
    ----------
    tag_sequence: ``List[Any]``, required
    The sequence that we intend to turn into a numerical vector.

    layout: ``List[Any]``, required
    This is the mapping and the table we are going to match the elements of the sequence against
    and output the vector.

    Returns
    ----------
    The output of this method is an ``numpy.ndarray`` which is our mathematical vector.

    ``Example:
    Sequence to vector: assume we have a sequence of tags coming from 100 element space
    the output would be a 100 element binary vector
    ``
    """

    output = numpy.zeros((len(layout))).astype('float')

    for tag in tag_sequence:
        output[layout.index(tag)] = 1.0

    return output
