#===============================================================================
# bbs_test.py
#===============================================================================

# Imports ======================================================================

from betabernsum.bbs import bbs_pmf, bbs_cdf




# Functions ====================================================================

def bbs_test(
    x,
    n,
    a,
    b,
    independent=True,
    alternative='two-sided',
    processes=1,
    max_iter=float('inf'),
    graceful=False
):
    """Perform a hypothesis test using a BBS distribution
    
    Parameters
    ----------
    x : int
        the number of successes
    n
        iterable giving the number of trials for each group
    a
        iterable giving the first shape parameter for each group
    b
        iterable giving the second shape parameter for each group
    alternative : str
        alternative hypothesis {'less', 'greater', 'two-sided'}
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
        the p-value of the hypothesis test
    """
    
    lower_tail_area = bbs_cdf(
        x, n, a, b, independent=independent, processes=processes,
        max_iter=max_iter, graceful=graceful
    )
    if lower_tail_area is None:
        return None
    if alternative == 'less':
        return lower_tail_area
    else:
        upper_tail_area = 1 - lower_tail_area + bbs_pmf(
            x, n, a, b, independent=independent
        )
    if alternative == 'two-sided':
        return min(1, 2 * min(lower_tail_area, upper_tail_area))
    elif alternative == 'greater':
        return upper_tail_area
