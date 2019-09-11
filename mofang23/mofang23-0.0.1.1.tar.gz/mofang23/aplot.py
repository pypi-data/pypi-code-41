# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     aplot
   Description :
   Author :        Asdil
   date：          2019/5/9
-------------------------------------------------
   Change Activity:
                   2019/5/9:
-------------------------------------------------
"""
__author__ = 'Asdil'
import random as rd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import seaborn as sns
sns.set_style("darkgrid")


# 计算散点平均值方差
def computePosCov(points, nstd=2, ax=None, **kwargs):
    """
    Plots an `nstd` sigma ellipse based on the mean and covariance of a point
    "cloud" (points, an Nx2 array).

    Parameters
    ----------
        points : An Nx2 array of the data points.
        nstd : The radius of the ellipse in numbers of standard deviations.
            Defaults to 2 standard deviations.
        ax : The axis that the ellipse will be plotted on. Defaults to the
            current axis.
        Additional keyword arguments are pass on to the ellipse patch.

    Returns
    -------
        A matplotlib ellipse artist
    """
    pos = points.mean(axis=0)
    cov = np.cov(points, rowvar=False)
    return plotByPosCov(pos, cov, nstd, ax, **kwargs)


# 使用mean，cov计算置信椭圆
def plotByPosCov(pos, cov, nstd=2, ax=None, **kwargs):
    return plotEllipse(cov, pos, nstd, ax, **kwargs)


# 计算置信椭圆
def plotEllipse(cov, pos, nstd=2, ax=None, **kwargs):
    """
    Plots an `nstd` sigma error ellipse based on the specified covariance
    matrix (`cov`). Additional keyword arguments are passed on to the
    ellipse patch artist.

    Parameters
    ----------
        cov : The 2x2 covariance matrix to base the ellipse on
        pos : The location of the center of the ellipse. Expects a 2-element
            sequence of [x0, y0].
        nstd : The radius of the ellipse in numbers of standard deviations.
            Defaults to 2 standard deviations.
        ax : The axis that the ellipse will be plotted on. Defaults to the
            current axis.
        Additional keyword arguments are pass on to the ellipse patch.

    Returns
    -------
        A matplotlib ellipse artist
    """
    def eigsorted(cov):
        vals, vecs = np.linalg.eigh(cov)
        order = vals.argsort()[::-1]
        return vals[order], vecs[:, order]

    if ax is None:
        ax = plt.gca()

    vals, vecs = eigsorted(cov)
    theta = np.degrees(np.arctan2(*vecs[:, 0][::-1]))

    # Width and height are "full" widths, not radius
    width, height = 2 * nstd * np.sqrt(vals)
    ellip = Ellipse(xy=pos, width=width, height=height, angle=theta, **kwargs)
    ellip.set_facecolor('none')
    #     ax.add_artist(ellip)
    ax.add_patch(ellip)
    return ellip, pos[0], pos[1], width, height, theta


# 颜色
def colors(random=False):
    colors = ['red', 'blue', 'green', '#801dae',
              'orange', 'yellow', '#ff7500', '#c3272b',
              '#70f3ff', 'black', '#b36d61', '#4b55c4',
              '#955539', '#3eede7', '#00e079',
              '#c0ebd7', '#eacd76', '#fff143']

    if random:
        rd.shuffle(colors)
    return colors

def hp():
    print('函数 computePosCov 计算散点均值方差画置信椭圆')
    print('函数 plotByPosCov使用均值方差置信椭圆')
    print('函数 plotEllipse画置信椭圆')
    print('函数 color 返回18中颜色')
