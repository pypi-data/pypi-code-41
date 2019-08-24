"""This module calculates jointly credible differences
between elements of random vectors, represented by
sample vectors drawn from a multivariate distribution.

Method reference:
A. Leijon, G. E. Henter, and M. Dahlquist.
Bayesian analysis of phoneme confusion matrices.
IEEE Transactions on Audio, Speech, and Language Processing 24(3):469–482, 2016.
"""
import numpy as np
from itertools import combinations, product


# ----------------------------------------------------------
def cred_diff(x, diff_axis=0, case_axis=1, sample_axis=2,
              p_lim=0.6, threshold=0.):
    """Find a sequence of pairs of jointly credible differences between
    random-vector elements in one or more case conditions.
    Distributions are represented by an array of RELATED SAMPLES.

    :param x: 2D or 3D array, or array-like list, of samples from random vector X, stored as
        (default) x[element, case, sample]
        NOTE: Samples are assumed JOINTLY sampled for all vector elements in all case variants.
    :param diff_axis: (optional) axis along which credible differences are to be found
    :param case_axis: (optional) secondary axis with cases within which differences are considered
    :param sample_axis: (optional) axis with samples from desired distribution
    :param p_lim: (optional) scalar minimum joint credibility for difference to be included
    :param threshold: scalar minimum difference between elements to be considered.
    :return: list of tuples ((i, j), p) if 2D data, OR ((i, j, c), p), if 3D data,
        meaning that
        prob{ X_i - X_j > threshold in case=c } AND similar for all preceding tuples } = p,
        where (i, j) are indices along diff_axis of x, c (if any) is index along case_axis of x.
        The probability is estimated from the relative frequency of samples
        stored along sample_axis of x.

    As each successive tuple includes one new pair in the jointly credible set,
    the joint probability for the sequence of pairs decreases with each new pair.
    Therefore, the result list is automatically ordered
    with strictly non-increasing values of p.

    Arne Leijon, 2017-12-25
    """
    # -------------------------------------------------
    def check_reverse():
        """reverse any pairs where opposite comparison is more frequent
        Result:
        reversed arrays diff and corresponding index pairs in ijc_tuples
        """
        i_rev = (np.sum(diff < -threshold, axis=1, keepdims=False) >
                 np.sum(diff > threshold, axis=1, keepdims=False))
        ijc_tuples[i_rev, :2] = ijc_tuples[i_rev, 1::-1]
        diff[i_rev, :] = - diff[i_rev, :]

    # -------------------------------------------------
    x = np.asarray(x)
    if x.ndim == 2:
        case_axis = None
        x = x.transpose((diff_axis, sample_axis))
        (n_x, n_samples) = x.shape
    elif x.ndim == 3:
        x = x.transpose((diff_axis, case_axis, sample_axis))
        (n_x, n_cases, n_samples) = x.shape
    else:
        raise RuntimeError('Input sample array must be 2D or 3D')

    ij_pairs = [pair for pair in combinations(np.arange(n_x), 2)]
    # = list of pairs (i,j)
    diff = np.array([xi - xj
                     for (xi, xj) in combinations(x, 2)
                     ])
    # saved as diff[pair, case, sample] or diff[ij_pair, sample] if 2D
    if case_axis is None:
        ijc_tuples = np.array(ij_pairs)
        # ijc_tuples.shape == (diff.shape[0], 2)
    else:
        diff = diff.reshape((-1, n_samples))
        ijc_tuples = np.array([(i, j, c) for ((i,j),c) in product(ij_pairs, range(n_cases))])
        # ijc_tuples.shape == (diff.shape[0], 3)
    check_reverse()

    res = []
    # space for result

    # Main loop:
    n_pos_diff = np.sum(diff > threshold, axis=1, keepdims=False)
    while np.any(n_pos_diff > p_lim * n_samples):
        i_max = np.argmax(n_pos_diff)
        res.append((tuple(ijc_tuples[i_max]),
                    (n_pos_diff[i_max] + 0.5) / (n_samples + 1)
                    ))
        # = ((i, j), p) OR ((i,j,c), p), where p is estimated using 0.5 pseudocount
        diff = diff[:, diff[i_max, :] > threshold]
        # keeping only samples where accepted condition is satisfied
        diff = np.delete(diff, i_max, axis=0)
        # keeping only pairs not yet included in res
        ijc_tuples = np.delete(ijc_tuples, i_max, axis=0)
        check_reverse()
        n_pos_diff = np.sum(diff > threshold, axis=1, keepdims=False)
    return res


