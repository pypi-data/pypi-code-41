from scipy.stats import binom
import numpy as np


def prob_of_twins(x):
    """ Return the probability of at least this many repeat pairs (adjacent
        digits being equal) in the given sequence of digits.
        In a sequence of 1, 1, 1, 2, 3, 3, 4 there will be 3 pairs considered.

        x: list-like of digits
    """
    if len(x) <= 1:
        # nothing to see here, not enough information
        return 1
    x = np.array(x)
    count = sum(x[:-1] == x[1:])
    return 1 - binom(len(x) - 1, 0.1).cdf(count - 1)
