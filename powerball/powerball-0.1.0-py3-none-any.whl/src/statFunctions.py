import numpy
import statsmodels.stats.multitest as stm

from .diversity import shannon_diversity_indv


def p_values(null, shDiv, twoTailedFlag, alpha):
    # Returns an fdr corrected p-value that is one or two tailed.
    # Null is a 2d array of null values for a group
    # generated through monte carlo simulation,
    # shDiv is a list of empirical shannon diversity values for a group,
    # TwoTailedFlag specifies whether it should be one or two-tailed,
    # Alpha is the threshold value we compare the p-values against.
    if twoTailedFlag:
        return stm.multipletests(two_tailed_comparison(null, shDiv), alpha,
                                 'hs')[1]
    return stm.multipletests(one_tailed_lower(null, shDiv), alpha,
                             'hs')[1]


def two_tailed_comparison(null, shDiv):  # Two-tailed p-value
    # Takes a 2d array of null values and a list of the empirical shannon
    # diversities for a group. Returns the upper or lower one tailed p-value
    # based on which is more significant.
    u = numpy.median(shDiv)
    mid = numpy.median(null)
    if u > mid:
        p = one_tailed_upper(null, shDiv)
    else:
        p = one_tailed_lower(null, shDiv)

    return p


def one_tailed_lower(null, shDiv):  # One-tailed lower p-value
    # Takes a 2d array of null values and a list of the empirical shannon
    # diversities for a group. Returns the p-value given by the proportion
    # of values greater than u in null.
    u = numpy.median(shDiv)
    n_below = numpy.sum(numpy.greater(u, null))
    if n_below <= 0:
        return 1/null.size
    else:
        return n_below / null.size


def one_tailed_upper(null, shDiv):  # One-tailed upper p-value
    # Takes a 2d array of null values and a list of the empirical shannon
    # diversities for a group. Returns the p-value given by the proportion
    # of values less than u in null.
    u = numpy.median(shDiv)
    n_below = numpy.sum(numpy.less(u, null))
    if n_below <= 0:
        return 1/null.size
    else:
        return n_below / null.size


def standard_effect(null, shDiv):  # Competitiveness score
    # Takes a 2d array of null values and a list of the empirical shannon
    # diversities for a group.
    # Returns the standard effect size for a group based off the formula below:
    # https://en.wikipedia.org/wiki/Effect_size#Difference_family:_Effect_sizes_based_on_differences_between_means
    return ((numpy.mean(shDiv) - numpy.mean(null))/numpy.std(null))
