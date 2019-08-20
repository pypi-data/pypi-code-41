#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 10:40:07 2017
Copyright (C) 2018
@author: Derek Pisner (dPys)
"""
import warnings
import numpy as np
warnings.filterwarnings("ignore")


def get_conn_matrix(time_series, conn_model, dir_path, node_size, smooth, dens_thresh, network, ID, roi, min_span_tree,
                    disp_filt, parc, prune, atlas, uatlas, labels, coords, c_boot, norm, binary,
                    hpass):
    """
    Computes a functional connectivity matrix based on a node-extracted time-series array.
    Includes a library of routines across Nilearn, scikit-learn, and skggm packages, among others.

    Parameters
    ----------
    time_series : array
        2D m x n array consisting of the time-series signal for each ROI node where m = number of scans and
        n = number of ROI's.
    conn_model : str
       Connectivity estimation model (e.g. corr for correlation, cov for covariance, sps for precision covariance,
       partcorr for partial correlation). sps type is used by default.
    dir_path : str
        Path to directory containing subject derivative data for given run.
    node_size : int
        Spherical centroid node size in the case that coordinate-based centroids
        are used as ROI's.
    smooth : int
        Smoothing width (mm fwhm) to apply to time-series when extracting signal from ROI's.
    dens_thresh : bool
        Indicates whether a target graph density is to be used as the basis for
        thresholding.
    network : str
        Resting-state network based on Yeo-7 and Yeo-17 naming (e.g. 'Default') used to filter nodes in the study of
        brain subgraphs.
    ID : str
        A subject id or other unique identifier.
    roi : str
        File path to binarized/boolean region-of-interest Nifti1Image file.
    min_span_tree : bool
        Indicates whether local thresholding from the Minimum Spanning Tree
        should be used.
    disp_filt : bool
        Indicates whether local thresholding using a disparity filter and
        'backbone network' should be used.
    parc : bool
        Indicates whether to use parcels instead of coordinates as ROI nodes.
    prune : bool
        Indicates whether to prune final graph of disconnected nodes/isolates.
    atlas : str
        Name of atlas parcellation used.
    uatlas : str
        File path to atlas parcellation Nifti1Image in MNI template space.
    labels : list
        List of string labels corresponding to ROI nodes.
    coords : list
        List of (x, y, z) tuples corresponding to a coordinate atlas used or
        which represent the center-of-mass of each parcellation node.
    c_boot : int
        Number of bootstraps if user specified circular-block bootstrapped resampling of the node-extracted time-series.
    norm : int
        Indicates method of normalizing resulting graph.
    binary : bool
        Indicates whether to binarize resulting graph edges to form an
        unweighted graph.
    hpass : bool
        High-pass filter values (Hz) to apply to node-extracted time-series.

    Returns
    -------
    conn_matrix : array
        Adjacency matrix stored as an m x n array of nodes and edges.
    conn_model : str
       Connectivity estimation model (e.g. corr for correlation, cov for covariance, sps for precision covariance,
       partcorr for partial correlation). sps type is used by default.
    dir_path : str
        Path to directory containing subject derivative data for given run.
    node_size : int
        Spherical centroid node size in the case that coordinate-based centroids
        are used as ROI's for tracking.
    smooth : int
        Smoothing width (mm fwhm) to apply to time-series when extracting signal from ROI's.
    dens_thresh : bool
        Indicates whether a target graph density is to be used as the basis for
        thresholding.
    network : str
        Resting-state network based on Yeo-7 and Yeo-17 naming (e.g. 'Default') used to filter nodes in the study of
        brain subgraphs.
    ID : str
        A subject id or other unique identifier.
    roi : str
        File path to binarized/boolean region-of-interest Nifti1Image file.
    min_span_tree : bool
        Indicates whether local thresholding from the Minimum Spanning Tree
        should be used.
    disp_filt : bool
        Indicates whether local thresholding using a disparity filter and
        'backbone network' should be used.
    parc : bool
        Indicates whether to use parcels instead of coordinates as ROI nodes.
    prune : bool
        Indicates whether to prune final graph of disconnected nodes/isolates.
    atlas : str
        Name of atlas parcellation used.
    uatlas : str
        File path to atlas parcellation Nifti1Image in MNI template space.
    labels : list
        List of string labels corresponding to graph nodes.
    coords : list
        List of (x, y, z) tuples corresponding to a coordinate atlas used or
        which represent the center-of-mass of each parcellation node.
    c_boot : int
        Number of bootstraps if user specified circular-block bootstrapped resampling of the node-extracted time-series.
    norm : int
        Indicates method of normalizing resulting graph.
    binary : bool
        Indicates whether to binarize resulting graph edges to form an
        unweighted graph.
    hpass : bool
        High-pass filter values (Hz) to apply to node-extracted time-series.
    """
    import warnings
    warnings.filterwarnings("ignore")
    from nilearn.connectome import ConnectivityMeasure
    from sklearn.covariance import GraphicalLassoCV

    conn_matrix = None
    if conn_model == 'corr' or conn_model == 'cor' or conn_model == 'correlation':
        # credit: nilearn
        print('\nComputing correlation matrix...\n')
        conn_measure = ConnectivityMeasure(kind='correlation')
        conn_matrix = conn_measure.fit_transform([time_series])[0]
    elif conn_model == 'partcorr' or conn_model == 'parcorr' or conn_model == 'partialcorrelation':
        # credit: nilearn
        print('\nComputing partial correlation matrix...\n')
        conn_measure = ConnectivityMeasure(kind='partial correlation')
        conn_matrix = conn_measure.fit_transform([time_series])[0]
    elif conn_model == 'cov' or conn_model == 'covariance' or conn_model == 'covar' or conn_model == 'sps' or conn_model == 'sparse' or conn_model == 'precision':
        # Fit estimator to matrix to get sparse matrix
        estimator_shrunk = None
        estimator = GraphicalLassoCV(cv=5)
        try:
            print('\nComputing covariance...\n')
            estimator.fit(time_series)
        except:
            print('Unstable Lasso estimation--Attempting to re-run by first applying shrinkage...')
            try:
                from sklearn.covariance import GraphicalLasso, empirical_covariance, shrunk_covariance
                emp_cov = empirical_covariance(time_series)
                for i in np.arange(0.8, 0.99, 0.01):
                    shrunk_cov = shrunk_covariance(emp_cov, shrinkage=i)
                    alphaRange = 10.0 ** np.arange(-8, 0)
                    for alpha in alphaRange:
                        try:
                            estimator_shrunk = GraphicalLasso(alpha)
                            estimator_shrunk.fit(shrunk_cov)
                            print("Retrying covariance matrix estimate with alpha=%s" % alpha)
                            if estimator_shrunk is None:
                                pass
                            else:
                                break
                        except:
                            print("Covariance estimation failed with shrinkage at alpha=%s" % alpha)
                            continue
            except ValueError:
                print('Unstable Lasso estimation! Shrinkage failed. A different connectivity model may be needed.')
        if estimator is None and estimator_shrunk is None:
            raise RuntimeError('\nERROR: Covariance estimation failed.')
        if conn_model == 'sps' or conn_model == 'sparse' or conn_model == 'precision':
            if estimator_shrunk is None:
                print('\nFetching precision matrix from covariance estimator...\n')
                conn_matrix = -estimator.precision_
            else:
                print('\nFetching shrunk precision matrix from covariance estimator...\n')
                conn_matrix = -estimator_shrunk.precision_
        elif conn_model == 'cov' or conn_model == 'covariance' or conn_model == 'covar':
            if estimator_shrunk is None:
                print('\nFetching covariance matrix from covariance estimator...\n')
                conn_matrix = estimator.covariance_
            else:
                conn_matrix = estimator_shrunk.covariance_
    elif conn_model == 'QuicGraphicalLasso':
        try:
            from inverse_covariance import QuicGraphicalLasso
        except ImportError:
            print('Cannot run QuicGraphLasso. Skggm not installed!')

        # Compute the sparse inverse covariance via QuicGraphLasso
        # credit: skggm
        model = QuicGraphicalLasso(
            init_method='cov',
            lam=0.5,
            mode='default',
            verbose=1)
        print('\nCalculating QuicGraphLasso precision matrix using skggm...\n')
        model.fit(time_series)
        conn_matrix = -model.precision_
    elif conn_model == 'QuicGraphLassoCV':
        try:
            from inverse_covariance import QuicGraphicalLassoCV
        except ImportError:
            print('Cannot run QuicGraphLassoCV. Skggm not installed!')

        # Compute the sparse inverse covariance via QuicGraphLassoCV
        # credit: skggm
        model = QuicGraphicalLassoCV(
            init_method='cov',
            verbose=1)
        print('\nCalculating QuicGraphLassoCV precision matrix using skggm...\n')
        model.fit(time_series)
        conn_matrix = -model.precision_
    elif conn_model == 'QuicGraphicalLassoEBIC':
        try:
            from inverse_covariance import QuicGraphicalLassoEBIC
        except ImportError:
            print('Cannot run QuicGraphLassoEBIC. Skggm not installed!')

        # Compute the sparse inverse covariance via QuicGraphLassoEBIC
        # credit: skggm
        model = QuicGraphicalLassoEBIC(
            init_method='cov',
            verbose=1)
        print('\nCalculating QuicGraphLassoEBIC precision matrix using skggm...\n')
        model.fit(time_series)
        conn_matrix = -model.precision_
    elif conn_model == 'AdaptiveQuicGraphLasso':
        try:
            from inverse_covariance import AdaptiveQuicGraphicalLasso, QuicGraphicalLassoEBIC
        except ImportError:
            print('Cannot run AdaptiveGraphLasso. Skggm not installed!')

        # Compute the sparse inverse covariance via
        # AdaptiveGraphLasso + QuicGraphLassoEBIC + method='binary'
        # credit: skggm
        model = AdaptiveQuicGraphicalLasso(
            estimator=QuicGraphicalLassoEBIC(
                init_method='cov',
            ),
            method='binary',
        )
        print('\nCalculating AdaptiveQuicGraphLasso precision matrix using skggm...\n')
        model.fit(time_series)
        conn_matrix = -model.estimator_.precision_
    else:
        raise ValueError('\nERROR! No connectivity model specified at runtime. Select a valid estimator using the '
                         '-mod flag.')

    if conn_matrix.shape < (2, 2):
        raise RuntimeError('\nERROR! Matrix estimation selection yielded an empty or 1-dimensional graph. '
                           'Check time-series for errors or try using a different atlas')

    coords = np.array(coords)
    labels = np.array(labels)
    return conn_matrix, conn_model, dir_path, node_size, smooth, dens_thresh, network, ID, roi, min_span_tree, disp_filt, parc, prune, atlas, uatlas, labels, coords, c_boot, norm, binary, hpass


def extract_ts_parc(net_parcels_map_nifti, conf, func_file, coords, roi, dir_path, ID, network, smooth, atlas,
                    uatlas, labels, c_boot, block_size, hpass, detrending=True):
    """
    API for employing Nilearn's NiftiLabelsMasker to extract fMRI time-series data from spherical ROI's based on a
    given 3D atlas image of integer-based voxel intensities. The resulting time-series can then optionally be resampled
    using circular-block bootrapping. The final 2D m x n array is ultimately saved to file in .npy format

    Parameters
    ----------
    net_parcels_map_nifti : Nifti1Image
        A nibabel-based nifti image consisting of a 3D array with integer voxel intensities corresponding to ROI
        membership.
    conf : str
        File path to a confound regressor file for reduce noise in the time-series when extracting from ROI's.
    func_file : str
        File path to a preprocessed functional Nifti1Image in standard space.
    coords : list
        List of (x, y, z) tuples corresponding to the center-of-mass of each parcellation node.
    dir_path : str
        Path to directory containing subject derivative data for given run.
    ID : str
        A subject id or other unique identifier.
    roi : str
        File path to binarized/boolean region-of-interest Nifti1Image file.
    network : str
        Resting-state network based on Yeo-7 and Yeo-17 naming (e.g. 'Default')
        used to filter nodes in the study of brain subgraphs.
    smooth : int
        Smoothing width (mm fwhm) to apply to time-series when extracting signal from ROI's.
    atlas : str
        Name of atlas parcellation used.
    uatlas : str
        File path to atlas parcellation Nifti1Image in MNI template space.
    labels : list
        List of string labels corresponding to graph nodes.
    c_boot : int
        Number of bootstraps if user specified circular-block bootstrapped resampling of the node-extracted time-series.
    block_size : int
        Size bootstrap blocks if bootstrapping (c_boot) is performed.
    hpass : bool
        High-pass filter values (Hz) to apply to node-extracted time-series.
    detrending : bool
        Indicates whether to remove linear trends from time-series when extracting across nodes. Default is True.

    Returns
    -------
    ts_within_nodes : array
        2D m x n array consisting of the time-series signal for each ROI node where m = number of scans and
        n = number of ROI's, where ROI's are parcel volumes.
    smooth : int
        Smoothing width (mm fwhm) to apply to time-series when extracting signal from ROI's.
    dir_path : str
        Path to directory containing subject derivative data for given run.
    atlas : str
        Name of atlas parcellation used.
    uatlas : str
        File path to atlas parcellation Nifti1Image in MNI template space.
    labels : list
        List of string labels corresponding to ROI nodes.
    coords : list
        List of (x, y, z) tuples corresponding to the center-of-mass of each parcellation node.
    c_boot : int
        Number of bootstraps if user specified circular-block bootstrapped resampling of the node-extracted time-series.
    hpass : bool
        High-pass filter values (Hz) to apply to node-extracted time-series.
    """
    import warnings
    warnings.filterwarnings("ignore")
    import os.path as op
    from nilearn import input_data
    from pynets.core import utils

    if not op.isfile(func_file):
        raise ValueError('\nERROR: Functional data input not found! Check that the file(s) specified with the -i flag '
                         'exist(s)')

    if conf:
        if not op.isfile(conf):
            raise ValueError('\nERROR: Confound regressor file not found! Check that the file(s) specified with the '
                             '-conf flag exist(s)')

    parcel_masker = input_data.NiftiLabelsMasker(labels_img=net_parcels_map_nifti, background_label=0,
                                                 standardize=True, smoothing_fwhm=float(smooth), high_pass=hpass,
                                                 detrend=detrending, verbose=2, resampling_target='data')
    ts_within_nodes = parcel_masker.fit_transform(func_file, confounds=conf)
    if ts_within_nodes is None:
        raise RuntimeError('\nERROR: Time-series extraction failed!')
    if float(c_boot) > 0:
        print("%s%s%s" % ('Performing circular block bootstrapping iteration: ', c_boot, '...'))
        ts_within_nodes = utils.timeseries_bootstrap(ts_within_nodes, block_size)[0]
    print("%s%s%d%s" % ('\nTime series has {0} samples'.format(ts_within_nodes.shape[0]), ' mean extracted from ',
                        len(coords), ' volumetric ROI\'s'))
    print("%s%s%s" % ('Smoothing FWHM: ', smooth, ' mm\n'))
    print("%s%s%s" % ('Applying high-pass filter: ', hpass, ' Hz\n'))

    # Save time series as file
    utils.save_ts_to_file(roi, network, ID, dir_path, ts_within_nodes, c_boot)
    node_size = None
    return ts_within_nodes, node_size, smooth, dir_path, atlas, uatlas, labels, coords, c_boot, hpass


def extract_ts_coords(node_size, conf, func_file, coords, dir_path, ID, roi, network, smooth, atlas,
                      uatlas, labels, c_boot, block_size, hpass, detrending=True):
    """
    API for employing Nilearn's NiftiSpheresMasker to extract fMRI time-series data from spherical ROI's based on a
    given list of seed coordinates. The resulting time-series can then optionally be resampled using circular-block
    bootrapping. The final 2D m x n array is ultimately saved to file in .npy format

    Parameters
    ----------
    node_size : int
        Spherical centroid node size in the case that coordinate-based centroids
        are used as ROI's for tracking.
    conf : str
        File path to a confound regressor file for reduce noise in the time-series when extracting from ROI's.
    func_file : str
        File path to a preprocessed functional Nifti1Image in standard space.
    coords : list
        List of (x, y, z) tuples corresponding to an a-priori defined set (e.g. a coordinate atlas).
    dir_path : str
        Path to directory containing subject derivative data for given run.
    ID : str
        A subject id or other unique identifier.
    roi : str
        File path to binarized/boolean region-of-interest Nifti1Image file.
    network : str
        Resting-state network based on Yeo-7 and Yeo-17 naming (e.g. 'Default')
        used to filter nodes in the study of brain subgraphs.
    smooth : int
        Smoothing width (mm fwhm) to apply to time-series when extracting signal from ROI's.
    atlas : str
        Name of atlas parcellation used.
    uatlas : str
        File path to atlas parcellation Nifti1Image in MNI template space.
    labels : list
        List of string labels corresponding to graph nodes.
    c_boot : int
        Number of bootstraps if user specified circular-block bootstrapped resampling of the node-extracted time-series.
    block_size : int
        Size bootstrap blocks if bootstrapping (c_boot) is performed.
    hpass : bool
        High-pass filter values (Hz) to apply to node-extracted time-series.
    detrending : bool
        Indicates whether to remove linear trends from time-series when extracting across nodes. Default is True.

    Returns
    -------
    ts_within_nodes : array
        2D m x n array consisting of the time-series signal for each ROI node where m = number of scans and
        n = number of ROI's, where ROI's are spheres.
    node_size : int
        Spherical centroid node size in the case that coordinate-based centroids
        are used as ROI's for tracking.
    smooth : int
        Smoothing width (mm fwhm) to apply to time-series when extracting signal from ROI's.
    dir_path : str
        Path to directory containing subject derivative data for given run.
    atlas : str
        Name of atlas parcellation used.
    uatlas : str
        File path to atlas parcellation Nifti1Image in MNI template space.
    labels : list
        List of string labels corresponding to ROI nodes.
    coords : list
        List of (x, y, z) tuples corresponding to a coordinate atlas used or
        which represent the center-of-mass of each parcellation node.
    c_boot : int
        Number of bootstraps if user specified circular-block bootstrapped resampling of the node-extracted time-series.
    hpass : bool
        High-pass filter values (Hz) to apply to node-extracted time-series.
    """
    import warnings
    warnings.filterwarnings("ignore")
    import os.path as op
    from nilearn import input_data
    from pynets.core import utils

    if not op.isfile(func_file):
        raise ValueError('\nERROR: Functional data input not found! Check that the file(s) specified with the -i flag '
                         'exist(s)')

    if conf:
        if not op.isfile(conf):
            raise ValueError('\nERROR: Confound regressor file not found! Check that the file(s) specified with the '
                             '-conf flag exist(s)')

    if len(coords) > 0:
        spheres_masker = input_data.NiftiSpheresMasker(seeds=coords, radius=float(node_size), allow_overlap=True,
                                                       standardize=True, smoothing_fwhm=float(smooth), high_pass=hpass,
                                                       detrend=detrending, verbose=2)
        ts_within_nodes = spheres_masker.fit_transform(func_file, confounds=conf)
        if float(c_boot) > 0:
            print("%s%s%s" % ('Performing circular block bootstrapping iteration: ', c_boot, '...'))
            ts_within_nodes = utils.timeseries_bootstrap(ts_within_nodes, block_size)[0]
        if ts_within_nodes is None:
            raise RuntimeError('\nERROR: Time-series extraction failed!')
    else:
        raise RuntimeError(
            '\nERROR: Cannot extract time-series from an empty list of coordinates. \nThis usually means '
            'that no nodes were generated based on the specified conditions at runtime (e.g. atlas was '
            'overly restricted by an RSN or some user-defined mask.')

    print("%s%s%d%s" % ('\nTime series has {0} samples'.format(ts_within_nodes.shape[0]), ' mean extracted from ',
                        len(coords), ' coordinate ROI\'s'))
    print("%s%s%s" % ('Using node radius: ', node_size, ' mm'))
    print("%s%s%s" % ('Smoothing FWHM: ', smooth, ' mm\n'))
    print("%s%s%s" % ('Applying high-pass filter: ', hpass, ' Hz\n'))

    # Save time series as file
    utils.save_ts_to_file(roi, network, ID, dir_path, ts_within_nodes, c_boot)
    return ts_within_nodes, node_size, smooth, dir_path, atlas, uatlas, labels, coords, c_boot, hpass
