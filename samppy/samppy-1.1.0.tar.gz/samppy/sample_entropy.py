"""Estimate differential entropy of a multivariate distribution
from a set of i.i.d. samples drawn from the distribution.

For a known density function q(X) for random variable (vector) X,
the entropy is defined as
h(q) = E_q{ - ln q(X) } = - integral{ q(x) ln q(x) dx}

*** Estimation function: entropy_nn_approx

Arne Leijon, 2018-08-08, included in samppy package
2019-07-08, minor intro comment typo correction
"""

import numpy as np
from scipy.special import gammaln, psi


# -----------------------------------------------------------------------
def entropy_nn_approx(x, sample_axis=1):
    """Estimate differential entropy of a multivariate distribution,
    using i.i.d. random samples drawn from the distribution,
    calculating the entropy by a nearest-neighbor approximation.

    :param x: 2D (or 1D) array, or array-like list, of i.i.d. sample vectors,
        assumed drawn from some unknown density q(). 
        x[i, d] = d-th element of i-th vector sample of the distribution.
        x.shape == (N, D) OR (N,) in case of a scalar random variable
    :param sample_axis: (optional) axis for input sample vectors
        =1 for ROW vectors,
        =0 for COLUMN vectors (need transpose for calculation)
    :return: h = scalar estimate of entropy
    h.shape == ()
            
    References:
    F Perez-Cruz (NIPS 2008): Estimation of Information Theoretic Measures
    for Continuous Random Variables.
    
    S Singh and B Poczos (2016): Analysis of k-nearest neighbor distances 
    with application to entropy estimation
    arXiv:1603.08578 [math.ST]

    Method Principle (Perez-Cruz, 2008, Eq. 3):
    Using a sequence of samples [ x_1, ..., x_i, ..., x_N],
    where each x_i is a 1D array vector with D elements,
    the probability density is modelled by a k-th nearest-neighbor approximation as
    q(x_i) approx (k / N V_D) r(x_k)**D, where
    V_D = pi**(D/2) / Gamma(D/2 + 1) is the volume of a D-dimensional ball with radius 1,
    r_k is the observed Euclidean distance from x_i to the k-th nearest neighbor sample.

    The differential entropy is then estimated as
    h = - mean_i log( q(x_i) ) - C_k
    where C_k is a bias-correcting constant.

    This function uses a slightly more elaborate version by
    Singh et al (2016), using the Kozachenko-Leonenko estimator.

    We use only the nearest-neighbor variant (k=1), for simplicity, and because
    Perez-Cruz found that k=1 gives the best convergence to the true value.
    """
    def _distance_nearest_neighbor(x):
        """
        :param x: 2D array of ROW vectors
            x[i, :] = i-th sample vector
        :return: r = 1D array of Euclidean distances
            r[i] = scalar Euclidean distance from x[i] to its nearest neighbor.
        """
        def min_sq_dist(x_diff):
            """Min distance, excluding distance == 0 to itself"""
            d2 = np.sum(x_diff**2, axis=-1, keepdims=False)
            return np.min(d2[d2 > 0.], axis=-1, keepdims=False)
        # -----------------------------
        return np.sqrt([min_sq_dist(x_i - x) for x_i in x])
    # ----------------------------------------------------------------
    x = np.asarray(x)
    if x.ndim < 2:
        # we assume D=1
        x = x.reshape((-1, 1))
    if sample_axis == 0:
        x = x.T
    (N, D) = x.shape
    if N < 2:
        raise ValueError('Entropy estimation needs more than one sample')
    r = _distance_nearest_neighbor(x)
    D_half = D / 2.
    log_c_D = D_half * np.log(np.pi) - gammaln(D_half + 1)
    # = log unit ball volume

    # h_Perez =  np.log(N-1) - psi(1) + log_c_D + D * np.mean(np.log(r))
    # Perez-Cruz (2008)
    # Singh et al (2016) formulation of the Kozachenko-Leonenko estimator
    # is just slightly different from Perez-Cruz, for k == 1:
    h_Singh = psi(N) - psi(1) + log_c_D + D * np.mean(np.log(r))
    return h_Singh


# ----------------------------------------------------------------- TEST:
if __name__ == '__main__':
    from scipy.stats import norm
    # checking estimator bias and variance for small N

    D = 26
    N = 20
    scale = np.ones(D) * 3.
    x = norm.rvs(size=(N, D)) * scale
    h_exact = (D / 2) * np.log(2*np.pi) + np.sum(np.log(scale)) + D / 2
    print('Source entropy    h(p)= ', h_exact)

    h_nn = [entropy_nn_approx(norm.rvs(size=(N, D)) * scale)
            for _ in range(100) ]
    print('entropy_nn_approx h(p)= ', np.mean(h_nn))
    print('mean bias = ', np.mean(h_nn) - h_exact)
    print('std. dev  = ', np.std(h_nn))
    print('')

