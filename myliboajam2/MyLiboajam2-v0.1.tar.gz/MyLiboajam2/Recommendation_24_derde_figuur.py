import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import matplotlib.pyplot as plt
from statsmodels.sandbox.regression.predstd import wls_prediction_std
from statsmodels.iolib.table import (SimpleTable, default_txt_fmt)
np.random.seed(1024)
from scipy.optimize import curve_fit
import os


# Data_All = pd.read_csv("Input/dataset_fixed_201209-201809_all.csv")
# Data_FIRP15 = pd.read_csv("Input/dataset_fixed_201209-201809_firp1to5.csv")
# Data_FIRP11_20 = pd.read_csv("Input/dataset_fixed_201209-201809_firp11to20.csv")
# Data_FIRP6_10 = pd.read_csv("Input/dataset_fixed_201209-201809_firp6to10.csv")
# Data_FIRP6_10_nozero = pd.read_csv("Input/dataset_fixed_201209-201809_firp6to10_nozero.csv")
WDCurrent = os.getcwd()
#Data_All = pd.read_csv("Input/Data_as_CBR_2018v14_original.csv")
Data_All = pd.read_csv("Input/Received0829/Input.csv")


#Incentive_buckets_bounds = np.round(np.append(np.arange(-0.02,0.04,0.004),0.04),4)

Incentive_buckets_bounds = np.round(np.append(np.arange(-0.01,0.02,0.01),0.02),3)
print(Incentive_buckets_bounds)
for i in range(len(Incentive_buckets_bounds)):
    # if i==0:
    #     continue
    # if Incentive_buckets_bounds[i]==-1.6:
    #     Data_All[str(i)] = Data_All['Incentive']<Incentive_buckets_bounds[i]
    # if Incentive_buckets_bounds[i]==3.6:
    #     Data_All[str(i)] = Data_All['Incentive'] >= Incentive_buckets_bounds[i]
    # else:
    #     Data_All[str(i)] = (Incentive_buckets_bounds[i-1] <= Data_All['Incentive']) & (Data_All['Incentive'] < Incentive_buckets_bounds[i])

    if i==0:
        continue
    if i==1:
        Data_All[str(i)] = Data_All['Incentive']<Incentive_buckets_bounds[i]
    if i==len(Incentive_buckets_bounds)-2:
        Data_All[str(i)] = Data_All['Incentive'] >= Incentive_buckets_bounds[i]
    else:
        Data_All[str(i)] = (Incentive_buckets_bounds[i-1] <= Data_All['Incentive']) & (Data_All['Incentive'] < Incentive_buckets_bounds[i])




Segment_str = 'Fixed - FIRP1to5'
DataUsed_incentives_1 = Data_All[Data_All['1']]
DataUsed_incentives_2 = Data_All[Data_All['2']]
DataUsed_incentives_3 = Data_All[Data_All['3']]

# ParamsTMD_Used = ParamsTMD_FIRP1_5
#DataUsed_11plus = Data_All[(Data_All['Description']== 'Fixed - FIRP11to20') | (Data_All['Description']== 'Fixed - FIRP21to25') | (Data_All['Description']== 'Fixed - FIRP26+')]
print("hoi")


def PrepFunction(x, a, b, c, d):
    return a + b / (1 + np.exp(c + d * x))

# ColumnNames = DataUsed_11plus.columns.values
Weights_values_incentives_1 = DataUsed_incentives_1['Volume']
y_values_incentives_1 = DataUsed_incentives_1['Observed value']
X_values_incentives_1 = DataUsed_incentives_1['Incentive']

Weights_values_incentives_2 = DataUsed_incentives_2['Volume']
y_values_incentives_2 = DataUsed_incentives_2['Observed value']
X_values_incentives_2 = DataUsed_incentives_2['Incentive']

Weights_values_incentives_3 = DataUsed_incentives_3['Volume']
y_values_incentives_3 = DataUsed_incentives_3['Observed value']
X_values_incentives_3 = DataUsed_incentives_3['Incentive']

