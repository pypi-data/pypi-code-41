# import numpy as np
import autograd.numpy as np
import scipy.io
from scipy.stats import t
from scipy.stats import norm
# import matplotlib.pyplot as plt
import pandas as pd
import autograd as grad

# global likelihood_setting


def negative_log_pdf_fun(mus, other_val, ydata_sub):

    likelihood_case = 1
    if likelihood_case == 1:
        total_mu_vec = mus+other_val

        super_mu_vec = np.sum(total_mu_vec[ydata_sub==0])
        numerator_log = (-super_mu_vec)
        denominator_log = np.sum(np.log(1+np.exp(-total_mu_vec)))

    return -numerator_log+denominator_log

# def Hamitonian_MC_Sampler(leapfrog_stepsize, leapfrog_num, mus, other_val, ydata_sub):
#     p_gradient = grad(negative_log_pdf_fun)
#     pp = np.random.rand()
#
#     pp = pp - leapfrog_stepsize*p_gradient(mus, other_val, ydata_sub)/2
#     for jj in range(leapfrog_num):
#         mus = mus + leapfrog_stepsize*pp
#         if jj <(leapfrog_num-1):
#             pp = pp - leapfrog_stepsize*p_gradient(mus, other_val, ydata_sub)/2
#     pp = pp - leapfrog_stepsize*p_gradient(mus, other_val, ydata_sub)/2
#
#     return mus, pp


#
# def random_effects_synthetic_data_gen(dataNum, dimNum, x_range, data_genrate_indicator, noise_level, group_numbers):
#
#     xdata_seq = []
#     ydata_seq = []
#     alpha_level = norm.rvs(loc=0, scale = 4, size=len(group_numbers))
#
#     for [datai, alpha_i] in zip(group_numbers, alpha_level):
#         noiseNess = [0.3, 0.7]
#         if dimNum == 1:
#             # print x_range
#             # xdata = np.arange(x_range[0], x_range[1], (x_range[1]-x_range[0])/dataNum)
#             xdata = np.arange(x_range[0], x_range[1], (x_range[1]-x_range[0])/datai)
#             dataNums = len(xdata)
#             noisess = np.random.randn(dataNums)*noiseNess[noise_level]
#
#             if data_genrate_indicator == 0:
#                 ydata = xdata**3 + noisess
#             elif data_genrate_indicator == 1:
#                 ydata = np.sin(8*np.pi*xdata) + noisess
#             elif data_genrate_indicator == 2:
#                 ydata = np.ones(len(xdata))
#                 ydata[xdata<0] = -1
#                 ydata = ydata + noisess
#             elif data_genrate_indicator == 3: # assume label number is 2
#                 inteception_points = np.sort(np.random.uniform(low=-0.99, high = 0.99, size = 7))
#                 ydata = np.ones(len(xdata))
#                 ydata[(inteception_points[0]<=xdata)&(xdata<inteception_points[1])] = 0
#                 ydata[(inteception_points[2]<=xdata)&(xdata<inteception_points[3])] = 0
#                 ydata[(inteception_points[4]<=xdata)&(xdata<inteception_points[5])] = 0
#                 ydata[inteception_points[6]<=xdata] = 0
#             elif data_genrate_indicator == 4: # this is the logit curve function: y=1/(1+exp(-x))
#                 yprob = 1/(1+np.exp(-10*xdata))
#                 ydata = (np.random.rand(len(xdata))<yprob)
#         else:
#             xdata = np.random.uniform(low = x_range[0],high = x_range[1], size = [dataNums, dimNum])
#             ydata = np.sum(xdata**3, axis = 1) + np.random.randn(dataNums)*noiseNess
#         ydata = ydata + alpha_i
#         xdata_seq.append(xdata)
#         ydata_seq.append(ydata)
#     return ydata_seq, xdata_seq
#
#
# def synthetic_data_gen(dataNum, dimNum, x_range, data_genrate_indicator, noise_level):
#     noiseNess = [0.3, 0.7]
#     if dimNum == 1:
#         # print x_range
#         # xdata = np.arange(x_range[0], x_range[1], (x_range[1]-x_range[0])/dataNum)
#         xdata = np.arange(x_range[0], x_range[1], 0.01)
#         noisess = np.random.randn(dataNum)*noiseNess[noise_level]
#
#         if data_genrate_indicator == 0:
#             ydata = xdata**3 + noisess
#         elif data_genrate_indicator == 1:
#             ydata = np.sin(8*np.pi*xdata) + noisess
#         elif data_genrate_indicator == 2:
#             ydata = np.ones(len(xdata))
#             ydata[xdata<0] = -1
#             ydata = ydata + noisess
#         elif data_genrate_indicator == 3: # assume label number is 2
#             inteception_points = np.sort(np.random.uniform(low=-0.99, high = 0.99, size = 7))
#             ydata = np.ones(len(xdata))
#             ydata[(inteception_points[0]<=xdata)&(xdata<inteception_points[1])] = 0
#             ydata[(inteception_points[2]<=xdata)&(xdata<inteception_points[3])] = 0
#             ydata[(inteception_points[4]<=xdata)&(xdata<inteception_points[5])] = 0
#             ydata[inteception_points[6]<=xdata] = 0
#         elif data_genrate_indicator == 4: # this is the logit curve function: y=1/(1+exp(-x))
#             yprob = 1/(1+np.exp(-10*xdata))
#             ydata = (np.random.rand(len(xdata))<yprob)
#     else:
#         xdata = np.random.uniform(low = x_range[0],high = x_range[1], size = [dataNum, dimNum])
#         ydata = np.sum(xdata**3, axis = 1) + np.random.randn(dataNum)*noiseNess
#     return ydata, xdata

