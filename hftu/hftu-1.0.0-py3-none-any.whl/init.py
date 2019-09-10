#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@summary: Code to initialize the HFTU optimization
@author: asr
"""

import numpy as np
from scipy.stats import ortho_group
from .types import Matrix


def power_iteration(A: Matrix, n_ite: int) -> Matrix:
    """
    Perform several power iterations to get the eigenvector
    with greatest eigenvalue

    Parameters
    ----------
    A: numpy.ndarray
        Square matrix
    n_ite: int
        Number of iterations
    """
    # Ideally choose a random vector
    # To decrease the chance that our vector
    # Is orthogonal to the eigenvector
    b_k = np.random.rand(A.shape[1])
    for _ in range(n_ite):
        # calculate the matrix-by-vector product Ab
        # change .dot (multi-thread to single thread matrix product)
        b_k1 = np.dot(A, b_k)
        # b_k1 = b_k @ A
        # calculate the norm
        b_k1_norm = np.linalg.norm(b_k1)
        # re normalize the vector
        b_k = b_k1 / b_k1_norm
    return b_k


def variance_init(X: Matrix, cov: Matrix, nb_power_ite: int):
    """
    Compute an initial hyperplane. It returns the hyperplane orthogonal to the
    direction with maximum variance within the dataset.

    Parameters
    ----------
    X: numpy.ndarray
        data (n x d matrix)
    cov: numpy.ndarray
        covariance of X (you can pass None to compute it)
    nb_power_ite: int
        Number of power iterations to get the direction with greatest variance

    Returns
    -------
    u: numpy.ndarray
        normal vector of the hyperplane
    u0: float
        intercept

    Notes
    -----
    The hyperplane is the set of vectors x verifying <u, x> + u0 = 0
    """
    # compute the covariance
    if cov is None:
        cov = np.cov(X.T)
    # perform power iterations to get the direction with
    # maximum of variance
    u = power_iteration(cov, nb_power_ite)
    # take the hyperplane passing through the mean
    # change .dot (multi-thread to single thread matrix product)
    # u0 = -1. * np.dot(X.mean(0), u)
    u0 = -(X.mean(0) * u).sum()
    return u.flatten(), u0


def random_init(X: Matrix):
    """
    Compute a random initial hyperplan passing through the mean of the dataset.

    Parameters
    ----------
    X: numpy.ndarray
        data (n x d matrix)

    Returns
    -------
    u: numpy.ndarray
        normal vector of the hyperplane
    u0: float
        intercept

    Notes
    -----
    The hyperplane is the set of vectors x verifying <u, x> + u0 = 0
    """
    # Random vector of R^d
    u = np.random.uniform(low=-1., high=1., size=X.shape[-1])
    # We normalize it
    u = u / np.linalg.norm(u)
    # Compute the intercept so that the mean belongs to the hyperplane
    # change .dot (multi-thread to single thread matrix product)
    # u0 = -1. * np.dot(X.mean(0), u)
    u0 = -(X.mean(0) * u).sum()
    return u, u0


def orthogonal_random_init(X: Matrix):
    """
    Compute several random initial hyperplane passing through the mean of the dataset.
    It computes d hyperplanes, where d is the space dimension. The particularity
    is that all the normal vectors of the hyperplanes are pairwise orthogonal

    Parameters
    ----------
    X: numpy.ndarray
        data (n x d matrix)

    Returns
    -------
    H: list
        list of tuple (u, u0) where u is the normal vector (numpy.ndarray)
        and u0 is the intercept (float)

    Notes
    -----
    The hyperplane is the set of vectors x verifying <u, x> + u0 = 0
    """
    O = ortho_group.rvs(dim=X.shape[-1])
    mean = X.mean(0)
    # change .dot (multi-thread to single thread matrix product)
    # return [(u, -1. * np.dot(mean, u)) for u in O]
    return [(u, -(mean * u).sum()) for u in O]
