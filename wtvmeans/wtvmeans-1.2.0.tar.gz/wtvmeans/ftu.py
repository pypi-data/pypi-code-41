# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 17:32:44 2018

@author: asr
"""

import numpy as np
from math import exp, sqrt, log
from scipy.optimize import brenth, minimize

PVAL_A = 0.4785
PVAL_B = 0.1946
PVAL_C = 2.0287


def decision_bound(p_value, n, d):
    """
    Compute the decision bound q according to the desired p-value. The test would
    be significant if |phi-1|>q.

    Parameters
    ----------

    p_value: float
        between 0 and 1 (this is the probability to be in the uniform case)
    n: int
        the number of observations
    d: int
        the dimension
    """
    return PVAL_A * (p_value - PVAL_B * log(1 - p_value)) * \
        (PVAL_C + log(d)) / sqrt(n)


def p_value(phi, n, d, e=1e-16):
    """
    Compute the p-value of a test

    Parameters
    ----------

    phi: float
        the folding statistics
    n: int
        the number of observations
    d: int
        the dimension
    """
    try:
        def obj_fun(p): return (abs(phi - 1.) - decision_bound(1 - p, n, d))
        p_val = brenth(obj_fun, 0., 1.)
    except BaseException:
        p_val = exp(-abs(phi - 1.) * sqrt(n) / (PVAL_C + log(d)))
    return p_val


def batch_folding_test(X):
    """
    Perform statically the folding test of unimodality (pure python)

    Parameters
    ----------

    X: numpy.ndarray
        a d by n matrix (n observations in dimension d)
    """
    try:
        n, p = X.shape
    except BaseException:
        X = X.reshape(1, len(X))
        n, p = X.shape

    if n > p:  # if lines are observations, we transpose it
        X = X.T
        dim = p
        n_obs = n
    else:
        dim = n
        n_obs = p

    X_square_norm = (X * X).sum(axis=0)  # |X|²
    mat_cov = np.cov(X).reshape(dim, dim)  # cov(X)
    trace = np.trace(mat_cov)  # Tr(cov(X))

    # cov_norm = np.cov(X, X_square_norm)[:-1, -1].reshape(-1, 1)  # cov(X,|X|²)
    # # 0.5 * cov(X)^{-1} * cov(X,|X|²)
    # pivot = 0.5 * np.linalg.solve(mat_cov, cov_norm)
    try:
        cov_norm = np.cov(X, X_square_norm)[
            :-1, -1].reshape(-1, 1)  # cov(X,|X|²)
        # 0.5 * cov(X)^{-1} * cov(X,|X|²)
        pivot = 0.5 * np.linalg.solve(mat_cov, cov_norm)
    except np.linalg.linalg.LinAlgError:
        # print(X.shape)
        # print("Attempting numerical optimization")
        pivot = minimize(lambda s: np.power(
            X.T - s, 2).sum(axis=1).var(), x0=X.mean(axis=1)).x.reshape(-1, 1)
        # print(pivot.shape)
#    X_reduced = np.sqrt(np.power(X - pivot, 2).sum(axis=0))  # |X-s*|
    X_reduced = np.linalg.norm(X - pivot, axis=0)  # |X-s*|
    phi = pow(1. + dim, 2) * X_reduced.var(ddof=1) / trace
    unimodal = (phi >= 1.)
    return unimodal, p_value(phi, n_obs, dim), phi


def diagonal(X):
    """
    Returns the diagonal of the smallest hypercube including the dataset X

    Parameters
    ----------

    X: numpy.ndarray
        a d by n matrix (n observations in dimension d)
    """
    return np.linalg.norm(X.max(1) - X.min(1))


def markov_coeff(X, X_reduced):
    """
    Computes the Markov coefficient

    Parameters
    ----------

    X: numpy.ndarray
        a d by n matrix (n observations in dimension d)
    X_reduced: numpy.ndarray
        the 1 by n matrix equals to ||X-s*(X)||
    """
    return (X_reduced / diagonal(X)).mean()


def markov_bound(d):
    """
    Returns the bound on the Markov coefficient

    Parameters
    ----------

    d: int
        dimension of the feature space
    """
    return sqrt(d) / (2. * (d + 1.))


def batch_folding_test_with_MPA(X):
    """
    Perform statically the folding test of unimodality (pure python) with a
    Markov Ex Post Analysis

    Parameters
    ----------

    X: numpy.ndarray
        a d by n matrix (n observations in dimension d)
    """
    try:
        n, p = X.shape
    except BaseException:
        X = X.reshape(1, len(X))
        n, p = X.shape

    if n > p:  # if lines are observations, we transpose it
        X = X.T
        dim = p
        n_obs = n
    else:
        dim = n
        n_obs = p

    X_square_norm = (X * X).sum(axis=0)  # |X|²
    mat_cov = np.cov(X).reshape(dim, dim)  # cov(X)
    trace = np.trace(mat_cov)  # Tr(cov(X))

    try:
        cov_norm = np.cov(X, X_square_norm)[
            :-1, -1].reshape(-1, 1)  # cov(X,|X|²)
        pivot = 0.5 * np.linalg.solve(mat_cov, cov_norm)
    except np.linalg.linalg.LinAlgError:
        pivot = minimize(lambda s: np.power(
            X.T - s, 2).sum(axis=1).var(), x0=X.mean(axis=1)).x.reshape(-1, 1)

    X_reduced = np.linalg.norm(X - pivot, axis=0)  # |X-s*|
    phi = pow(1. + dim, 2) * X_reduced.var(ddof=1) / trace
    unimodal = (phi >= 1.)
    if unimodal:
        mc = markov_coeff(X, X_reduced)
        if mc > markov_bound(dim):
            unimodal = False
    else:
        mc = None
    return unimodal, p_value(phi, n_obs, dim), phi, mc


# def batch_folding_test_robust(X, depth=3):
#     """
#     Perform statically the folding test of unimodality (pure python)

