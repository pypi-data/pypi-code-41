#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@summary: Code to plot the folding hyperplane H* (2D or 3D)
@author: asr
"""

import numpy as np
import matplotlib.pyplot as plt
from .types import Matrix, Axes, Pair


def boxed_line(normal_vector: Matrix, intercept: float, xlim: Pair, ylim: Pair) -> (Pair, Pair):
    if normal_vector[0] == 0:
        # horizontal line
        y = -intercept / normal_vector[1]
        return xlim, (y, y)
    if normal_vector[1] == 0:
        # vertical line
        x = -intercept / normal_vector[0]
        return (x, x), ylim

    # output points
    xout = [0, 0]
    yout = [0, 0]
    # neither horizontal nor vertical
    # y = ax + b
    a = - normal_vector[0] / normal_vector[1]
    b = - intercept / normal_vector[1]

    # left point
    y_at_xmin = a * xlim[0] + b
    if y_at_xmin > ylim[1]:
        # if the point is out of the box (up)
        xout[0] = (ylim[1] - b) / a
        yout[0] = ylim[1]
    elif y_at_xmin < ylim[0]:
        # if the point is out of the box (low)
        xout[0] = (ylim[0] - b) / a
        yout[0] = ylim[0]
    else:
        # between the two limits
        xout[0] = xlim[0]
        yout[0] = y_at_xmin

    # right point
    y_at_xmax = a * xlim[1] + b
    if y_at_xmax > ylim[1]:
        # if the point is out of the box (up)
        xout[1] = (ylim[1] - b) / a
        yout[1] = ylim[1]
    elif y_at_xmax < ylim[0]:
        # if the point is out of the box (low)
        xout[1] = (ylim[0] - b) / a
        yout[1] = ylim[0]
    else:
        xout[1] = xlim[1]
        yout[1] = y_at_xmax
    # return the two points
    return tuple(xout), tuple(yout)


def __boxed_plan(normal_vector: Matrix, intercept: float, xlim: Pair, ylim: Pair, zlim: Pair):
    if normal_vector[2] != 0:
        X, Y = np.meshgrid(xlim, ylim)
        Z = np.zeros(X.shape)
        for i in range(len(xlim)):
            for j in range(len(ylim)):
                Z[i, j] = -(intercept +
                            normal_vector[0] * X[i, j] +
                            normal_vector[1] * Y[i, j]) / normal_vector[2]
    elif normal_vector[1] != 0:
        X, Z = np.meshgrid(xlim, zlim)
        Y = np.zeros(X.shape)
        for i in range(len(xlim)):
            for j in range(len(ylim)):
                Y[i, j] = -(intercept +
                            normal_vector[0] * X[i, j] +
                            normal_vector[2] * Z[i, j]) / normal_vector[1]
    else:
        Y, Z = np.meshgrid(xlim, zlim)
        X = np.zeros(X.shape)
        for i in range(len(xlim)):
            for j in range(len(ylim)):
                X[i, j] = -(intercept +
                            normal_vector[1] * Y[i, j] +
                            normal_vector[2] * Z[i, j]) / normal_vector[0]
    return X, Y, Z


# def plot(self, X: Matrix, y: Matrix = None, ax=None, **kwargs) -> Axes:
#     """
#     Plot data and the folding hyperplan (line)
#     """
#     if y is None:
#         y = self.predict(X)

#     if ax is None:
#         f = plt.figure()
#         ax = f.add_subplot(111)
#     ax.scatter(X[:, 0], X[:, 1], c=y)
#     ax.axis('equal')

#     if normal_vector[0] == 0:
#         r = - intercept / normal_vector[1]
#         ax.plot(ax.get_xlim(), (r, r), **kwargs)
#     else:
#         xlim = np.array(self.__boxed_line(ax.get_xlim(), ax.get_ylim()))
#         if normal_vector[1] != 0:
#             a = - normal_vector[0] / normal_vector[1]
#             b = - intercept / normal_vector[1]
#             ax.plot(xlim, a * xlim + b, **kwargs)
#         else:
#             ax.plot(xlim, ax.get_ylim(), **kwargs)
#     return ax


# def plot3d(self, X: Matrix, y: Matrix = None) -> Axes:
#     """
#     Plot data and the folding hyperplan (plan)
#     """
#     if y is None:
#         y = self.predict(X)

#     ax = plt.subplot(111, projection='3d')
#     ax.scatter(X[:, 0], X[:, 1], X[:, 2], c=y)
#     ax.set_aspect('equal')

#     A, B, C = self.__boxed_plan(ax.get_xlim(),
#                                 ax.get_ylim(),
#                                 ax.get_zlim())
#     ax.plot_surface(A, B, C, alpha=0.2)
#     ax.set_aspect('equal')
#     return ax
