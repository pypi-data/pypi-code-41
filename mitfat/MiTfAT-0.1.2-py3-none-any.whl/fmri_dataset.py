#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 10:55:19 2018

@author: vbokharaie
"""
# pylint: disable=line-too-long
# pylint: disable=C0103, E1101, W0212
# %% defintion of fMRI dataset class
# This _Lib module is just a trick to distribute methods of the class over
# several modules.
from mitfat import _Lib
from mitfat import _basics
from mitfat import _plotting
from mitfat import _clustering
from mitfat import _detrending
from mitfat import file_io
@_Lib.add_methods_from(_basics)
@_Lib.add_methods_from(_plotting)
@_Lib.add_methods_from(_clustering)
@_Lib.add_methods_from(_detrending)
@_Lib.add_methods_from(file_io)
class fmri_dataset:
    """
    A class as a container for all relvant data of an fMRI recording.

    """


    #  a variable to keep track of all created objects
    total_created_objects = 0
    """ keeps track of total number of objects"""

    ###
    def __init__(self, data_masked, mask_numpy,
                time_steps,
                signal_name, indices_cutoff,
                experiment_name, dataset_no, mol_name,
                dir_source, dir_save,
                description):
        """
        Parameters
        ----------
        data_masked: 'numpy.ndarray', (N_time_steps, N_voxels)
        mask_numpy: 'numpy.ndarray', (d1, d2, d3)
        time_steps: 'list' of 'float'
        signal_name: 'str'
        indices_cuttoff: 'list' if 'int'
        experiment_name: 'str'
        dataset_no: 'int'
        mol_name: 'str'
        dir_source: 'str'
        dir_save: 'str'mask_roi_numpy
        description: 'str'
        """
        import numpy as np
        from mitfat._shapes import bbox_3d, bbox_mean, bbox_3d_seq
        from mitfat import flags

        # main variables
        self.data_raw = data_masked
        """raw data, always"""
        self.data = self.data_raw  # default: raw. Can also be normalised.
        """normalised, unless flags.if_normalise=False"""
        self.data_mean = np.nanmean(self.data, axis=0)
        """mean of each voxels"""
        self.mask = mask_numpy
        """3d mask"""
        self.time_steps = time_steps
        """flow list"""
        self.num_voxels = self.data.shape[1]
        """inti"""
        self.num_time_steps = self.data.shape[0]
        """int"""
        assert self.num_voxels == np.sum(self.mask),\
            'mask size not equal to number of voxels in data file'
        assert self.num_time_steps == len(self.time_steps),\
            'number of time-steps in data file does not match that of time file'
        # now other variables
        self.signal_name = signal_name

        self.indices_cutoff = indices_cutoff

        self.cutoff_times = [0.0]*len(indices_cutoff)
        for idx, elem in enumerate(indices_cutoff):
            self.cutoff_times[idx] = self.time_steps[elem]

        self.calc_mean_segments()

        self.experiment_name = experiment_name

        self.dataset_no = dataset_no

        self.mol_name = mol_name

        self.dir_source = dir_source

        self.dir_save = dir_save

        self.description = description

        self.data_normalised = None

        # linear regression
        self.line_reg = None

        self.line_reg_slopes = None

        self.line_reg_biases = None

        # bbox
        self.bbox_mask = bbox_3d(self.mask)

        self.bbox_data_mean = bbox_mean(self.bbox_mask, self.data)

        self.bbox_mask_seq = bbox_3d_seq(self.bbox_mask)

        # possible hiearachial clustering
        self.data_hierarchical = None

        self.bbox_mask_hierarchical = None

        #
        fmri_dataset.total_created_objects = fmri_dataset.total_created_objects + 1

        # fix anamolies, impute, normlaise
        if flags.if_fix_anomolies:
            self.fix_anomolies()

        if flags.if_impute:
            self.impute()

        if flags.if_normalised:
            self.normalise()

        self.calc_lin_reg()


# %% __main__
if __name__ == "__main__":
    # a script to test the MiTfAT code.

    from mitfat.file_io import read_data
    if_save_eps = False  # if save plots in .eps format. All are saved in .png format by default.
                        # if setting it to True casues some warning messages, just ignore them.

    if_plot_basics = True  # plot normalised time-series, or raw if you do not normalise the data
    if_plot_lin_reg = True  # plots of linearised siganls, separately for each time-degment.
    if_plot_raw = True  #  plot raw time-series

    if_cluster = True  # if cluster and then dave plots for [2, ..., 9] clusters.
    if_cluster_hiararchical = True  # if hierarchical cluster and then save.

    if_detrend = True  # if detrend and save

    # %% look at the sample_info_file.txt for info on how to setup the info.file
    info_file_name = 'sample_info_file.txt'

    # %% read the data based on the info in info_file_name
    dataset1 = read_data(info_file_name)

    # Basic plots
    if_plot_basics = False
    if_plot_lin_reg = False
    if_plot_raw = False
    if if_plot_basics:
        dataset1.plot_basics()

    if if_plot_lin_reg:
        dataset1.plot_basics('lin_reg')

    if if_plot_raw:
        dataset1.plot_basics('raw')

    if if_cluster:
        ###
        X_train = dataset1.data_normalised
        X_train_label = 'RAW_Normalised'
        print('-----------------------------------')
        print('Clustering ', X_train_label)
        for num_clusters in [2, 3, 4, 5, 6, 7, 8, 9, ]:
            print(num_clusters, 'clusters')
            cluster_labels, cluster_centroid = \
                dataset1.cluster_raw(X_train, num_clusters)
            dataset1._save_clusters(X_train, X_train_label,
                                    cluster_labels, cluster_centroid)
            dataset1._plot_clusters(X_train, X_train_label,
                                    cluster_labels, cluster_centroid)
        ###
        X_train = dataset1.data_mean
        X_train_label = 'Mean_Normalised'
        print('-----------------------------------')
        print('Clustering ', X_train_label)
        for num_clusters in [2, 3, 4, 5, 6, 7, 8, 9, ]:
            print(num_clusters, 'clusters')
            cluster_labels, cluster_centroid = \
                dataset1.cluster_scalar(X_train, num_clusters)
            dataset1._save_clusters(X_train, X_train_label,
                                    cluster_labels, cluster_centroid)
            dataset1._plot_clusters(X_train, X_train_label,
                                    cluster_labels, cluster_centroid)
        ###
        X_train = dataset1.line_reg_slopes
        X_train_label = 'Lin_regression_slopes_per_segments'
        print('-----------------------------------')
        print('Clustering ', X_train_label)
        for num_clusters in [2, 3, 4, 5, 6, 7, 8, 9, ]:
            print(num_clusters, 'clusters')
            cluster_labels, cluster_centroid = \
                dataset1.cluster_raw(X_train, num_clusters)
            dataset1._save_clusters(X_train, X_train_label,
                                    cluster_labels, cluster_centroid)
            dataset1._plot_clusters(X_train, X_train_label,
                                    cluster_labels,
                                    cluster_centroid, if_slopes=True)
        ###
        X_train = dataset1.mean_segments
        X_train_label = 'Mean_Segments'
        print('-----------------------------------')
        print('Clustering ', X_train_label)
        for num_clusters in [2, 3, 4, 5, 6, 7, 8, 9, ]:
            print(num_clusters, 'clusters')
            cluster_labels, cluster_centroid = dataset1.cluster_raw(X_train,
                                                                    num_clusters)
            dataset1._save_clusters(X_train, X_train_label,
                                    cluster_labels, cluster_centroid)
            dataset1._plot_clusters(X_train, X_train_label,
                                    cluster_labels, cluster_centroid)

    if if_cluster_hiararchical:
        signal = 'raw'
        dataset1.cluster_hierarchial(signal, if_save_plot=True)

    if if_detrend:
        dataset1.detrend()