# try:
#     popt_1to5, pcov_1to5 = curve_fit(PrepFunction, X_values_1to5, y_values_1to5, sigma=1. / Weights_values_1to5, absolute_sigma=True,
#                            bounds=([-1000, -1000, -1000, -1000], [1000, 1000, 1000, 0]))
#     NoFitFound_weighted_1to5 = False
# except:
#     popt_1to5 = [0,0,0,0]
#     NoFitFound_weighted_1to5 = True
#
# try:
#     popt_6to15, pcov_6to15 = curve_fit(PrepFunction, X_values_6to15, y_values_6to15, sigma=1. / Weights_values_6to15, absolute_sigma=True,
#                            bounds=([-1000, -1000, -1000, -1000], [1000, 1000, 1000, 0]))
#     NoFitFound_weighted_6to15 = False
# except:
#     popt_6to15 = [0,0,0,0]
#     NoFitFound_weighted_6to15 = True

# try:
#     popt_16plus, pcov_16pus = curve_fit(PrepFunction, X_values_16plus, y_values_16plus,
#                                        sigma=1. / Weights_values_16plus, absolute_sigma=True,
#                                        bounds=([-1000, -1000, -1000, -1000], [1000, 1000, 1000, 0]))
#     NoFitFound_weighted_16plus = False
# except:
#     popt_16plus = [0, 0, 0, 0]
#     NoFitFound_weighted_16plus = True


# X_values_sorted_1to5 = X_values_1to5.copy().sort_values()
# if not NoFitFound_weighted_1to5:
#     plt.plot(X_values_sorted_1to5, PrepFunction(X_values_sorted_1to5, *popt_1to5), color='purple', label='1to5: a=%5.3f, b=%5.3f, c=%5.3f, d=%5.3f' % tuple(popt_1to5))
#
# X_values_sorted_6to15 = X_values_6to15.copy().sort_values()
# if not NoFitFound_weighted_6to15:
#     plt.plot(X_values_sorted_6to15, PrepFunction(X_values_sorted_6to15, *popt_6to15), color='green', label='6to15: a=%5.3f, b=%5.3f, c=%5.3f, d=%5.3f' % tuple(popt_6to15))
#
# X_values_sorted_16plus = X_values_16plus.copy().sort_values()
# if not NoFitFound_weighted_6to15:
#     plt.plot(X_values_sorted_16plus, PrepFunction(X_values_sorted_16plus, *popt_16plus), color='aqua', label='16+: a=%5.3f, b=%5.3f, c=%5.3f, d=%5.3f' % tuple(popt_16plus))
#
#
# plt.scatter(X_values_1to5,y_values_1to5, s=100*Weights_values_1to5/max(Weights_values_1to5), alpha=0.3, edgecolors='b', facecolors='none')
# plt.scatter(X_values_6to15,y_values_6to15, s=100*Weights_values_6to15/max(Weights_values_6to15), alpha=0.3, edgecolors='r', facecolors='none')
# plt.scatter(X_values_16plus,y_values_16plus, s=100*Weights_values_16plus/max(Weights_values_16plus), alpha=0.3, edgecolors='y', facecolors='none')


