import random, numpy as np
from numba import jit, njit, int32, int64, prange, types
from numba.types import boolean
from numba.typed import Dict

from .conversions import (
    _ranges_np_to_nb, _ranges_nb_to_np, label_to_index
)

# @njit(cache=True)
def _pad(start, stop, length, position=None, min=0, max=np.inf):
    '''
    Ensures the specified range is of specified length.

    Arguments:
        start (int): the start of the range
        stop (int):  the stop of the range
        length (int): the desired length of the range
        position (None / int): pads using position as the start position for the
            padding. Defaults to `None`. If `None`, the padding will be applied
            randomly.
        min (int): the minimum value the range (start) could take. Defualts to 0.
        max (int): the minimum value the range (stop) could take. Defualts to `inf`.

    Returns:
        padded_start (int): the new start of the range
        padded_stop (int): the new stop of the range
    '''
    needed = length - (stop - start)

    if position is not None:
        pad_start = position
    else:
        pad_start = random.randint(0, abs(needed))


    if needed < 0:
        pad_start *= -1

    if start - pad_start <= min:
        pad_start = min

    pad_stop = needed - pad_start
    if stop + pad_stop >= max:
        pad_stop = max - pad_stop
        pad_start = needed - pad_stop

    new_start  = start - pad_start
    new_stop   = stop  + pad_stop

    return [int(new_start), int(new_stop)]

# @jit(forceobj=True, cache=True)
def pad(_range, length, position=None, min=0, max=np.inf):
    '''
    Arguments:
        _range (list): a range consisting of `[label, start, stop]`
        length (int): the desired length of the range
        position (None / int): pads using position as the start position for the
            padding. Defaults to `None`. If `None`, the padding will be applied
            randomly.
        min (int): the minimum value the range (start) could take. Defualts to 0.
        max (int): the minimum value the range (stop) could take. Defualts to `inf`.

    Returns:
        padded_start (int): the new start of the range
        padded_stop (int): the new stop of the range
    '''
    label, start, stop = _range
    pstart, pstop =_pad(int(start), int(stop), length, position, min, max)
    return [label, pstart, pstop]


# @njit(cache=True)
def _pad_ranges(ranges, length, position=None, max_lookup=None):
    '''
    Notes:
        Currated for my use case.
        `min` for every range will always be `0`

    Arguments:
        ranges (np.array): a list of ranges, with shape (-1, 3) where each range
            (sublist / row) is a list of length 3 consisting of: `[label, start, stop]`
        length (int): the desired length of the range
        position (None / int): pads using position as the start position for the
            padding. Defaults to `None`. If `None`, the padding will be applied
            randomly.
        max_lookup (None / Dict): A dictionary corresponding of label / `max`
            pairs. If None, max will always be `inf`

    Returns:
        padded_ranges (np.array): the padded ranges
    '''
    results = np.array([0][:0]).reshape(-1, 3)
    for i in prange(len(ranges)):
        if max_lookup is None:
            _max = np.inf
        else:
            _max = max_lookup[ranges[i][0]]
        label, start, stop = ranges[i]
        pstart, pstop =_pad(int(start), int(stop), length, position, 0, _max)
        results = np.concatenate((results, np.array([[label, pstart, pstop]])))
    return results


# @jit(forceobj=True)
def pad_ranges(ranges, labels_order, length, position=None, max_lookup=None):
    '''
    Notes:
        Currated for my use case.
        `min` for every range will always be `0`

    Arguments:
        ranges (np.array): a list of ranges, with shape (-1, 3) where each range
            (sublist / row) is a list of length 3 consisting of: `[label, start, stop]`
        labels_order (list): if the labels of ranges are as strings, then
            labels_order corresponds to a list, containing each label to be used
            as a lookup table for converting them to indicies.
        length (int): the desired length of the range
        position (None / int): pads using position as the start position for the
            padding. Defaults to `None`. If `None`, the padding will be applied
            randomly.
        max_lookup (None / Dict): A dictionary corresponding of label / `max`
            pairs. If None, max will always be `inf`.

    Returns:
        padded_ranges (np.array): the padded ranges
    '''
    # ensure np as input
    np_result = np.array(ranges)
    np_labels = np.array(labels_order)
    np_ranges = np_result[:, :3]
    # convert string labels to integers
    np_ranges = _ranges_np_to_nb(np_ranges, np_labels)

    if max_lookup is not None:
        lookup = Dict.empty(
            # key_type=types.unicode_type,
            key_type=types.int64,
            value_type=types.int64
        )
        for k, v in max_lookup.items():
            lookup[label_to_index(k, np_labels)] = int(v)
    else:
        lookup = None

    np_ranges = _pad_ranges(np_ranges, length, position, lookup)
    np_result[:, :3] = _ranges_nb_to_np(np_ranges, np_labels)
    return np_result.tolist()
