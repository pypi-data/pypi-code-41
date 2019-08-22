#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 18:21:14 2019

@author: vbokharaie
"""
if_verbose = False # keep it False

if_debug = False  # keep it False

if_save_eps = False  # if save plots in .eps format. All are saved in .png format regardless if this flag.
                    # if setting it to True causes some warning messages, just ignore them.

if_fix_anomolies = True  # overshoots and undershoots casued by various sources of noise
                        # it replaces anything outside +-3 SD of the time-series MEAN with nan
if_impute = True  # use scikit-learn imput to replace nan values with float values
if_normalised = True  # divide each dataset by the maximum value of all time-series

# if_plot_basics = True  # plot normalised time-series, or raw if you do not normalise the data
# if_plot_lin_reg = True  # plots of linearised siganls, separately for each time-degment.
# if_plot_raw = True  #  plot raw time-series

# if_cluster = True  # if cluster and then dave plots for [2, ..., 9] clusters.
# if_cluster_hiararchical = True  # if hierarchical cluster and then save.

# if_detrend = True  # if detrend and save