# ---------------------------------------------------------------
def cred_group_diff(x_groups, case_axis=0, sample_axis=1,
                    p_lim=0.6, threshold=0.):
    """Find pairs of jointly credible differences between
    groups with independent scalar or vector-valued random variables,
    represented by UNRELATED sets of samples for each group.

    :param x_groups: list of 1D or 2D arrays, or array-like lists,
        with samples from random vectors X_group, stored as
        (default) x_groups[group][case, sample]
        Samples are treated as independent across groups,
        but assumed jointly sampled within each group.
        Thus, the order of samples is not related across groups,
        but samples are assumed jointly related within each group.
    :param diff_axis: (optional) axis along which credible differences are to be found
    :param case_axis: (optional) secondary axis with cases within which differences are considered
    :param sample_axis: (optional) axis with samples from desired distribution
    :param p_lim: (optional) scalar minimum joint credibility for difference to be included
    :param threshold: scalar minimum difference between elements to be considered.

    :return: list of tuples ((i, j), p) if scalar data,
        OR ((i, j, c), p), if 2D data with separate case variants,
        meaning that
        prob{ X_i - X_j > threshold in case=c } AND similar for all preceding tuples } = p,
        where (i, j) are indices of x_groups, c (if any) is index along case_axis.
        The probability is estimated from the relative frequency of samoles
        stored along sample_axis of x_groups.

    As each successive tuple includes one new pair in the credible set,
    the joint probability for the sequence of pairs decreases with each new pair.
    Therefore, the result list is automatically ordered
    with non-increasing values of p.

    Method: Data for each x_group are re-sampled for equal number of samples,
    then handled as usual by cred_diff function.

    Arne Leijon, 2017-12-25
    """
    n_groups = len(x_groups)
    if case_axis is not None:
        x_groups = [x.transpose((sample_axis, case_axis)) for x in x_groups]
        case_axis = 2
    # always stored as x_groups[g][sample, case]
    max_n_samples = max((x.shape[0] for x in x_groups))
    # re-sample to equal size
    x_groups = [x[np.random.randint(0, len(x), size=max_n_samples)]
               if len(x) < max_n_samples else x
               for x in x_groups]
    return cred_diff(x_groups, diff_axis=0,
                     sample_axis=1,
                     case_axis=case_axis,
                     p_lim=p_lim, threshold=threshold)


# -------------------------------------------------------------------
def cred_corr(x, corr_axis=0, sample_axis=1, vector_axis=2, p_lim=0.6):
    """Find set of jointly credible correlations
    between random vectors or scalars,
    represented by sampled joint distributions.
    Distributions are represented by an array of RELATED SAMPLES.

    :param x: 2D or 3D array, or array-like list, with samples from random vector X, stored as
        (default) x[element, case, sample]
        NOTE: Samples are assumed JOINTLY sampled for all vector elements in all case variants.
    :param diff_axis: (optional) axis along which credible differences are to be found
    :param case_axis: (optional) secondary axis with cases within which differences are considered
    :param sample_axis: (optional) axis with samples from desired distribution
    :param p_lim: (optional) scalar minimum joint credibility for difference to be included

    :return: list of tuple((i, j), p, median_corr), where
        (i, j) is the pair of indices along corr_axis for the credibly correlated random variables
        p = the JOINT credibility of this and all previous tuples in the list,
        median_c = the median conditional correlation coefficient, given that
            all previous correlations in the list are credibly non-zero.

    The correlation (cosine) values are calculated WITHOUT subtraction of the mean,
    i.e., vectors are treated as non-normalized directions.
    For random scalars, each correlation sample is the product, normalized by sample std.deviation.
    For random vectors, each correlation sample is the cosine angle between the pair of vector samples,
        normalized by mean square norm across all samples,
        with vector elements stored along vector_axis of x.

    Arne Leijon, 2017-12-26
    """
    x = np.asarray(x)
    if x.ndim == 2:
        vector_axis = None
        x = x.reshape((corr_axis, sample_axis))
        corr = np.array([x_i * x_j
                         / np.sqrt(np.mean(x_i**2) * np.mean(x_j**2))
                         for (x_i, x_j) in combinations(x, 2)])
    elif x.ndim == 3:
        x = x.transpose((corr_axis, sample_axis, vector_axis))
        corr = np.array([np.sum(x_i * x_j, axis=1)
                         / np.sqrt(np.mean(np.sum(x_i**2, axis=1)) *
                                   np.mean(np.sum(x_j**2, axis=1)))
                         for (x_i, x_j) in combinations(x, 2)])
    else:
        raise RuntimeError('Input array must be 2D or 3D')
    ij_pairs = [p for p in combinations(range(x.shape[0]), 2)]
    return credibly_nonzero(corr, ij_pairs, p_lim=p_lim)


