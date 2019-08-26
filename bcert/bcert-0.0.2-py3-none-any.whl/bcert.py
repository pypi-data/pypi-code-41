# coding: utf-8

import os
import numpy as np

from abc import ABCMeta, abstractmethod
from multiprocessing import Pool

class FunLipschitz(object):
    def __init__(self, fix_param=None):
        self.fix_param = fix_param
        self.b_df = self.bound_df()

    @abstractmethod
    def f(self,x):
        raise NotImplemented("Please implement the function")

    @abstractmethod
    def bound_df(self):
        raise NotImplemented("Please implement the function: return a list of bound on partial derivatives")


class CompactSpace(object):
    def __init__(self, bound):
        self.__bound = self.__check_dim_bound(bound)
        self.__dim = len(bound)

    def __check_dim_bound(self,bound):
        if len(bound.shape) != 2:
            raise ValueError("bound should be of two dimensions, found dimension {}".format(len(bound.shape)))
        elif len(bound[0]) !=2:
            raise ValueError("bound should contain exactly two elements per dimension")
        else:
            return bound

    def discretized(self, step):
        if type(step) in [int,float]:
            return self.discretized_symmetric(step)
        elif type(step) is np.ndarray:
            return self.discretized_asymmetric(step)

    def discretized_symmetric(self, step):
        X = np.meshgrid(*[np.arange(b[0],b[1]+step,step) for b in self.__bound])
        grid = np.array([x.ravel() for x in X]).T
        return grid

    def discretized_asymmetric(self, step):
        X = np.meshgrid(*[np.arange(b[0],b[1]+step[i],step[i]) for i,b in enumerate(self.__bound)])
        grid = np.array([x.ravel() for x in X]).T
        return grid

    def discr_element(self, elem, directions, step):
        if len(elem) != self.__dim:
            raise ValueError("provide element is not in the same space as the original compact space")
        grid = []
        if directions is None:
            directions = range(self.__dim)
        for _ in directions:
            grid.append([e-step if _==i and e>self.__bound[_][0] else e for i,e in enumerate(elem)])
            grid.append([e+step if _==i and e<self.__bound[_][0] else e for i,e in enumerate(elem)])
        grid = np.unique(np.array(grid), axis=0)
        grid = np.delete(grid, np.where([(g==elem).all() for g in grid]), axis=0)
        return grid


def boundCert(fun, space, lmbd, step, exclude_element=None, **kwargs):
    depth = kwargs.get("depth", 0)
    verbose = kwargs.get("verbose",0)
    max_depth = kwargs.get("max_depth",-1)
    f_max = kwargs.get("f_max", -np.inf)
    g_max = kwargs.get("g_max", None)
    direction = kwargs.get("direction", None)
    elem = kwargs.get("elem", None)
    grid = space.discretized(step) if depth == 0 else space.discr_element(elem, direction, step/2)
    if verbose != 0:
        if depth % verbose:
            print("Depth {}, step is {}, max_function {}".format(depth, delta,max_f))
    for e,g in enumerate(grid):
        if type(exclude_element) is np.ndarray:
            if np.array([(g==_).all() for _ in exclude_element]).any():
                continue
        eval_f = fun.f(g)
        if eval_f >= lmbd:
            raise Exception("Exceed or found {}: reach {} at grid element {}, certification failed.".format(lmbd, eval_f, g))
        evol_f = np.array([eval_f+(step*df/2) for df in fun.b_df])
        exceed_lmbd = np.where(evol_f > lmbd)[0]
        if exceed_lmbd.size:
            f_max_tmp, g_max_tmp = boundCert(fun, space, lmbd, step/2, exclude_element=exclude_element,
                    f_max=f_max, g_max=g_max, depth=depth+1, direction=exceed_lmbd, elem=g)
            if f_max_tmp > f_max:
                f_max = f_max_tmp
                g_max = g_max_tmp
        else:
            if max(evol_f) >= f_max:
                f_max = max(evol_f)
                g_max = g
    if depth == 0:
        print("Maximum value found {} for x={}".format(f_max,g_max))
        print("Certification sucessfull.")
    return f_max, g_max

def boundCertPar(fun, bound, lmbd, step, threads=os.cpu_count(), exclude_element=None):
    bound_max = np.argmax([b[1]-b[0] for b in bound])
    bound_subdiv = bound[bound_max][1]/threads
    bound_div = [bound[:bound_max] + [[bound_subdiv*_, bound_subdiv*(_+1)]] 
            + bound[bound_max+1:] for _ in range(threads)]
    if step >= bound_max:
        step = bound_max/2
        print("Step larger than bound_subdiv, changing it's value to {}".format(step))
    spaces = [CompactSpace(np.array(b)) for b in bound_div]
    with Pool(processes=threads) as pool:
        res = pool.starmap(boundCert, [(fun, s, lmbd, step, exclude_element) for s in spaces])
        print("Found max:\n",res)
        print("Certified.\n")
        return res
