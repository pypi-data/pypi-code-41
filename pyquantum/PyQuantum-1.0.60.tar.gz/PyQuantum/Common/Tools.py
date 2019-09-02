import os
import numpy as np
import pandas as pd

# from inspect import currentframe as cf
# from inspect import getframeinfo
# from Common.Assert import *


def list_to_csv(outfile, states, header):
    pd.DataFrame(states).to_csv(outfile, header=header, index=False)


def write_x(states, x_csv, ind_1=None, ind_2=None):
    _k = [int(k) for k in states.keys()]
    _v = [str(v) for v in states.values()]

    if ind_1 != None and ind_2 != None:
        lKey = [key for key, value in states.items() if value == ind_1][0]
        rKey = [key for key, value in states.items() if value == ind_2][0]

        for k in _k:
            if k != lKey and k != rKey:
                _v[k] = ""
    _x = np.matrix([
        _v,
        _k
    ]).getT()

    list_to_csv(x_csv, _x, ["x", "vals"])


def write_x_not_ind(states, x_csv):
    _k = []
    _v = []

    for k, v in enumerate(states):
        _k.append(k)
        _v.append(str(v))

    # exit(1)
    _x = np.matrix([
        _v,
        _k
    ]).getT()

    list_to_csv(x_csv, _x, ["x", "vals"])


def write_xx(states, x_csv):
    _k = [int(k) for k in states.keys()]
    # _v = [str(v) for v in states.values()]
    _v = [v for v in states.values()]

    # if ind_1 != None and ind_2 != None:
    #     lKey = [key for key, value in states.items() if value == ind_1][0]
    #     rKey = [key for key, value in states.items() if value == ind_2][0]
    # print(ind)
    # print(states)
    # print(_k)
    # print(_v)
    # for i in range(len(ind)):
    # ind[i] = str(ind[i])
    # print(ind)
    for k in _k:
        _v[k] = str(states[k])

    # exit(1)
    _x = np.matrix([
        _v,
        _k
    ]).getT()

    list_to_csv(x_csv, _x, ["x", "vals"])


def write_xbp(states, x_csv, ind):
    _x = np.matrix([
        list(ind.values()),
        list(ind.keys())
    ]).getT()

    list_to_csv(x_csv, _x, ["x", "vals"])


def write_xbpg(states, x_csv, ind):
    _k = [int(k) for k in states.keys()]
    # _v = [str(v) for v in states.values()]
    _v = [v for v in states.values()]

    # if ind_1 != None and ind_2 != None:
    #     lKey = [key for key, value in states.items() if value == ind_1][0]
    #     rKey = [key for key, value in states.items() if value == ind_2][0]
    # print(ind)
    # print(states)
    # print(_k)
    # print(_v)
    # for i in range(len(ind)):
    # ind[i] = str(ind[i])
    # print(ind)
    for k in _k:
        if states[k] in ind:
            _v[k] = str(states[k])
        else:
            _v[k] = ''

    # exit(1)
    _x = np.matrix([
        _v,
        _k
    ]).getT()

    list_to_csv(x_csv, _x, ["x", "vals"])


def write_t(T, nt, t_csv, count=10, precision=3):
    _t = np.matrix([
        np.round(np.linspace(0, T, count + 1), precision),
        np.round(np.linspace(0, nt, count + 1), precision)
    ]).getT()

    list_to_csv(t_csv, _t, ["y", "vals"])


def mkdir(newpath):
    if not os.path.exists(newpath):
        os.makedirs(newpath)

# def print_error(err_msg, cf):
#     filename = getframeinfo(cf).filename

#     print("\033[1;31;1mError:\033[1;32;0m", end=" ")
#     print(err_msg, end="\n\n")

#     print("\033[1;33;1mFile:\033[1;32;0m", end=" ")
#     print("\"", filename, "\"", sep="")

#     print("\033[1;33;1mLine:\033[1;32;0m", end=" ")
#     print(cf.f_lineno)

#     print()

#     return
