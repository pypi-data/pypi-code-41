#===============================================================================
# region.R
#===============================================================================

# Imports ======================================================================

import itertools
from accelasc import accel_asc




# Functions ====================================================================

def region(k, n):
    """Region of integration for bernoulli sums

    Parameters
    ----------
    k : int
        number of successes
    n
        iterable of integers, giving the number of trials for each group

    Yields
    -------
    tuple
        a set of coordinates in the region
    """

    if k < 0 or k > sum(n):
        raise RuntimeError('provided k is out of bounds')
    if k == 0:
        yield (0,) * len(n)
        return
    if k == sum(n):
        yield tuple(n)
        return
    yield from itertools.chain.from_iterable(
        set(
            permutation for permutation in itertools.permutations(
                partition + [0] * (len(n) - len(partition))
            )
            if all((p <= s for p, s in zip(permutation, n)))
        )
        for partition in accel_asc(k) if len(partition) <= len(n)
    )
