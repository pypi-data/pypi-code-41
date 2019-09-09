import random, numpy as np
from numba import jit, njit, int32, int64, prange

from .conversions import (
    _ranges_np_to_nb, _ranges_nb_to_np, _ranges_np_to_py
)

@njit(cache=True)
def merge_q(label_a, start_a, stop_a, label_b, start_b, stop_b):
    '''
    Whether or not range `A` and range `B` can be merged.

    Arguments:
        label_a (int): label of range `A`
        start_a (int): start of range `A`
        stop_a (int): stop of range `A`
        label_b(int): label of range `B`
        start_b(int): start of range `B`
        stop_b (int): stop of range `B`

    Returns:
        answer (bool)
    '''
    if label_a != label_b: # not of same type
        return False
    elif stop_a < start_b: # a does not start and then overlap b
        return False
    elif stop_b < start_a: # b does not start and then overlap a
        return False
    else: # same type and overlap, merge into i, do not append
        return True


@njit(cache=True)
def _merge_ranges(ranges):
    '''
    Simplifies the input ranges by merging overlaps ranges.

    Arguments:
        ranges (np.array): a list of ranges, with shape (-1, 3) where each range
            (sublist / row) is a list of length 3 consisting of: `[label, start, stop]`

    Returns:
        ranges (list): a simplified version of the input
    '''
    coalesced = np.array([0][:0]).reshape(-1, 3)
    for i in range(len(ranges)):
        label_a, start_a, stop_a = ranges[i]
        append_flag = True
        for j in range(len(coalesced)):
            label_b, start_b, stop_b = coalesced[j]
            if merge_q(label_a, start_a, stop_a, label_b, start_b, stop_b):
                append_flag = False
                coalesced[j] = [label_a, min(start_a, start_b), max(stop_a, stop_b)]
                break
        if append_flag:
            coalesced = np.concatenate((coalesced, np.array([[label_a, start_a, stop_a]])))
        # coalesced = np.sort(coalesced)
    return coalesced

@njit(cache=True)
def _coalesce(ranges):
    '''
    A helper wrapper over the function `_merge_ranges` which continues to reduce
    ranges until reduction no longer occurs.

    Arguments:
        ranges (np.array): a list of ranges, with shape (-1, 3) where each range
            (sublist / row) is a list of length 3 consisting of: `[label, start, stop]`

    Returns:
        ranges (list): a simplified version of the input
    '''
    _len = np.inf
    coalesced = ranges
    while _len > len(coalesced):
        coalesced = _merge_ranges(coalesced)
        _len = len(coalesced)
    return coalesced


@jit(forceobj=True, cache=True)
def coalesce(ranges, labels_order=[]):
    '''
    A python wrapper for taking LabeledRanges (as list) and sending it to numba
    to simplify.

    Arguments:
        ranges (list): a list of ranges, where each range is a list of length
            3 consisting of:  `[label, start, stop]`

        labels_order (list): if the labels of ranges are as strings, then
            labels_order corresponds to a list, containing each label to be used
            as a lookup table for converting them to indicies.

    Returns:
        ranges (list): a simplified version of the input
    '''
    # ensure np as input
    np_labels = np.array(labels_order)
    np_ranges = np.array(ranges)
    # convert string labels to integers
    np_ranges = np.sort(_ranges_np_to_nb(np_ranges, np_labels))
    np_ranges = _coalesce(np_ranges)
    # invert labels to strings
    np_result = _ranges_nb_to_np(np_ranges, np_labels)
    return _ranges_np_to_py(np_result)
