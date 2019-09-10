#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@summary: Optimizers
@author: asr
"""

import os
import numpy as np
import scipy.optimize as opt

from joblib import Parallel, delayed
import concurrent.futures as futures

from .types import OptimizeResult, Matrix
from .folding import __target_function
from .init import power_iteration, random_init, variance_init, orthogonal_random_init

PARALLEL_ENV_VAR = ['OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS']


def _legacy_optimizer(X: Matrix,
                      u: Matrix,
                      u0: float,
                      slsqp_opt: dict) -> (Matrix, float, OptimizeResult):

    def __constraint__fun(z: Matrix) -> float:
        beta = z[:-1].flatten()
        # change .dot (multi-thread to single thread matrix product)
        # return np.dot(beta, beta) - 1
        return (beta**2).sum() - 1

    def __constraint__jac(z: Matrix) -> float:
        t = 2 * z
        t[-1] = 0.
        return t

    def __obj_fun(y: Matrix):
        return __target_function(X, y[:-1], y[-1])

    const = {"type": "eq",
             "fun": __constraint__fun,
             "jac": __constraint__jac}

    results = opt.minimize(__obj_fun,
                           x0=np.hstack((u, u0)),
                           constraints=(const),
                           method='SLSQP',
                           options=slsqp_opt)
    # return the normal vector, the intercept and
    # the optimization results
    return results.x[:-1], results.x[-1], results


def legacy_optimizer_variance(
        X: Matrix,
        cov: Matrix,
        power_iterations: int,
        slsqp_opt: dict) -> (Matrix, float, OptimizeResult):

    # check covariance
    if cov is None:
        cov = np.cov(X.T)
    # initialize the optimizer
    u, u0 = variance_init(X, cov, power_iterations)
    # run
    return _legacy_optimizer(X, u, u0, slsqp_opt)


def legacy_optimizer_random_single(
        X: Matrix,
        slsqp_opt: dict) -> (Matrix, float, OptimizeResult):

    # initialize the optimizer
    u, u0 = random_init(X)
    # run
    return _legacy_optimizer(X, u, u0, slsqp_opt)


def legacy_optimizer_random(
        X: Matrix,
        n_init: int,
        slsqp_opt: dict) -> (Matrix, float, OptimizeResult):

    all_results = [legacy_optimizer_random_single(X=X,
                                                  slsqp_opt=slsqp_opt)
                   for _ in range(n_init)]
    # return the best result
    return min(all_results, key=lambda res: res[-1].fun)


class HeuristicResult:
    """
    Basic structure to present the results of the heuristic method
    """

    def __init__(
        self,
        n_ite: int,
        u: Matrix,
        u0: float,
        target: float,
        above_center: Matrix,
            below_center: Matrix):

        self.n_ite = n_ite
        self.u = u
        self.u0 = u0
        self.target = target
        self.above_center = above_center
        self.below_center = below_center

    def __repr__(self):
        return """\
         n_ite: {:d}
             u: {}
            u0: {}
        target: {:.6f}
  above center: {}
  below center: {}""".format(self.n_ite,
                             self.u,
                             self.u0,
                             self.target,
                             self.above_center,
                             self.below_center)


def _evaluate(X: Matrix, u: Matrix, u0: float) -> (float, Matrix, Matrix):
    # change .dot (multi-thread to single thread matrix product)
    # hx = X.dot(u) + u0
    hx = np.matmul(X, u) + u0
    index = (hx >= 0)
    a = X[index].mean(0)
    b = X[~index].mean(0)
    w = hx.mean()**2 - np.abs(hx).mean()**2
    return w, a, b


def _heuristic_optimizer(X: Matrix, u: Matrix, u0: float, max_ite: int,
                         tol: float) -> (Matrix, float, HeuristicResult):
    # compute the target function f
    # HX = X.dot(u) + u0
    # W = HX.mean()**2 - np.abs(HX).mean()**2
    W, A, B = _evaluate(X, u, u0)

    # iterations
    for i in range(max_ite):
        # compute the new hyperplane
        # up = (HX >= 0)
        # Mu = X[up].mean(0)
        # Md = X[~up].mean(0)
        # target
        # w, a, b = _evaluate(X, u, u0)
        gap = A - B
        v = gap / np.linalg.norm(gap)
        # change .dot (multi-thread to single thread matrix product)
        # v0 = -1. * np.dot(v, (A + B) / 2.0)
        v0 = - (v * (A + B) / 2.0).sum()
        # compute the corresponding target
        w, a, b = _evaluate(X, v, v0)
        # hx = X.dot(v) + v0
        # g = hx.mean()**2 - np.abs(hx).mean()**2
        # check the relative tolerance
        if abs((W - w) / W) < tol:
            return v, v0, HeuristicResult(i + 1, v, v0, w, a, b)
        # update the current hyperplane
        u, u0, W, A, B = v, v0, w, a, b
        # >> iterate again >>

    # return the results
    return v, v0, HeuristicResult(max_ite, v, v0, w, a, b)


def heuristic_optimizer_random_single(X: Matrix,
                                      max_ite: int,
                                      tol: float) -> (Matrix,
                                                      float,
                                                      HeuristicResult):

    # initialize the optimizer randomly
    u, u0 = random_init(X)

    # run
    return _heuristic_optimizer(X, u, u0, max_ite, tol)


def heuristic_optimizer_random(X: Matrix,
                               n_init: int,
                               max_ite: int,
                               tol: float) -> (Matrix,
                                               float,
                                               HeuristicResult):
    all_results = [heuristic_optimizer_random_single(X=X,
                                                     max_ite=max_ite,
                                                     tol=tol)
                   for _ in range(n_init)]
    # return the best result
    return min(all_results, key=lambda res: res[-1].target)


def heuristic_optimizer_variance(X: Matrix,
                                 cov: Matrix,
                                 power_iterations: int,
                                 max_ite: int,
                                 tol: float) -> (Matrix,
                                                 float,
                                                 HeuristicResult):
    # initialize the optimizer with variance
    u, u0 = variance_init(X, cov, power_iterations)

    # run
    return _heuristic_optimizer(X, u, u0, max_ite, tol)


# def heuristic_optimizer_ortho(X: Matrix,
#                               max_ite: int,
#                               tol: float) -> (Matrix,
#                                               float,
#                                               HeuristicResult):
#     all_results = [_heuristic_optimizer(X, u, u0, max_ite, tol)
#                    for u, u0 in orthogonal_random_init(X)]
#     # return the best result
#     return min(all_results, key=lambda res: res[-1].target)

# def __split(X: Matrix, u: Matrix, u0: float) -> (float, Matrix, Matrix):
#     n, d = X.shape
#     q = 0
#     A = np.zeros(d)
#     B = np.zeros(d)
#     for x in X:
#         h = x.dot(u) + u0
#         if h >= 0:
#             A += x
#             q += 1
#         else:
#             B += x
#     A = A / q
#     B = B / (n - q)
#     p = q / n
#     gap = A - B
#     return p * (1 - p) * gap.dot(gap), A, B

# def heuristic_optimizer_random(X: Matrix,
#                                max_ite: int,
#                                tol: float) -> (Matrix,
#                                                float,
#                                                HeuristicResult):

#     # initialize the optimizer
#     u, u0 = random_init(X)

#     # compute the target function f
#     W, A, B = __split(X, u, u0)

#     # iterations
#     for i in range(max_ite):
#         # new hyperplane
#         v = (A - B) / np.linalg.norm(A - B)
#         v0 = -1. * np.dot(v, (A + B) / 2.0)
#         # compute the corresponding target
#         w, a, b = __split(X, v, v0)
#         # check the relative tolerance
#         if abs((W - w) / W) < tol:
#             return v, v0, HeuristicResult(i + 1, v, v0, w)
#         # if np.linalg.norm(u - v) < tol:
#         #     return v, v0, HeuristicResult(i + 1, v, v0, g)
#         # update the hyperplane
#         u = v
#         u0 = v0
#         W = w
#         A = a
#         B = b
#         # iterate again

#     # return the results
#     return v, v0, HeuristicResult(max_ite, v, v0, w)


# class ParallelHeuristic:
#     def __init__(self, X: Matrix, max_ite: int, tol: float):
#         self.data = X
#         self.max_ite = max_ite
#         self.tol = tol

#     def single_run(self):
#         return heuristic_optimizer_random(X=self.data,
#                                           max_ite=self.max_ite,
#                                           tol=self.tol)

#     def run(self, n_init: int):
#         # l = list(range(n_init))
#         # processes = [Process(target=self.single_run) for _ in range(n_init)]
#         processes = [
#             Process(
#                 target=heuristic_optimizer_random,
#                 args=(
#                     self.data,
#                     self.max_ite,
#                     self.tol)) for _ in range(n_init)]
#         [p.start() for p in processes]
#         z = [p.join() for p in processes]
#         print(z)
#         return min(z, key=lambda res: res[-1].target)
#         # with Pool(4) as pool:
#         #     p = pool.map(self.single_run, l)
#         # return min(p, key=lambda res: res[-1].target)

# class ParallelHeuristic:
#     def __init__(self, n_jobs: int, max_ite: int, tol: float):
#         self.context = Parallel(n_jobs=n_jobs)
#         self.max_ite = max_ite
#         self.tol = tol

#     def run(self, X: Matrix, n_init: int) -> (Matrix, float,):
#         results = self.context(delayed(heuristic_optimizer_random)(X, self.max_ite, self.tol)
#                                for i in range(n_init))
#         U, U0, HR = zip(*results)
#         best = np.argmin(map(lambda r: r.target, HR))
#         return U[best], U0[best], HR[best]

#     def run_multiple(self, generator, n_init):
#         with Parallel(n_jobs=4, prefer='threads') as context:
#             for X in generator:
#                 results = context(delayed(heuristic_optimizer_random)(X, self.max_ite, self.tol)
#                                   for i in range(n_init))
#                 U, U0, HR = zip(*results)
#                 best = np.argmin(map(lambda r: r.target, HR))


# def _activate_multithreading():
#     for k in PARALLEL_ENV_VAR:
#         try:
#             del os.environ[k]
#         except KeyError:
#             continue


# def _desactivate_multithreading():
#     for k in PARALLEL_ENV_VAR:
#         os.environ[k] = '1'


# def heuristic_optimizer_random_parallel(
#         X: Matrix,
#         n_init: int,
#         max_ite: int,
#         tol: float,
#         n_jobs: int):

#     results = Parallel(n_jobs=n_jobs, verbose=0, prefer='threads')(
#         delayed(heuristic_optimizer_random_single)(X, max_ite, tol)
#         for i in range(n_init))

#     U, U0, HR = zip(*results)
#     best = np.argmin(map(lambda r: r.target, HR))
#     return U[best], U0[best], HR[best]


def __fun(args):
    X, max_ite, tol = args
    return heuristic_optimizer_random_single(X, max_ite, tol)


def heuristic_optimizer_random_parallel(
        X: Matrix,
        n_init: int,
        max_ite: int,
        tol: float,
        n_jobs: int):

    min_target = np.inf
    U, U0, HR = None, None, None
    with futures.ThreadPoolExecutor(max_workers=n_jobs) as executor:
        # Start the load operations and mark each future with its URL
        iterable = [(X, max_ite, tol) for _ in range(n_init)]
        results = executor.map(__fun, iterable)

        for u, u0, hr in results:
            # u, u0, hr = f.result()
            if hr.target < min_target:
                min_target = hr.target
                U, U0, HR = u, u0, hr
        # ff = [executor.submit(heuristic_optimizer_random_single,
        #                       X, max_ite, tol) for _ in range(n_init)]
        # for f in futures.as_completed(ff):
        #     u, u0, hr = f.result()
        #     if hr.target < min_target:
        #         min_target = hr.target
        #         U, U0, HR = u, u0, hr

        return U, U0, HR


# def legacy_optimizer_random_parallel(
#         X: Matrix,
#         n_init: int,
#         slsqp_opt: dict,
#         n_jobs: int):

#     results = Parallel(n_jobs=n_jobs, verbose=0, prefer='threads')(
#         delayed(legacy_optimizer_random_single)(X, slsqp_opt)
#         for i in range(n_init))

#     U, U0, HR = zip(*results)
#     best = np.argmin(map(lambda r: r.target, HR))
#     return U[best], U0[best], HR[best]


def legacy_optimizer_random_parallel(
        X: Matrix,
        n_init: int,
        slsqp_opt: dict,
        n_jobs: int):

    min_target = np.inf
    U, U0, HR = None, None, None
    with futures.ThreadPoolExecutor(max_workers=n_jobs) as executor:
        # Start the load operations and mark each future with its URL
        ff = [executor.submit(legacy_optimizer_random_single,
                              X, slsqp_opt) for _ in range(n_init)]
        for f in futures.as_completed(ff):
            u, u0, hr = f.result()
            if hr.fun < min_target:
                min_target = hr.fun
                U, U0, HR = u, u0, hr

        return U, U0, HR
