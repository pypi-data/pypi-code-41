import os
import sys
import numpy as np
import matplotlib.image as image
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
from matplotlib import cm

from operator import sub
from pathlib import Path
from mpl_toolkits.mplot3d import Axes3D
from matplotlib._png import read_png
from matplotlib.cbook import get_sample_data


class Logotype:
    ''' Class that keeps parameters of a logotype that
        should be added to different graphs.
    '''

    def __init__(self, file_path, x=0, y=0, alpha=0.5):
        my_dir = os.path.dirname(os.path.realpath(__file__))
        path = Path(os.path.join(my_dir, file_path)).resolve()
        if not path.is_file():
            raise FileNotFoundError("logo file is not found: " + file_path)
        self._file_path = path
        if x >= 0:
            self._x = x
        else:
            raise ValueError("Logo position coordinate x must be positive")

        if y >= 0:
            self._y = y
        else:
            raise ValueError("Logo position coordinate y must be positive")

        if alpha > 0 and alpha <= 1:
            self._alpha = alpha
        else:
            raise ValueError("Logo alpha value must be in (0, 1]")

    @property
    def file_path(self):
        return self._file_path

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def alpha(self):
        return self._alpha

    def add_to_3d_graph(self, range_x, range_y, ax):
        # TODO: implement 2d logo on 3d graphs
        with cbook.get_sample_data(self._file_path) as file:
            img = image.imread(file)
            xrng = plt.xlim(range_x[0], range_x[1])
            yrng = plt.ylim(range_y[0], range_y[1])
            ax.imshow(img,
                      extent=[1, 0.1, 10, 0.1],
                      origin='upper',
                      alpha=self._alpha,
                      aspect='auto')

    def add_to_2d_graph(self, fig):
        with cbook.get_sample_data(self._file_path) as file:
            img = image.imread(file)
            fig.figimage(img,
                         self._x,
                         self._y,
                         zorder=1,
                         alpha=self._alpha)


def _add_logo_2d(logo, fig):
    if logo:
        if isinstance(logo, bool):
            logo = Logotype("logo64.png", x=400, y=300, alpha=0.4)
        if isinstance(logo, Logotype):
            logo.add_to_2d_graph(fig)


def _add_logo_3d(logo, ax):
    if logo:
        raise AttributeError("Logotypes are not supported for d>1")
        logo.add_to_3d_graph(range_x, range_y, ax)


def convergence(convergence, title, logo=True, save_to=None):
    '''Plot convergence to a solution (result: 2d graph)
    '''
    fig, ax = plt.subplots()
    _add_logo_2d(logo, fig)

    ax.set_xlabel('number of function evaluations')
    ax.set_ylabel('value of function')
    ax.set_title(title)
    ax.plot(convergence, 'b', label='line')
    ax.grid()

    if save_to:
        plt.savefig(save_to, bbox_inches='tight')
    else:
        plt.show()


def _zip_xy(fobj, X, Y, dim, d0, d1):
    def _get_value(x, y):
        args = [0] * dim
        args[d0] = x
        args[d1] = y
        return fobj(args)

    return [_get_value(x, y) for x, y in zip(np.ravel(X), np.ravel(Y))]


def fobj_2d(fobj, solution, range_x, range_y, dim, dim_indices,
            title, logo=True, save_to=None):
    '''Plot 2d objective function (result: 3d graph)
    '''
    d0, d1 = _get_dimenstion_indeces(dim, dim_indices)

    step_x = abs(range_x[0] - range_x[1]) / 500  # TODO as option for user to change steps_x=500 (with default value)
    step_y = abs(range_y[0] - range_y[1]) / 500  # TODO as option for user to change steps_y=500 (with default value)

    x = np.arange(range_x[0], range_x[1], step_x)
    y = np.arange(range_y[0], range_y[1], step_y)
    X, Y = np.meshgrid(x, y)

    zs = np.array(_zip_xy(fobj, X, Y, dim, d0, d1))
    Z = zs.reshape(X.shape)

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    surf = ax.plot_surface(X, Y, Z, cmap=cm.gist_rainbow, antialiased=False, alpha=0.3)
    cset = ax.contour(X, Y, Z, zdir='z', offset=fobj(solution), cmap=cm.coolwarm)

    ax.grid(b=False, which='major', color='#D3D3D3', linestyle='-')
    ax.set_xlim(x[0], x[-1])
    ax.set_ylim(y[0], y[-1])
    ax.set_xlabel('x%s' % (d0 + 1).__str__())
    ax.set_ylabel('x%s' % (d1 + 1).__str__())
    ax.set_zlabel('fobj')
    ax.set_title(title)

    # _add_logo_3d(logo, ax)

    if save_to:
        plt.savefig(save_to, bbox_inches='tight')
    else:
        plt.show()