#     Parameters
#     ----------

#     X: numpy.ndarray
#         a d by n matrix (n observations in dimension d)
#     depth: int
#         number of iterations to confirm the unimodality character
#     """
#     if not (isinstance(depth, int) and depth>=1):
#         raise ValueError("The depth must be an integer >= 1")

#     try:
#         n, p = X.shape
#     except BaseException:
#         X = X.reshape(1, len(X))
#         n, p = X.shape

#     if n > p:  # if lines are observations, we transpose it
#         X = X.T
#         dim = p
#         n_obs = n
#     else:
#         dim = n
#         n_obs = p

#     X_square_norm = (X * X).sum(axis=0)  # |X|²
#     mat_cov = np.cov(X).reshape(dim, dim)  # cov(X)
#     trace = np.trace(mat_cov)  # Tr(cov(X))

#     # cov_norm = np.cov(X, X_square_norm)[:-1, -1].reshape(-1, 1)  # cov(X,|X|²)
#     # # 0.5 * cov(X)^{-1} * cov(X,|X|²)
#     # pivot = 0.5 * np.linalg.solve(mat_cov, cov_norm)
#     try:
#         cov_norm = np.cov(X, X_square_norm)[
#             :-1, -1].reshape(-1, 1)  # cov(X,|X|²)
#         # 0.5 * cov(X)^{-1} * cov(X,|X|²)
#         pivot = 0.5 * np.linalg.solve(mat_cov, cov_norm)
#     except np.linalg.linalg.LinAlgError:
#         # print(X.shape)
#         # print("Attempting numerical optimization")
#         pivot = minimize(lambda s: np.power(
#             X.T - s, 2).sum(axis=1).var(), x0=X.mean(axis=1)).x.reshape(-1, 1)
#         # print(pivot.shape)
# #    X_reduced = np.sqrt(np.power(X - pivot, 2).sum(axis=0))  # |X-s*|
#     X_reduced = np.linalg.norm(X-pivot, axis=0)  # |X-s*|
#     phi = pow(1. + dim, 2) * X_reduced.var(ddof=1) / trace
#     unimodal = (phi >= 1.)
#     if (not unimodal) or (depth == 1):
#         return unimodal, p_value(phi, n_obs, dim), phi
#     else:
#         return batch_folding_test_robust(X, depth-1)
