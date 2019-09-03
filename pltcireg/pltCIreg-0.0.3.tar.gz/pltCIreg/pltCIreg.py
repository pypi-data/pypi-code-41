# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 23:59:12 2019

@author: zhedashen
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def tworegCI(data, data0, xlim = None, ylim = None, legloc = 'best', xlab = None
             ,ylab = None, leglab = ['a', 'b'], figsz = None):
    
    """Data preparation1"""
    #data = [[0, 1, 2, 3],  # x variable (quantile)
    #        [2, 3, 4, 5],  # y variable (x effect)
    #        [1.5, 2, 3, 3],  #  low CI
    #        [2.5, 4, 5, 7]]  #  upper CI
    data = np.array(data).T
    predict_mean_ci_low, predict_mean_ci_upp = data[:, 2:].T  #summary_table
    
    # 创建置信区间DataFrame，上下界
    CI_df = pd.DataFrame(columns = ['x_data', 'low_CI', 'upper_CI'])
    CI_df['x_data'] = data[:, 0]  
    CI_df['low_CI'] = predict_mean_ci_low
    CI_df['upper_CI'] = predict_mean_ci_upp
    CI_df.sort_values('x_data', inplace = True) # 根据x_data进行排序
    
    x_data = data[:, 0]  
    y_data = data[:, 1] 
    sorted_x = CI_df['x_data']
    low_CI = CI_df['low_CI']
    upper_CI = CI_df['upper_CI']


    """Data preparation2"""
    #data0 = [[0, 1, 2, 3],  # x variable (quantile)
    #         [3, 3, 3, 3],  # y variable (x effect)
    #         [2, 2, 2, 2],  #  low CI
    #         [4, 4, 4, 4]]  #  upper CI
    data0 = np.array(data0).T
    predict_mean_ci_low0, predict_mean_ci_upp0 = data0[:, 2:].T  #summary_table
    CI_df0 = pd.DataFrame(columns = ['x_data', 'low_CI', 'upper_CI'])
    CI_df0['x_data'] = data0[:, 0]  
    CI_df0['low_CI'] = predict_mean_ci_low0
    CI_df0['upper_CI'] = predict_mean_ci_upp0
    CI_df0.sort_values('x_data', inplace = True) # 根据x_data进行排序
    
    x_data0 = data0[:, 0]  
    y_data0 = data0[:, 1] 
    sorted_x0 = CI_df0['x_data']
    low_CI0 = CI_df0['low_CI']
    upper_CI0 = CI_df0['upper_CI']
    
    #########Figure        
    try:
        plt.figure(figsize=(figsz[0], figsz[1]), dpi=figsz[2])
    except:
        pass

    '''Plot'''
    plt.plot(x_data, y_data, lw = 1, color = '#0257cc', alpha = 1, label = leglab[0])
    # 绘制置信区间，顺序填充
    plt.fill_between(sorted_x, low_CI, upper_CI, color = '#539caf', alpha = 0.4)   
    
    # 绘制预测曲线
    plt.plot(x_data0, y_data0, lw = 1, color = '#815d07', alpha = 1, label = leglab[1])
    # 绘制置信区间，顺序填充
    plt.fill_between(sorted_x0, low_CI0, upper_CI0, color = '#c99d49', alpha = 0.4) 
    
    ftsize = 14
    fam = 'Times New Roman'
    plt.xlabel(xlab, fontsize = ftsize, family = fam)
    plt.ylabel(ylab, fontsize = ftsize, family = fam)
    plt.xticks(10 * np.arange(1, 10, 2))
    plt.xlim(xlim[0], xlim[1])
    try:
        plt.ylim(ylim[0], ylim[1])
    except:
       pass
    plt.xticks(fontsize = ftsize, family = fam)  # 设置刻度字体大小
    plt.yticks(fontsize = ftsize, family = fam)
    
    font1 = {'family' : 'Times New Roman',
    'weight' : 'normal',
    'size'   : 14}
    plt.legend(loc = legloc, fontsize = ftsize, prop = font1)
    plt.show()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    