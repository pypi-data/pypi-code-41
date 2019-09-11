import numpy as np
import scipy.io
# import matplotlib.pyplot as plt
import os
import pandas as pd
# from pandas.plotting import autocorrelation_plot



from .utility import *
from .p_class import *



def BART_M(ydata, xdata, IterationTime = 100, mTree = 50, alphav = 0.95, betav = 2, particleNUm = 10, likelihood_setting = 0):

    dataNum = xdata.shape[0]
    dimNum = xdata.shape[1]

    # global likelihood_setting
    noise_name_file = ['small normal noise', 'large normal noise', 'logistic regression']
    likelihood_function_file = ['cubic function', 'sine function', 'indicator function', 'logistic binary regression', 'logit curve function']
    noise_setting = 2 # 0: normal distributed likelihood; 1: t distributed likelihood; 2: logistic regression likelihood
    likelihood_setting_seq = [3] # 0; cubic function; 1: since function; 2, indicator function; 3, logistic binary regression
    noise_level_seq = [2]


    noise_level = 0


    x_range = np.array([-1, 1])

    maxStage = 100
    dataflag = 1
    # if dataflag == 1:
    #     ydata, xdata = synthetic_data_gen(dataNum, dimNum, x_range, likelihood_setting, noise_level)
    # elif dataflag == 2:
    #     ydata,xdata = read_data()
    mus = np.mean(ydata)

    sigmas = np.std(ydata)


    constraintIndicator = False

    add_dts_v = add_dts(mTree, constraintIndicator, mus, sigmas, maxStage, alphav, betav, dimNum, xdata, ydata, noise_setting)
    predicted_y = np.zeros([IterationTime, add_dts_v.mTree, len(ydata)])
    predicted_mu = np.zeros([IterationTime, add_dts_v.mTree, 4])
    posterior_x = np.arange(-1, 1, 0.01)
    posterior_mean = np.zeros([add_dts_v.mTree, len(posterior_x)])
    posterior_var = np.zeros(IterationTime)
    for itei in range(IterationTime):
        add_dts_v.updates(particleNUm, maxStage, xdata, ydata, alphav, betav, dimNum)

        if add_dts_v.noise_setting != 2:
            add_dts_v.hyper_sigma_update(xdata, ydata)
        if np.remainder(itei, 100)==0:
            print(str(itei)+'-th iteration has finished. \n')

        total_val_mat = np.zeros([add_dts_v.mTree, len(xdata)])
        mu_val_mat = np.zeros([add_dts_v.mTree, 4])
        for mi in range(add_dts_v.mTree):
            total_val_mat[mi] = add_dts_v.add_dts[mi].assign_to_data(xdata, add_dts_v.add_dts[mi].nodeNumseq[-1])
            mu_val_mat[mi] = add_dts_v.add_dts[mi].assign_to_data(np.array([-0.9, -0.4, 0.1, 0.6]), add_dts_v.add_dts[mi].nodeNumseq[-1])

        predicted_y[itei] = total_val_mat
        predicted_mu[itei] = mu_val_mat

        posterior_var[itei] = add_dts_v.true_var
    for mi in range(add_dts_v.mTree):
        posterior_mean[mi] = add_dts_v.add_dts[mi].assign_to_data(posterior_x,add_dts_v.add_dts[mi].nodeNumseq[-1])
    posterior_mean_val = np.sum(posterior_mean, axis=0)


    # discard the burn-in stage
    remain_predicted_y = predicted_y[np.ceil(IterationTime/2).astype(int):]

    sum_predicted_y = np.sum(remain_predicted_y, axis=1)
    sqe = np.var(sum_predicted_y - ydata, axis = 1)


    remain_predicted_mu = predicted_mu[np.ceil(IterationTime/2).astype(int):]
    sum_predicted_mu = np.sum(remain_predicted_mu, axis=1)

    remain_posterior_var = posterior_var[np.ceil(IterationTime/2).astype(int):]
    boxplot_data = np.concatenate((sum_predicted_mu, sqe.reshape((-1, 1)), remain_posterior_var.reshape((-1, 1))), axis = 1)


