# -*- coding: utf-8 -*-
from itertools import groupby


def get_rs_range_list(rs_port_list):
    ret_list = []
    lst = sorted(rs_port_list)  # 连续数字
    fun = lambda x: x[1] - x[0]
    for k, g in groupby(enumerate(lst), fun):
        l1 = [j for i, j in g]  # 连续数字的列表
        if len(l1) > 1:
            scop = str(min(l1)) + '-' + str(max(l1))  # 将连续数字范围用"-"连接
        else:
            scop = l1[0]
        ret_list.append(str(scop))
    return ret_list


if __name__ == "__main__":
    lst = [1231, 23333, 23334, 23335, 23337]
    ret_list = get_rs_range_list(lst)
    print(ret_list)