import numpy as np
from numba import jit, njit, int32, int64, prange
from numba.types import boolean

# @jit(forceobj=True, cache=True)
def label_to_index(label, labels_order):
    '''
    Returns first index of label in labels_order

    Arguments:
        label (str/int): a label to encode
        labels_order (list): a list of labels with each label appearing only
            once indicating which index to encode each label as.
    '''
    return np.where(labels_order == label)[0][0]

def labels_to_indices(labels, labels_order):
    '''
    Maps `label_to_index` to labels.

    Arguments:
        labels (list): a list of labels (str / int)
        labels_order (list): a list of labels with each label appearing only
            once indicating which index to encode each label as.
    '''
    f = lambda label: label_to_index(label, labels_order)
    return np.array(list(map(f, labels)))

# @jit(forceobj=True, cache=True)
def index_to_label(index, labels_order):
    '''
    Returns label at index

    Arguments:
        index (int): index of a label
        labels_order (list): a list of labels with each label appearing only
            once indicating which index to encode each label as.
    '''
    return labels_order[int(index)]

def indices_to_labels(indices, labels_order):
    '''
    Maps `label_to_index` to labels.

    Arguments:
        indices (list): a list of indices which correspoinds to labels
        labels_order (list): a list of labels with each label appearing only
            once indicating which index to encode each label as.
    '''
    f = lambda index : index_to_label(int(index), labels_order)
    return np.array(list(map(f, indices)))

# @jit(forceobj=True, cache=True)
def _ranges_np_to_py(ranges):
    '''
    Helper function to convert numpy arrays to python with mixed type.

    Arguments:
        np_ranges (np.array): a list of ranges, with shape (-1, 3) where each range
            (sublist / row) is a list of length 3 consisting of: `[label, start, stop]`

    Returns:
        ranges (list): a list of ranges where the second and third entry in each
            sublist are cast to integers.
    '''
    return [[type, int(float(start)), int(float(stop))] for type, start, stop in ranges]

# @jit(forceobj=True, cache=True)
def _ranges_np_to_nb(np_ranges, np_labels_order):
    '''
    Helper function to convert numpy arrays for numba requirements.

    Arguments:
        np_ranges (np.array): a list of ranges, with shape (-1, 3) where each range
            (sublist / row) is a list of length 3 consisting of: `[label, start, stop]`

        np_labels_order (np.array): a list of the types of ranges which might
            appear in np_ranges.
    Returns:
        np_ranges (np.array <int64>): the label column (`np_ranges[:, 0]`) now corresponds
            to values of the index from np_labels_order.
    '''
    if np_labels_order.size > 0:
        np_ranges[:, 0] = labels_to_indices(np_ranges[:, 0], np_labels_order)
    return np.array(np_ranges, dtype=np.int64)


# @jit(forceobj=True, cache=True)
def _ranges_nb_to_np(np_ranges, np_labels_order):
    '''
    Helper function to undo numba requirements to have non-string based numpy
    arrays.

    Arguments:
        np_ranges (np.array): a list of ranges, with shape (-1, 3) where each range
            (sublist / row) is a list of length 3 consisting of: `[label, start, stop]`

        np_labels_order (np.array): a list of the types of ranges which might
            appear in np_ranges.
    Returns:
        np_ranges (np.array): the label column (`np_ranges[:, 0]`) now corresponds
            to values from np_labels_order
    '''
    if np_labels_order.size > 0:
        np_labels = indices_to_labels(np_ranges[:, 0], np_labels_order).reshape((-1, 1))
        np_ranges = np.append(np_labels, np_ranges[:, 1:], axis=1)
    return np_ranges
