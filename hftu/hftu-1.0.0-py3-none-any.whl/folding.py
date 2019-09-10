#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@summary: Code gathering the folding materials
@author: asr
"""

import numpy as np
import scipy.stats as ss
from .types import Matrix


def __target_function(X: Matrix, u: Matrix, u0: float) -> float:
    """
    Function to minimize: [ E(<X, u> + u0) ]^2 - [ E|<X, u> + u0| ]^2

    Parameters
    ----------
    X: numpy.ndarray
        data (n x d matrix)
    u: numpy.ndarray
        normal vector of the folding hyperplane (length d)
    u0: float
        intercept of the folding hyperplane
    """
    HX = X.dot(u) + u0
    return HX.mean()**2 - np.abs(HX).mean()**2


def folded_variance(X: Matrix, u: Matrix, u0: float) -> float:
    """
    Compute the folded variance Tr(Cov(Fold(X))) according to the
    given hyperplane.

    Parameters
    ----------
    X: numpy.ndarray
        data (n x d matrix)
    u: numpy.ndarray
        normal vector of the folding hyperplane (length d)
    u0: float
        intercept of the folding hyperplane
    """
    return np.trace(np.cov(X.T)) + __target_function(X, u, u0)


def folding_ratio(X: Matrix, u: Matrix, u0: float) -> float:
    """
    Compute the folding ratio which is the ratio
    Tr(Cov(Fold(X))) / Tr(Cov(X))

    Parameters
    ----------
    X: numpy.ndarray
        data (n x d matrix)
    u: numpy.ndarray
        normal vector of the folding hyperplane (length d)
    u0: float
        intercept of the folding hyperplane
    """
    return folded_variance(X, u, u0) / np.trace(np.cov(X.T))


def __ad(d: int) -> float:
    """
    Compute a specific coefficient needed to get the folded variance of the
    uniform distribution.

    Returns
    -------
    ad: float
        ad = (2/sqrt(pi)) * Gamma(d/2 + 1) / Gamma(d/2 + 1/2)
    """
    if d % 2 == 0:
        p = d // 2
        r = pow(4, p) / np.pi
        for i in range(p):
            r = r * (1 + i) / (p + i)
        return r
    p = (d - 1) // 2
    r = d / pow(4, p)
    for i in range(p):
        r = r * (p + 1 + i) / (1 + i)
    return r


def uniform_folded_variance(d: int, radius: float = 1) -> float:
    """
    Compute the folded variance of the uniform d-sphere with given radius

    Parameters
    ----------
    d: int
        dimension
    radius: float
        radius of the sphere (default is 1)
    """
    return radius**2 * ((d / (d + 2)) - (__ad(d) / (d + 1))**2)


def uniform_folding_ratio(d: int) -> float:
    """
    Compute the folding ration of the uniform d-sphere. It does
    not depend on the radius of the sphere.

    Parameters
    ----------
    d: int
        dimension
    """
    return 1 - (1 + 2 / d) * (__ad(d) / (d + 1))**2


def folding_statistics(X: Matrix, u: Matrix, u0: float) -> float:
    """
    Compute the folding statistic Φ of a given sample. It compares it folding ratio
    with those of the uniform distribution.

    Parameters
    ----------
    X: numpy.ndarray
        data (n x d matrix)
    u: numpy.ndarray
        normal vector of the folding hyperplane (length d)
    u0: float
        intercept of the folding hyperplane
    """
    return folding_ratio(X, u, u0) / uniform_folding_ratio(d=X.shape[1])


def decision_bound(n: int, d: int, alpha: float):
    """
    Compute the HFTU decision bound at given level alpha

    Parameters
    ----------
    n: int
        the number of observations
    d: int
        the dimension
    alpha: float
        the type I error (between 0 and 1)
    """
    a = 0.9
    sigma = a / (d * np.sqrt(n))
    mu = 1 - 2 * np.log(d) * sigma
    return ss.norm(loc=mu, scale=sigma).ppf(alpha)


def inverse_decision_bound(n: int, d: int, Phi: float):
    """
    Compute the HFTU decision bound at given level alpha

    Parameters
    ----------
    n: int
        the number of observations
    d: int
        the dimension
    Phi: float
        the folding statistics
    """
    a = 0.9
    sigma = a / (d * np.sqrt(n))
    mu = 1 - 2 * np.log(d) * sigma
    return ss.norm(loc=mu, scale=sigma).cdf(Phi)
