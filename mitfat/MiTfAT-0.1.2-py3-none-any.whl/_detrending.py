#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 11:01:06 2019

@author: vbokharaie

This module includes methods of fmri_dataset class used for detrending.

"""
from mitfat import _Lib
__methods__ = [] # self is a DataStore
register_method = _Lib.register_method(__methods__)

#%%
@register_method
def detrend(self):
    """Detrending the time-series.
    When cutoff times are set merely to begining and end times:
        spline-smooth the time-series, and subtract it from the original signal.
    For three segments:
        Fits a spline to first and third time-segments.
        Interpolates the second segment, and subtract it from the original time-series values.
        In doing so, chnages in the signal trend in segment 2 becomes evident.


    Saves detrended plots, saved in png and optionaly eps format.
    Saves bar plots of detrended time segments, saved in png and optionaly eps format
    Saves an .xlsx file including values of detrended signals
    """
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import os

    from mitfat import flags

    cluster_labels, cluster_centroids = self.cluster_hierarchial()
    cluster_centroids_0 = cluster_centroids[0, :]
    first_cent_el = cluster_centroids_0[0]
    cluster_centroids = cluster_centroids/first_cent_el
    cluster_centroids_0 = cluster_centroids_0/first_cent_el
    x_new = self.data_hierarchical
    x_new = x_new/first_cent_el
#    time_stepsrain_cluster0 = x_new[cluster_labels == 0, :]


    from scipy.interpolate import splrep, splev
    time_steps = self.time_steps
    y_t = cluster_centroids_0
    indices_cutoff = self.indices_cutoff
    dir_save_main = self.dir_save
    dir_save_subfolder = os.path.join(dir_save_main, '03_detrending_raw')
    if not os.path.exists(dir_save_subfolder):
        os.makedirs(dir_save_subfolder)

    column_names = ['Time', 'representtaive_signal', 'spline_seg_1_2_3',\
                    'detrended_based_on_spline_seg_1_2_3', 'spline_seg_1_3',\
                    'detrended_based_on_spline_seg_1_3', ]
    my_index = np.arange(len(time_steps))
    df_detrended = pd.DataFrame(columns=column_names, index=my_index)
    df_detrended.at[:, 'Time'] = time_steps

    fig, ax1 = plt.subplots(nrows=1, ncols=1, sharey=True, figsize=(12, 8))
    fig.suptitle('Mean and its spline')
    ## representative signal
    ax1.plot(time_steps, y_t,\
            label='mean', color='k', lw=5, alpha=0.95)
    df_detrended.at[:, 'representtaive_signal'] = y_t
    if len(indices_cutoff) == 4:
        cps = time_steps[indices_cutoff[1:-1]]

        k = 3
        smooth = 1
        ind_seg1 = list(np.arange(indices_cutoff[1]))
        ind_seg3 = list(np.arange(indices_cutoff[2], indices_cutoff[3]))
        ind_seg1_3 = ind_seg1 + ind_seg3
        x_seg1_3 = time_steps[ind_seg1_3]
        y_seg1_3 = y_t[ind_seg1_3]
        spl = splrep(x_seg1_3, y_seg1_3, s=smooth, k=k)

#            y2_all = splev(x_seg1_3, spl)
#            ax1.plot(x_seg1_3, y2_all,\
#                    label ='spline with s='+str(s), color='r', lw = 5,\
#                    alpha = 0.5, linestyle='--')
        y_hat_seg1_3 = splev(time_steps, spl)
        ## seg1_3 smoothed
        ax1.plot(time_steps, y_hat_seg1_3,\
                label='spline with s='+str(smooth), color='r', lw=5,\
                alpha=0.5, linestyle='-')
        df_detrended.at[:, 'spline_seg_1_3'] = y_hat_seg1_3
        df_detrended.at[:, 'detrended_based_on_spline_seg_1_3'] = y_t-y_hat_seg1_3


        x_seg1 = time_steps[ind_seg1]
        y_seg1 = y_t[ind_seg1]
        spl = splrep(x_seg1, y_seg1, s=smooth, k=k)
#            y2_all = splev(x_seg1, spl)

#            ax1.plot(x_seg1, y2_all,\
#                    label ='spline with s='+str(s), color='g', lw = 5,\
#                    alpha = 0.5, linestyle='--')
        x_seg3 = time_steps[ind_seg3]
        y_seg3 = y_t[ind_seg3]
        spl = splrep(x_seg3, y_seg3, s=smooth, k=k)
#            y2_all = splev(x_seg3, spl)
#            ax1.plot(x_seg3, y2_all,\
#                    label ='spline with s='+str(s), color='g', lw = 5,\
#                    alpha = 0.5, linestyle='--')

        knot_multiplicity = 1
        epsilon_ = 0.0001

        if cps.shape[0] == 2:
            if knot_multiplicity == 1:
                knots = np.array([cps[0], cps[0]+epsilon_, cps[0]+2*epsilon_, cps[1], \
                                  cps[1]+epsilon_, cps[1]+2*epsilon_])
            elif knot_multiplicity == 2:
                knots = np.array([cps[0], cps[0]+epsilon_, cps[1], cps[1]+epsilon_])
            elif knot_multiplicity == 3:
                knots = np.array([cps[0], cps[1]])
    smooth = 1
    k = 3
    #knots=[]################!!!!!!!!!!
    try:
        spl = splrep(time_steps, y_t, task=-1, t=knots, k=k)
    except:
        spl = splrep(time_steps, y_t, s=smooth, k=k)

    ## spline seg_1_2_3
    y2_t = splev(time_steps, spl)
    if len(indices_cutoff) == 2:
        ax1.plot(time_steps, y2_t,\
        label='spline with s='+str(smooth), color='r', lw=5,\
        alpha=0.5, linestyle='-')

#        ax1.plot(time_steps, y2_t,\
#                label ='spline', color='y_t', lw = 5, alpha = 0.5,\
#                linestyle='-')
    df_detrended.at[:, 'spline_seg_1_2_3'] = y2_t
    df_detrended.at[:, 'detrended_based_on_spline_seg_1_2_3'] = y_t-y2_t

    filename_csv = os.path.join(dir_save_subfolder, 'spline_detrended_signals.xlsx')
    df_detrended.to_excel(filename_csv, index=False)

    for cc_t in np.arange(len(indices_cutoff)):
        ax1.axvline(x=time_steps[indices_cutoff[cc_t]], color='k',\
                      linestyle='--', linewidth=1) # vertical lines
    ax1.set_xticks(time_steps[indices_cutoff])
    ax1.grid(True)
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right')

    filename_bb = os.path.join(dir_save_subfolder, 'mean_and_splines')
    fig.savefig(filename_bb+'.png', dpi=100, figsize=(16.0, 10.0), format='png')
    if flags.if_save_eps:
        fig.savefig(filename_bb+'.eps', transparent=False,
                    dpi=100, figsize=(16.0, 10.0), format='eps')

    ####
    fig, ax1 = plt.subplots(nrows=1, ncols=1, sharey=True, figsize=(12, 8))
    fig.suptitle('Mean detrended (using spline)')
    if len(indices_cutoff) == 4:
        ax1.plot(time_steps, y_t-y_hat_seg1_3,\
                label='mean detrended', color='k', lw=5, alpha=0.95)
#        ax1.plot(time_steps, y2_t-y_hat_seg1_3,\
#                label ='mean detrended', color='b', lw = 5, alpha = 0.3)
        ax1.plot(time_steps, np.zeros(time_steps.shape),\
                color='b', lw=5, alpha=0.95, linestyle='--')

        for cc_t in np.arange(len(indices_cutoff)):
            ax1.axvline(x=time_steps[indices_cutoff[cc_t]], color='k',\
                          linestyle='--', linewidth=1) # vertical lines
        ax1.set_xticks(time_steps[indices_cutoff])
        ax1.set_ylim([-.1, .1])
        ax1.grid(True)
        handles, labels = ax1.get_legend_handles_labels()
        fig.legend(handles, labels, loc='upper right')

        filename_bb = os.path.join(dir_save_subfolder, 'mean_detrnded')
        fig.savefig(filename_bb+'.png', dpi=100, figsize=(16.0, 10.0), format='png')
        if flags.if_save_eps:
            fig.savefig(filename_bb+'.eps', transparent=False, \
                        dpi=100, figsize=(16.0, 10.0), format='eps')

    ####
    fig, ax1 = plt.subplots(nrows=1, ncols=1, sharey=True, figsize=(12, 8))
    fig.suptitle('Mean splined then detrended (using spline)')
#        ax1.plot(time_steps, y_t-y_hat_seg1_3,\
#                label ='mean detrended', color='k', lw = 5, alpha = 0.95)
    if len(indices_cutoff) == 4:
        ax1.plot(time_steps, y_t-y_hat_seg1_3,\
                label='mean detrended', color='b', lw=5, alpha=0.3)
    else:
        ax1.plot(time_steps, y_t-y2_t,\
                label='mean detrended', color='b', lw=5, alpha=0.3)

    ax1.plot(time_steps, np.zeros(time_steps.shape),\
            color='b', lw=5, alpha=0.95, linestyle='--')

    for cc_t in np.arange(len(indices_cutoff)):
        ax1.axvline(x=time_steps[indices_cutoff[cc_t]], color='k',\
                      linestyle='--', linewidth=1) # vertical lines
    ax1.set_xticks(time_steps[indices_cutoff])
    ax1.set_ylim([-.1, .1])
    ax1.grid(True)
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right')

    filename_bb = os.path.join(dir_save_subfolder, 'mean_splined_detrnded')
    fig.savefig(filename_bb+'.png', dpi=100, figsize=(16.0, 10.0), format='png')
    if flags.if_save_eps:
        fig.savefig(filename_bb+'.eps', transparent=False, dpi=100, figsize=(16.0, 10.0), format='eps')

    ### saving mean value of each segment to excel file
    if len(indices_cutoff) == 4:
        ind_seg1 = list(np.arange(indices_cutoff[1]))
        ind_seg2 = list(np.arange(indices_cutoff[1], indices_cutoff[2]))
        ind_seg3 = list(np.arange(indices_cutoff[2], indices_cutoff[3]))
        my_signal = y_t-y_hat_seg1_3
        filename_txt = os.path.join(dir_save_subfolder, 'detrended_signal.txt')
        np.savetxt(filename_txt, my_signal, delimiter='\n')
        my_signal_seg1 = my_signal[ind_seg1]
        my_signal_seg2 = my_signal[ind_seg2]
        my_signal_seg3 = my_signal[ind_seg3]
        mean1 = np.nanmean(my_signal_seg1)
        mean2 = np.nanmean(my_signal_seg2)
        mean3 = np.nanmean(my_signal_seg3)
        text_file = 'segment_mean.txt'
        text_file = os.path.join(dir_save_main, text_file)
        out_file = open(text_file, "a")
        dataset_name = self.experiment_name
        my_string = dataset_name+'\t'+str(mean1)+'\t'+str(mean2)+'\t'+str(mean3)
        out_file.write(my_string + '\n')
        out_file.close()
        ind = np.arange(3)
        fig, ax1 = plt.subplots(nrows=1, ncols=1, sharey=True, figsize=(12, 8))
        fig.suptitle('Mean values of detrended signal in each segment')
        colours_for_cat = ['#f43605', '#fcc006', '#89a203', '#047495', '#030764', '#c071fe',\
                       '#db5856', '#0cdc73', '#fbdd7e', '#e78ea5']

        try:
            ax1.bar(ind, [mean1, mean2, mean3], color=colours_for_cat)
            ax1.set_ylim([-.05, .02])
            ax1.grid(True)

        except TypeError:
            print('Bar plot of cluster Centroides could not be printed')
        filename_bb = os.path.join(dir_save_subfolder, 'bar_plot_mean_detrnded')
        fig.savefig(filename_bb+'.png', dpi=100, figsize=(16.0, 10.0), format='png')
        if flags.if_save_eps:
            fig.savefig(filename_bb+'.eps', transparent=False,\
                        dpi=100, figsize=(16.0, 10.0), format='eps')

    else:
        filename_txt = os.path.join(dir_save_subfolder, 'difference_to_smoothed_signal.txt')
        np.savetxt(filename_txt, y_t-y2_t, delimiter='\n')

    plt.close('all')