def tree_stage_cut(dts_star, stage_i):
    if stage_i < len(dts_star.candidate_set):
        dts_star.treev = dts_star.treev[:(dts_star.nodeNumseq[stage_i]+1), ]
        condition_judge = dts_star.treev[:, 1] > dts_star.treev[-1, 0]

        dts_star.treev[condition_judge, 1] = 0
        dts_star.treev[condition_judge, 2] = 0
        dts_star.treev[condition_judge, 3] = 0
        dts_star.treev[condition_judge, 4] = 0

        dts_star.treebound_lower = dts_star.treebound_lower[:(dts_star.nodeNumseq[stage_i]+1), :]
        dts_star.treebound_upper = dts_star.treebound_upper[:(dts_star.nodeNumseq[stage_i]+1), :]
        dts_star.candidate_set = dts_star.candidate_set[:(stage_i+1)]
        dts_star.nodeNumseq = dts_star.nodeNumseq[:(stage_i+1)]
        dts_star.cut_prior = dts_star.cut_prior[:(stage_i)]
        dts_star.cut_proposal = dts_star.cut_proposal[:(stage_i)]
    return dts_star

def non_increasing(L):
    return all(x>=y for x, y in zip(L, L[1:]))

def non_decreasing(L):
    return all(x<=y for x, y in zip(L, L[1:]))

def index_judge(current_lower, current_upper, xdata):
    if xdata.ndim==1:
        return np.where(((current_lower <= xdata) * (current_upper > xdata)).astype(bool))
    else:
        return np.where((np.prod(current_lower<=xdata, axis=1)*np.prod(current_upper>xdata, axis=1)).astype(bool))


# def auto_corr(M):
# #   The autocorrelation has to be truncated at some point so there are enough
# #   data points constructing each lag. Let kappa be the cutoff
#     kappas = len(M)
#     auto_corrval = np.zeros(kappas-30)
#     mu = np.mean(M)
#     for s in range(1,kappas-30):
#         # auto_corrval[s] = np.corrcoef(M[:-s],M[s:])[0, 1]
#         # auto_corrval[s] = np.sum((M[:-s]-mu)*(M[s:]-mu))/np.sum((M-mu)*(M-mu))
#         auto_corrval[s] = np.mean((M[:-s]-mu) * (M[s:]-mu)) / np.var(M)
#     return auto_corrval, 1+2*np.sum(auto_corrval)
#
# def auto_corr_1(M):
# #   The autocorrelation has to be truncated at some point so there are enough
# #   data points constructing each lag. Let kappa be the cutoff
#     kappas = len(M)
#     auto_corrval = np.zeros(kappas-30)
#     mu = np.mean(M)
#     for s in range(1,kappas-30):
#         auto_corrval[s] = np.corrcoef(M[:-s],M[s:])[0, 1]
#         # auto_corrval[s] = np.mean( (M[:-s]-mu) * (M[s:]-mu) ) / np.var(M)
#     return auto_corrval, 1+2*np.sum(auto_corrval)
#
# def auto_corr_2(M):
# #   The autocorrelation has to be truncated at some point so there are enough
# #   data points constructing each lag. Let kappa be the cutoff
#     kappas = len(M)
#     auto_corrval = np.zeros(kappas-30)
#     mu = np.mean(M)
#     for s in range(1,kappas-30):
#         covval = np.cov(np.vstack((M[:-s],M[s:])))
#         varval1 = np.var(M[:-s],M[s:])
#         varval2 = np.cov(M[:-s],M[s:])
#         auto_corrval[s] = covval[0, 1]/((varval1**(0.5))*(varval2**(0.5)))
#     return auto_corrval, 1+2*np.sum(auto_corrval)


# def read_data():
#     datafile = 'boston/boston_data.csv'
#     vals = pd.read_csv(datafile, header = 0)
#     xydata = vals.values
#     xyxy = xydata[np.arange(1, len(xydata), 2)]
#     ydata = xyxy[:, -1]
#     xdata = xyxy[:, :(-1)]
#     return ydata, xdata
#
# def autocorr(x):
#     result = np.correlate(x, x, mode='full')
#     return result[np.ceil(result.size/2.0).astype(int):]