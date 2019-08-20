#===============================================================================
# bbs.py
#===============================================================================

# Imports ======================================================================

from functools import partial
from multiprocessing import Pool
from betabernsum.region import region
from betabernsum.probability_mass import (
    probability_mass_independent, probability_mass_dependent
)




# Functions ====================================================================

def bbs_pmf(k, n, a, b, independent=True):
    """Probability mass function for a sum of beta-bernoulli variables

    Parameters
    ----------
    k
        number of successes
    n
        iterable giving the number of trials for each group
    a
        iterable giving the first shape parameter for each group
    b
        iterable giving the second shape parameter for each group
    independent : bool
        If TRUE (default), assume a sum of two independent groups of variables.
        If FALSE, assume all variables are mutually dependent.

    Returns
    -------
    float
        the value of the PMF
    """

    if k > sum(n) / 2:
        k, a, b = sum(n) - k, b, a

    if isinstance(n, int) or (isinstance(n, (tuple, list)) and len(n) == 1):
        reg = ((k,),)
    else:
        reg = region(k, n)
    return sum(
        probability_mass_independent(coord, n, a, b) if independent
        else probability_mass_dependent(coord, n, a, b)
        for coord in reg
    )

def bbs_cdf(
    k,
    n,
    a,
    b,
    independent=True,
    processes=1,
    max_iter=float('inf'),
    graceful=False
):
    """Cumulative distribution function for a sum of beta-bernoulli variables

    Parameters
    ----------
    k
        number of successes
    n
        iterable giving the number of trials for each group
    a
        iterable giving the first shape parameter for each group
    b
        iterable giving the second shape parameter for each group
    independent : bool
        If TRUE (default), assume a sum of two independent groups of variables.
        If FALSE, assume all variables are mutually dependent.
    processes : int
        number of processes to use
    max_iter : int
        maximum number of iterations
    graceful
        if True, return None when max_iter is exceeded, rather than raising an
        error

    Returns
    -------
    float
        the value of the CDF
    """

    if k == sum(n):
        return 1.0

    if k <= sum(n) / 2:
        speed_flip, r = False, range(k + 1)
    else:
        speed_flip, r, a, b = True, range(sum(n) - k), b, a

    if len(r) > max_iter:
        if graceful:
            return None
        else:
            raise RuntimeError('max iter exceeded')

    if processes == 1:
        return speed_flip + (1 - 2 * speed_flip) * sum(
            map(partial(bbs_pmf, n=n, a=a, b=b, independent=independent), r)
        )
    else:
        with Pool(processes=min(len(r), processes)) as pool:
            return speed_flip + (1 - 2 * speed_flip) * sum(
                pool.map(
                    partial(bbs_pmf, n=n, a=b, b=a, independent=independent), r
                )
            )