weighted_ppr_incentives_1 = []
weighted_ppr_incentives_2 = []
weighted_ppr_incentives_3 = []
for i in range(31):
    i += 1
    # print(i)

    DataUsed_incentives_1_i = DataUsed_incentives_1[DataUsed_incentives_1['Segments_original_for_ordering']==i]
    Volume_incentives_1_i = DataUsed_incentives_1_i['Volume']
    Incentive_incentives_1_i = DataUsed_incentives_1_i['Incentive']
    ppr_incentives_1_i = DataUsed_incentives_1_i['Observed value']

    DataUsed_incentives_2_i = DataUsed_incentives_2[DataUsed_incentives_2['Segments_original_for_ordering'] == i]
    Volume_incentives_2_i = DataUsed_incentives_2_i['Volume']
    Incentive_incentives_2_i = DataUsed_incentives_2_i['Incentive']
    ppr_incentives_2_i = DataUsed_incentives_2_i['Observed value']

    DataUsed_incentives_3_i = DataUsed_incentives_3[DataUsed_incentives_3['Segments_original_for_ordering'] == i]
    Volume_incentives_3_i = DataUsed_incentives_3_i['Volume']
    Incentive_incentives_3_i = DataUsed_incentives_3_i['Incentive']
    ppr_incentives_3_i = DataUsed_incentives_3_i['Observed value']


    if DataUsed_incentives_1_i.shape[0]!=0:
        weighted_ppr_incentives_1 = np.append(weighted_ppr_incentives_1,i)
        # print(Incentive_buckets_bounds[i])
        weighted_ppr_incentives_1 = np.append(weighted_ppr_incentives_1,sum(Volume_incentives_1_i*ppr_incentives_1_i)/sum(Volume_incentives_1_i))

    if DataUsed_incentives_2_i.shape[0] != 0:
        weighted_ppr_incentives_2 = np.append(weighted_ppr_incentives_2, i)
        # print(Incentive_buckets_bounds[i])
        weighted_ppr_incentives_2 = np.append(weighted_ppr_incentives_2, sum(Volume_incentives_2_i * ppr_incentives_2_i) / sum(Volume_incentives_2_i))

    if DataUsed_incentives_3_i.shape[0] != 0:
        weighted_ppr_incentives_3 = np.append(weighted_ppr_incentives_3, i)
        # print(Incentive_buckets_bounds[i])
        weighted_ppr_incentives_3 = np.append(weighted_ppr_incentives_3, sum(Volume_incentives_3_i * ppr_incentives_3_i) / sum(Volume_incentives_3_i))




# x1,x2,y1,y2 = plt.axis()
# plt.axis((x1,x2,y1,0.15))
# plt.legend()
# # plt.title(Segment_str)
# plt.savefig('namaak figuur 6.17 van vorige validatie.png')
# plt.close()


x_values_segments_1 = DataUsed_incentives_1['Segments_original_for_ordering']
weights_1 = DataUsed_incentives_1['Volume']
y_values_ppr_1 = DataUsed_incentives_1['Observed value']

x_values_segments_2 = DataUsed_incentives_2['Segments_original_for_ordering']
weights_2 = DataUsed_incentives_2['Volume']
y_values_ppr_2 = DataUsed_incentives_2['Observed value']

x_values_segments_3 = DataUsed_incentives_3['Segments_original_for_ordering']
weights_3 = DataUsed_incentives_3['Volume']
y_values_ppr_3 = DataUsed_incentives_3['Observed value']


plt.plot()

plt.scatter(x_values_segments_1,y_values_ppr_1, s=100*weights_1/max(weights_1), alpha=0.3, edgecolors='b', facecolors='none', label ='Incentives [-0.01, 0)')
plt.scatter(x_values_segments_2,y_values_ppr_2, s=100*weights_1/max(weights_2), alpha=0.3, edgecolors='r', facecolors='none',label='Incentives [0, 0.01)')
plt.scatter(x_values_segments_3,y_values_ppr_3, s=100*weights_1/max(weights_3), alpha=0.3, edgecolors='g', facecolors='none',  label='Incentives [0.01, 0.02)')

Matrix_1 = np.reshape(weighted_ppr_incentives_1,(-1,2))
Matrix_2 = np.reshape(weighted_ppr_incentives_2,(-1,2))
Matrix_3 = np.reshape(weighted_ppr_incentives_3,(-1,2))


plt.plot(Matrix_1[:,0],Matrix_1[:,1], color="purple", label='Incentives [-0.01, 0)')
plt.plot(Matrix_2[:,0],Matrix_2[:,1], color="green", label='Incentives [0, 0.01)')
plt.plot(Matrix_3[:,0],Matrix_3[:,1], color="aqua", label='Incentives [0.01, 0.02)')

x1, x2, y1, y2 = plt.axis()
plt.axis((x1,x2, -0.015, 0.15))
plt.legend()
plt.savefig('Recommendation 24 - 3rd figure.png')
plt.close()
