from scipy.stats import poisson
import numpy as np


def prob_of_twins(x):
    """ Return the probability of at least this many repeats
        in the sequence of digits

        x: list-like of digits
    """
    if len(x) <= 1:
        # nothing to see here, not enough information
        return 1
    x = np.array(x)
    count = sum(x[:-1] == x[1:])
    return 1 - poisson((len(x) - 1) / 10).cdf(count - 1)
