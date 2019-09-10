#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@summary: Code to compute HFTU
@author: asr
"""

import numpy as np
from .types import Matrix, Axes, Any
from .optimization import legacy_optimizer_variance, legacy_optimizer_random
from .optimization import heuristic_optimizer_random, heuristic_optimizer_variance
from .optimization import heuristic_optimizer_random_parallel, legacy_optimizer_random_parallel
from .folding import folding_statistics, decision_bound, inverse_decision_bound
from .plot import boxed_line
import matplotlib.pyplot as plt


class HFTU:
    def __init__(self):
        self.size_ = (0, 0)
        self.coef_ = None
        self.intercept_ = None
        self.covariance_ = None
        self.folding_statistics_ = None
        self.__fitted = False

    def fit(
            self,
            X: Matrix,
            method: str = 'legacy',
            init: str = 'variance',
            power_iterations: int = 15,
            n_init: int = 10,
            max_ite: int = 30,
            tol: float = 1e-4,
            n_jobs: int = -1,
            slsqp_opt: dict = {'maxiter': 100}):
        """
        Compute the best folding hyperplane according to the input data

        Parameters
        ----------
        X: numpy.ndarray
            data (n x d matrix)
        method: str
            'legacy' or 'heuristic'. The 'legacy' method uses a contrained optimization algorithm
            while 'heuristic' uses a k-means-like procedure to find the best hyperplane (it is faster).
        init: str
            Way to compute an initial hyperplane: 'variance' or 'random':
            'variance takes the hyperplane orthogonal to the covariance eigenvector with greatest
            eigenvalue (direction with maximum of variance). 'random' takes a random hyperplane, it is
            relevant when several runs are performed (see n_init).
        power_iterations: int
            ('variance' initialization only) number of power iterations to get the eigenvector with
            greatest eigenvalue.
        n_init: int
            ('random' initialization only) number of runs to perform
        max_ite: int
            ('heuristic' method only) number of iterations whithin the heuristic
        tol: float
            ('heuristic' method only) relative tolerance on the target (folded variance) to stop the heuristic
        n_jobs: int
            ('random' initialization only) number of parallel runs to perform
        slsqp_opt: dict
            ('legacy' method only) parameters to pass to the SLSQP algorithm of Scipy.
            See https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html
        """
        # null results
        results = None
        # retrieve the size
        self.size_ = X.shape
        # retrieve the covariance
        self.covariance_ = np.cov(X.T)
        # FIT
        if method == 'legacy':
            if init == 'variance':
                u, u0, results = legacy_optimizer_variance(
                    X=X,
                    cov=self.covariance_,
                    power_iterations=power_iterations,
                    slsqp_opt=slsqp_opt)
            elif init == 'random':
                if n_jobs > 1:
                    u, u0, results = legacy_optimizer_random_parallel(X=X,
                                                                      n_init=n_init,
                                                                      slsqp_opt=slsqp_opt,
                                                                      n_jobs=n_jobs)
                else:
                    u, u0, results = legacy_optimizer_random(X=X,
                                                             n_init=n_init,
                                                             slsqp_opt=slsqp_opt)
        elif method == 'heuristic':
            if init == 'variance':
                u, u0, results = heuristic_optimizer_variance(
                    X=X,
                    cov=self.covariance_,
                    power_iterations=power_iterations,
                    max_ite=max_ite,
                    tol=tol)
            elif init == 'random':
                if n_jobs > 1:
                    u, u0, results = heuristic_optimizer_random_parallel(X=X,
                                                                         n_init=n_init,
                                                                         max_ite=max_ite,
                                                                         tol=tol,
                                                                         n_jobs=n_jobs)
                else:
                    u, u0, results = heuristic_optimizer_random(X=X,
                                                                n_init=n_init,
                                                                max_ite=max_ite,
                                                                tol=tol)
            else:
                raise ValueError(
                    "Unknown initialization method: only 'variance' and 'random' are supported")
        else:
            raise ValueError("Unknown method: only 'legacy' and 'heuristic' are supported")

        # update the attributes
        self.coef_ = u
        self.intercept_ = u0
        self.folding_statistics_ = folding_statistics(X, u, u0)
        self.__fitted = True
        return results

    def predict(self, X: Matrix) -> Matrix:
        """
        Return a classification of the input data (1 for points "above" H*
        and 0 for points "below")
        """
        if not self.__fitted:
            raise RuntimeError("Data have not been fitted")
        return (X.dot(self.coef_) + self.intercept_ >= 0).astype(int)

    def fit_predict(self, X: Matrix, **kwargs) -> (Matrix, Any):
        """
        Compute the best folding hyperplane according to the input data and
        return a classification of the input data (1 for points "above" H*
        and 0 for points "below")

        Parameters
        ----------
        X: numpy.ndarray
            data (n x d matrix)
        kwargs:
            parameters passed for the fit (see the 'HFTU.fit' function)
        """
        # perform the fit
        results = self.fit(X=X, **kwargs)
        # return 1 for points "above" H* and 0 for points "below"
        return self.predict(X), results

    def is_unimodal(self, alpha: float) -> bool:
        """
        Return whether the fitted dataset is unimodal or not at
        given level alpha.

        Parameters
        ----------
        alpha: float
            type I error associated to the null hypothesis H0:
            "X is uniformly distributed". This is the probability
            to reject H0 while it is true. It is roughly the probability
            to say "multimodal" while it is "unimodal".
        """
        if not self.__fitted:
            raise RuntimeError("Data have not been fitted")
        return self.folding_statistics_ >= decision_bound(
            n=self.size_[0], d=self.size_[1], alpha=alpha)

    def confidence(self):
        """
        Return the corresponding type I error which would
        output the fitted dataset as unimodal/multimodal.
        If the output is very close to 1, it means that
        the test is confident while outputing "unimodal".
        If it is close to 0, the test is confident while
        outputing "multimodal".
        """
        if not self.__fitted:
            raise RuntimeError("Data have not been fitted")
        return inverse_decision_bound(
            n=self.size_[0],
            d=self.size_[1],
            Phi=self.folding_statistics_)

    def plot(
            self,
            X: Matrix,
            y: Matrix = None,
            hyperplane_plot_opt: dict = {},
            ax: Axes = None, **kwargs) -> Axes:
        """
        2D data only
        """
        if y is None:
            y = self.predict(X)
        if ax is None:
            f = plt.figure()
            ax = f.add_subplot(111)
        # plot the observations
        ax.scatter(X[:, 0], X[:, 1], c=y, **kwargs)
        # scale axes (normed)
        ax.axis('equal')
        a, b = boxed_line(self.coef_,
                          self.intercept_,
                          ax.get_xlim(),
                          ax.get_ylim())
        print(a, b)
        ax.plot(a, b, **hyperplane_plot_opt)
        return ax