# -------------------------------------------------------------------
def credibly_nonzero(x, id_x,
                     diff_axis=0, sample_axis=1,
                     p_lim=0.6):
    """Find set of elements of a random-vector X that are credibly non-zero,
    useful, e.g., when X is a random array of correlation-like values.
    :param x: 2D array, or array-like list,
        with sampled values from a random vector, stored as
        (default) x[element, sample]
    :param id_x: list of objects identifying the external meaning of elements of x.
        Elements may be string labels, index integers or whatever.
        len(id_x) == x.shape[diff_axis]
    :param diff_axis: axis along which credibly non-zero elements are to be found
    :param sample_axis: axis with samples from the distribution
    :param p_lim: (optional) scalar minimum joint credibility for difference to be included

    :return: list of tuples(id, p, median_x), where
        id is an identifying element from input id_x, and
        p is the JOINT credibility of non-zero values,
        meaning that
        max( prob{ X_id > 0), prob(X_id < 0) ) AND similar for all previous tuples } = p
        median_x is the conditional median(X_id), given that X is non-zero in all previous tuples.

        The probability is estimated from the relative frequency of samples
        which are systematically deviating from zero on either side,
        using the side that has the greatest relative frequency,
        including only the remaining samples for which all previous results were satisfied.
        Thus, if 80% of samples are positive, p = 0.8.
        Similarly, if 80% of samples are negative, p = 0.8.
        If the median of samples is zero, p = 0.5, indicating no systematic deviation.

        The mean_x is similarly estimated as the sample average across remaining samples.
        Thus, this value indicates both the sign and magnitude of the deviation from zero.

    As each successive result tuple includes one new element in the credible set,
    the joint probability decreases with each new element in the sequence.
    Therefore, the result list is automatically ordered
    with non-increasing values of p.
    The absolute value of median_x will also decrease toward zero.

    Arne Leijon, 2017-12-26
    """
    def check_reverse():
        """Flip positive_x samples, if negative are more common than positive
        """
        i_flip = np.sum(positive_x, axis=1) < positive_x.shape[1] / 2.
        positive_x[i_flip] = np.logical_not(positive_x[i_flip])
    # -------------------------------------------------------------------

    x = np.array(x)
    id_x = id_x.copy()
    # must use copies, because x and id_x are destroyed during calculations
    assert x.ndim == 2, 'Input must be 2-dim array'
    x = x.transpose((diff_axis, sample_axis))
    (n_x, n_samples) = x.shape
    assert len(id_x) == n_x ,'Input id_x size mismatch'
    positive_x = x > 0.
    check_reverse()

    res = []
    # space for result

    # main loop:
    sum_positive = np.sum(positive_x, axis=1)
    while np.any(sum_positive > p_lim * n_samples):
        i_max = np.argmax(sum_positive)
        res.append(tuple((id_x[i_max],
                         (sum_positive[i_max] + 0.5) / (n_samples + 1),
                         np.median(x[i_max])))
                   )
        x = x[:, positive_x[i_max]]
        positive_x = positive_x[:, positive_x[i_max]]
        # keeping only samples where earlier accepted conditions are satisfied
        positive_x = np.delete(positive_x, i_max, axis=0)
        x = np.delete(x, i_max, axis=0)
        # id_x = np.delete(id_x, i_max)
        del id_x[i_max]
        # keeping only elements not already included in res
        check_reverse()
        sum_positive = np.sum(positive_x, axis=1)
    return res


# ----------------------------------------------------------- TEST:
if __name__ == '__main__':
    from scipy.stats import norm

    print('*** Testing cred_diff, cred_group_diff, cred_corr')
    n_samples = 1000
    mu = [[0., 0.5, 1.],
          [0., -1., 0.5],
          [0., -1., -2.]]
    n_mu = 3
    len_x = 3
    x = [norm.rvs(loc=m, size=(n_samples, len_x))
         for m in mu]
    print('mean x', np.mean(x, axis=1))

    print('\nTest cred_diff:')
    d = cred_diff(x, diff_axis=2, sample_axis=1, case_axis=0)
    print('cred_diff = ', d)
    true_prob_diff = [norm.cdf(mu[c][i] - mu[c][j], scale=np.sqrt(2))
                      for ((i,j,c),_) in d]
    # print('true marg. prob. ', true_prob_diff)
    print('true joint prob. ', np.cumprod(true_prob_diff))
    print("""NOTE: the 3rd cred_diff result shows slightly over-estimated credibility
    probably because the largest value is selected in each step,
    and the test data includes three different cases with equal true differences
    """)

    print('\nTest cred_group_diff:')
    n_group_samples = [100, 500, 1000]
    x_groups = [norm.rvs(loc=m, size=(ns, len_x))
         for (m, ns) in zip(mu, n_group_samples)]

    d = cred_group_diff(x_groups, sample_axis=0, case_axis=1)
    print('cred_group_diff ', d)

    true_prob_diff = [norm.cdf(mu[i][c] - mu[j][c], scale=np.sqrt(2))
                      for ((i,j,c),_) in d]
    # print('true marg. prob. ', true_prob_diff)
    print('true joint prob. ', np.cumprod(true_prob_diff))

    print('\nTest cred_corr:')
    d = cred_corr(x, corr_axis=0, sample_axis=1, vector_axis=2)
    print('cred_corr ', d)
    cosine = np.array([np.sum(x_i * x_j)
                       / np.sqrt(np.sum(x_i ** 2) *
                                 np.sum(x_j ** 2))
                       for (x_i, x_j) in combinations(np.asarray(mu), 2)])
    ij_pairs = [p for p in combinations(range(n_mu), 2)]
    print('mu cosine = ', [ (ij, c) for (ij, c) in zip(ij_pairs, cosine)])