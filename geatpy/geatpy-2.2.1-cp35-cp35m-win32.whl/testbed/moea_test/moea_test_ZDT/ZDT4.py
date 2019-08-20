# -*- coding: utf-8 -*-
import numpy as np
import geatpy as ea

class ZDT4(ea.Problem): # 继承Problem父类
    def __init__(self):
        name = 'ZDT4' # 初始化name（函数名称，可以随意设置）
        M = 2 # 初始化M（目标维数）
        maxormins = [1] * M # 初始化maxormins（目标最小最大化标记列表，1：最小化该目标；-1：最大化该目标）
        Dim = 10 # 初始化Dim（决策变量维数）
        varTypes = [0] * Dim # 初始化varTypes（决策变量的类型，0：实数；1：整数）
        lb = [0] + [-5] * (Dim - 1) # 决策变量下界
        ub = [1] + [5] * (Dim - 1) # 决策变量上界
        lbin = [1] * Dim # 决策变量下边界
        ubin = [1] * Dim # 决策变量上边界
        # 调用父类构造方法完成实例化
        ea.Problem.__init__(self, name, M, maxormins, Dim, varTypes, lb, ub, lbin, ubin)
    
    def aimFunc(self, pop): # 目标函数
        Vars = pop.Phen # 得到决策变量矩阵
        ObjV1 = Vars[:, 0]
        Vars1_10 = Vars[:, 1:10]
        gx = 1 + 10 * (self.Dim - 1) + np.sum(Vars1_10**2 - 10 * np.cos(4 * np.pi * Vars1_10), 1)
        hx = 1 - np.sqrt(ObjV1 / gx)
        ObjV2 = gx * hx
        pop.ObjV = np.array([ObjV1, ObjV2]).T # 把结果赋值给ObjV
    
    def calBest(self): # 计算全局最优解
        N = 10000 # 生成10000个参考点
        ObjV1 = np.linspace(0, 1, N)
        ObjV2 = 1 - np.sqrt(ObjV1)
        globalBestObjV = np.array([ObjV1, ObjV2]).T
        
        return globalBestObjV
    