def fobj_1d(fobj, sol_range, title, logo=True, save_to=None):
    '''Plot 1d objective function (result: 2d graph)
    '''
    fig, ax = plt.subplots()
    _add_logo_2d(logo, fig)

    ax.set_xlabel('x')
    ax.set_ylabel('objective function')
    ax.set_title(title)
    # TODO better to intruduce the number of steps in range to compute
    x = np.arange(sol_range[0], sol_range[1], 0.0001)  # TODO as option for user to change steps=1000 (with default value)
    y = fobj(x)

    ax.plot(x, y, label='line')
    ax.grid()

    if save_to:
        plt.savefig(save_to, bbox_inches='tight')
    else:
        plt.show()


def optimum_1d(title, fobj, solution, sol_range, eps, logo, save_to=None):
    '''Plot optimum area for 1d objective function (result: 2d graph)
    '''
    fig, ax = plt.subplots()
    _add_logo_2d(logo, fig)

    ax.set_xlabel('x')
    ax.set_ylabel('fobj')
    ax.set_title(title)

    # Ensure that we don't plot out of boundaries
    low = solution - eps
    high = solution + eps
    if sol_range and low < sol_range[0]:
        low = sol_range[0]
    if sol_range and high > sol_range[1]:
        high = sol_range[1]

    x = np.arange(low, high, eps / 100)  # TODO as steps=1000 optional param with default value
    y = fobj(x)

    ax.grid()
    for i in range(9):
        ax.plot(solution, fobj(solution), 'ro', fillstyle='none', markersize=i)
    ax.plot(x, y, label='line')

    if save_to:
        plt.savefig(save_to, bbox_inches='tight')
    else:
        plt.show()


def _get_dimenstion_indeces(dim, dim_indices):
    d0 = 0
    d1 = 1
    if dim_indices:
        if not isinstance(dim_indices, list):
            print(sys.stderr, "Dimension indeces parameter must be a list")
        elif not len(dim_indices) == 2:
            print(sys.stderr, "Dimension indeces list length must be 2")
        elif not isinstance(dim_indices[0], int):
            print(sys.stderr, "Dimension index 0 must be an integer number: %s" % dim_indices[0])
        elif not isinstance(dim_indices[1], int):
            print(sys.stderr, "Dimension index 1 must be an integer number: %s" % dim_indices[1])
        elif dim_indices[0] < 0:
            print(sys.stderr, "Dimension index 0 must pbe positive: %s" % dim_indices[0])
        elif dim_indices[1] < 0:
            print(sys.stderr, "Dimension index 1 must pbe positive: %s" % dim_indices[1])
        elif dim_indices[0] >= dim:
            print(sys.stderr, "Dimension index 0 must pbe positive: %s" % dim_indices[0])
        elif dim_indices[1] >= dim:
            print(sys.stderr, "Dimension index 1 must pbe positive: %s" % dim_indices[1])
        elif dim_indices[0] == dim_indices[1]:
            print(sys.stderr, "Dimension indeces must differ: %d" % dim_indices[0])
        else:
            d0 = dim_indices[0]
            d1 = dim_indices[1]
    return d0, d1


def _get_eps_range(d0, d1, solution, sol_range, eps):
    ''' Ensure that we don't plot out of boundaries
    '''
    eps_x_low = solution[d0] - eps
    eps_x_high = solution[d0] + eps
    eps_y_low = solution[d1] - eps
    eps_y_high = solution[d1] + eps

    if eps_x_low < sol_range[0][d0]:
        eps_x_low = sol_range[0][d0]
    if eps_x_high > sol_range[1][d0]:
        eps_x_high = sol_range[1][d0]
    if eps_y_low < sol_range[0][d1]:
        eps_y_low = sol_range[0][d1]
    if eps_y_high > sol_range[1][d1]:
        eps_y_high = sol_range[1][d1]

    return [eps_x_low, eps_x_high], [eps_y_low, eps_y_high]


def optimum_2d(title, fobj, solution, sol_range, eps, dim, dim_indices, logo, save_to=None):
    '''Plot optimum area for 1d objective function (result: 2d graph)
    '''
    d0, d1 = _get_dimenstion_indeces(dim, dim_indices)
    range_x, range_y = _get_eps_range(d0, d1, solution, sol_range, eps)

    x = np.arange(range_x[0], range_x[1], eps / 300)
    y = np.arange(range_y[0], range_y[1], eps / 300)
    X, Y = np.meshgrid(x, y)
    zs = np.array([fobj([x, y]) for x, y in zip(np.ravel(X), np.ravel(Y))])
    Z = zs.reshape(X.shape)

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    surf = ax.plot_surface(X, Y, Z, cmap=cm.gist_rainbow, antialiased=False, alpha=0.3)
    cset = ax.contour(X, Y, Z, zdir='z', offset=fobj(solution), cmap=cm.coolwarm)

    ax.set_xlabel('x%s' % (d0 + 1).__str__())
    ax.set_ylabel('x%s' % (d1 + 1).__str__())
    ax.set_zlabel('fobj')
    ax.set_xlim(x[0], x[-1])
    ax.set_ylim(y[0], y[-1])
    ax.set_title(title)

    ax.plot([solution[d0]], [solution[d1]], [fobj(solution)], 'ro', markersize=7)

    # _add_logo_3d(logo, ax)

    if save_to:
        plt.savefig(save_to, bbox_inches='tight')
    else:
        plt.show()
