#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 19:05:33 2019

@author: vbokharaie

This module includes methods of fmri_dataset class used for plotting.

"""
from mitfat import _Lib
from mitfat import flags

__methods__ = []
register_method = _Lib.register_method(__methods__)

# %% plotting a list of 2d arrays, each row being fmri time-series for each voxel
# function plots all time series in each voxel in a plot
@register_method
def plot_basics(self, data_type='normalised'):
    """Plots the time-series corresponsing to each voxel.
    The plots are arranged in a layout which follows the mask.
    Each layer is saved in a separeta file.
    Parameters
    ----------
    data_type : {'normalised', 'raw', 'lin_reg'}
        'normalised' (default): plot normalised time-series.
        'raw': plot raw signal
        'lin_reg': plot linear regression of time-series
    Raises
    ------
    NameError
        If data is not normalised and user tries to plot normalised data.
    """

    import matplotlib.pyplot as plt
    import matplotlib
    import os
    import numpy as np

    # which kind of signal?
    if data_type == 'normalised':
        try:
            my_data = self.data_normalised
        except NameError:
            print('normalised version of data does not exist')
            return
        subfolder = '01_basics_normalised'
        print('Plot basic plots for normalised signals ...')
    elif data_type == 'raw':
        my_data = self.data
        subfolder = '01_basics_raw'
        print('Plot basic plots for raw signals ...')
    elif data_type == 'lin_reg':
        try:
            my_data = self.line_reg
            subfolder = '01_basics_linear_regresseion'
            print('Plot basic plots for linear regressed signals ...')
        except:
            print('The RoiDataset object does not contain a linear regression version of the data.')
            print('Run lin_reg method first.')
            return
    # where to save?
    dir_save = os.path.join(self.dir_save, subfolder)
    print('Plot will be saved in: \n', dir_save)
    if not os.path.exists(dir_save):
        os.makedirs(dir_save)

    # general variables
    no_voxels = self.num_voxels
#    no_time_steps = self.num_time_steps
    bbox_seq = self.bbox_mask_seq
    bbox_mean = self.bbox_data_mean
    [n_row, n_col, no_figures] = bbox_seq.shape
    y_max = np.nanmax(my_data)

    # plot params
    plt.style.use('classic')
    cmap = matplotlib.cm.get_cmap('viridis')
    fig_w = 2*n_col
    fig_h = 2*n_row

    # %% let's count
    idx = 0
    for cc1 in np.arange(no_figures):
        print('Saving layer', cc1+1, 'of ', no_figures, ' ...')
        fig, my_ax_all = plt.subplots(nrows=n_row, ncols=n_col,
                                      sharey=False, figsize=(fig_w, fig_h))
        fig.tight_layout(rect=[0, 0.03, 1, 0.95], w_pad=0.02)

        for cc_r in np.arange(n_row):
            is_new_row = True
            if data_type == 'lin_reg':
                is_new_row == False  # no need for y-axis ticks for lin_reg data.
            for cc_c in np.arange(n_col):
                my_ax = my_ax_all[cc_r, cc_c]
                my_ax.grid()
                my_ax.set_ylim(0, y_max)

                if bbox_seq[cc_r, cc_c, cc1] != 0:
                    data_ind = bbox_seq[cc_r, cc_c, cc1]-1
                    my_ax.set(title='Voxel '+str(idx+1).zfill(4))
                    my_ax.plot(self.time_steps, my_data[:, data_ind],
                               label=self.signal_name,
                               color='black')

                    if len(self.cutoff_times) > 2:
                        my_ax.set_xticks(self.cutoff_times)
                        my_ax.tick_params(axis='both', which='major', labelsize=7)
                        from matplotlib.ticker import FormatStrFormatter
                        my_ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
                        my_ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
                        for cc_t in np.arange(len(self.cutoff_times)):
                            my_ax.axvline(x=self.cutoff_times[cc_t],
                                          color='k', linestyle='--', linewidth=1) # vertical lines
                    color_face = cmap(bbox_mean[cc_r, cc_c, cc1])
                    my_ax.set_facecolor(color_face)
                    # y label ticks only shown in the first subplot in each row
                    if not is_new_row:
                        my_ax.set_yticklabels([])
                    else:
                        is_new_row = False

                    idx = idx+1
                else:
                    my_ax.axis('off')  #subplots outside the mask are suppressed

        voxel_start = str(cc1*(n_row*n_col)).zfill(4)
        voxel_end = str(np.min([(cc1+1)*n_row*n_col, no_voxels])).zfill(4)
        filename = 'Voxels_'+voxel_start+'_to_'+voxel_end
        filename = os.path.join(dir_save, filename)
        fig.savefig(filename+'.png', dpi=200, figsize=(fig_w, fig_h), format='png')
        if flags.if_save_eps:
            fig.savefig(filename+'.eps', transparent=False, figsize=(fig_w, fig_h), format='eps')
        fig.clf()

    plt.close('all')


# %% bbox the clusters and time-series plots
@register_method
def plot_clusters(self, original_data, data_label,
                   cluster_labels, cluster_centroids,
                   if_slopes=False, if_hierarchical=False):
    """Plots the cluster, saves cntroid values.
    Including bbox plots, centroid plots.
    centroids are saved in .xlsx file in the same folder as plots.

    The plots are arranged in a layout which follows the mask.
    Each layer is saved in a separeta file.

    Parameters
    ----------

    original_data: 'numpy.ndarray', (N_clustered_data, N_voxels)
                    N_clustered_data can be N_time_steps, 1, or N_segments
    data_label: 'str'
                used in establishing save folders
    cluster_labels: 'numpy.ndarray', (N_voxels, 1)
    cluster_centroids: 'numpy.ndarray', (N_clusters, N_clustered_data)

    Raises
    ------

    NameError
        If data is not normalised and user tries to plot normalised data.
    """

    import seaborn as sns
    import numpy as np
    import matplotlib.pyplot as plt
    import os
    sns.set_style("white", {'axes.grid': True})
    # sns.set(font_scale=2.0)
    no_clusters = np.unique(cluster_labels).shape[0]
    centroid_length = np.shape(cluster_centroids)[1]
    if if_hierarchical:
        original_data = self.data_hierarchical
        mask_bbox = self.bbox_mask_hierarchical
        dir_save_subfolder = os.path.join(self.dir_save,
                                          '02_clusters_hierarchical',
                                          data_label+'_clusters_'+str(no_clusters))
    else:
        mask_bbox = self.bbox_mask
        dir_save_subfolder = os.path.join(self.dir_save,
                                          '02_clusters',
                                          data_label+'_clusters_'+str(no_clusters))
    if not os.path.exists(dir_save_subfolder):
        os.makedirs(dir_save_subfolder)

#    original_data = self.data_normalised
    y_max = np.nanmax(original_data)
    colours_for_cat = ['#f43605', '#fcc006', '#89a203',
                       '#047495', '#030764', '#c071fe',
                       '#db5856', '#0cdc73', '#fbdd7e', '#e78ea5']
    colours_for_cat = colours_for_cat + colours_for_cat
    colours_for_cat = colours_for_cat[0:no_clusters]
    colours_for_cat_colorbar = ['#000000']+colours_for_cat
    cat_labels = ['Cluster '+str(idx+1) for idx in np.arange(no_clusters)]
    bbox_cat = np.int8(np.zeros(np.shape(mask_bbox)))-1
    bbox_cat[mask_bbox == 1] = cluster_labels
    _plot_and_save_bbox_discrete(bbox_cat, dir_save_subfolder,
                                sup_title='kmeans with '+str(no_clusters)+' clusters',
                                colours=colours_for_cat_colorbar)
    fig, my_ax = plt.subplots(nrows=1, ncols=1, sharey=True, figsize=(12, 8))

    if (self.num_time_steps == centroid_length) and centroid_length > 1:
        for cc2 in np.arange(no_clusters):
            sns.set_style("white", {'axes.grid': True})

            my_ax.plot(self.time_steps, cluster_centroids[cc2, :],
                       label=cat_labels[cc2], color=colours_for_cat[cc2], lw=5)
            fig.suptitle(str(len(list(set(cluster_labels)))) + ' clusters')
            for cc_t in np.arange(len(self.indices_cutoff)):
                my_ax.axvline(x=self.cutoff_times[cc_t], color='k',
                              linestyle='--', linewidth=1)  # vertical lines
        my_ax.set_xticks(self.cutoff_times)
        my_ax.grid(True)
        my_ax.set_ylim(0, y_max)
        for item in ([my_ax.xaxis.label, my_ax.yaxis.label] +
                     my_ax.get_xticklabels() + my_ax.get_yticklabels()):
            item.set_fontsize(20)
            item.set_fontweight('bold')
        handles, labels = my_ax.get_legend_handles_labels()
        fig.legend(handles, labels, loc='upper right')

        filename_bb_wo_raw = os.path.join(dir_save_subfolder, 'Cluster_centres')
        fig.savefig(filename_bb_wo_raw+'.png', dpi=100, figsize=(16.0, 10.0), format='png')
        if flags.if_save_eps:
            fig.savefig(filename_bb_wo_raw+'.eps', transparent=False, dpi=100,
                        figsize=(16.0, 10.0), format='eps')
        for cc3 in np.arange(original_data.shape[1]):
            my_cluster_label = cluster_labels[cc3]
            my_ax.plot(self.time_steps, original_data[:, cc3],
                       color=colours_for_cat[my_cluster_label],
                       alpha=0.2, linestyle='dotted')

        filename_bb_alpha = os.path.join(dir_save_subfolder,
                                         'Cluster_centres_with_OriginalData')
        fig.savefig(filename_bb_alpha+'.png', dpi=100, figsize=(16.0, 10.0), format='png')
        if flags.if_save_eps:
            fig.savefig(filename_bb_alpha+'.eps', transparent=False, dpi=100,
                        figsize=(16.0, 10.0), format='eps')
    else:
        if centroid_length == 1 and not if_slopes:
            ind = (np.arange(np.shape(cluster_centroids)[0])+1)
            my_ax.bar(ind, cluster_centroids.flatten(), color=colours_for_cat)
            fig.suptitle('Cluster Centres')

        elif centroid_length == 1 and if_slopes:
            for cc2 in np.arange(no_clusters):
                time_steps = self.time_steps
                temp_line = np.zeros(np.shape(time_steps))
                indices_cutoff = self.indices_cutoff
                for cc3 in np.arange(centroid_length):
                    x_temp = time_steps[indices_cutoff[cc3]:indices_cutoff[cc3+1]+1]\
                                - time_steps[indices_cutoff[cc3]]
                    if cc3 > 0:
                        y_temp = x_temp*cluster_centroids[cc2, cc3] + \
                                temp_line[indices_cutoff[cc3]]
                    else:
                        y_temp = x_temp*cluster_centroids[cc2, cc3]
                    temp_line[indices_cutoff[cc3]:indices_cutoff[cc3+1]+1] = y_temp

                my_ax.plot(time_steps, temp_line[:],\
                    label=cat_labels[cc2], color=colours_for_cat[cc2])

                fig.suptitle('Cluster Centres'+\
                             '\n lines represent slopes, not actuall signal values')
                for cc_t in np.arange(len(indices_cutoff)):
                    my_ax.axvline(x=time_steps[indices_cutoff[cc_t]], color='k',\
                                      linestyle='--', linewidth=1) # vertical lines

        elif centroid_length < self.num_time_steps and centroid_length > 1 and not if_slopes:
            for cc2 in np.arange(no_clusters):
                my_ax.plot(np.arange(centroid_length)+1,\
                            cluster_centroids[cc2, :], label=cat_labels[cc2],\
                            color=colours_for_cat[cc2], marker='H', linestyle=':')
            from matplotlib.ticker import MaxNLocator
            my_ax.xaxis.set_major_locator(MaxNLocator(integer=True)) # x ticks be integer
            fig.suptitle('Cluster Centres')

        elif centroid_length < self.num_time_steps and centroid_length > 1 and if_slopes:
            for cc2 in np.arange(no_clusters):
                time_steps = self.time_steps
                temp_line = np.zeros(np.shape(time_steps))
                indices_cutoff = self.indices_cutoff
                for cc3 in np.arange(centroid_length):
                    x_temp = time_steps[indices_cutoff[cc3]:indices_cutoff[cc3+1]+1] - \
                             time_steps[indices_cutoff[cc3]]
                    if cc3 > 0:
                        y_temp = x_temp*cluster_centroids[cc2, cc3] + \
                                        temp_line[indices_cutoff[cc3]]
                    else:
                        y_temp = x_temp*cluster_centroids[cc2, cc3]
                    temp_line[indices_cutoff[cc3]:indices_cutoff[cc3+1]+1] = y_temp

                my_ax.plot(time_steps, temp_line[:],
                           label=cat_labels[cc2], color=colours_for_cat[cc2])
                fig.suptitle('Cluster Centres' +
                             '\n lines represent slopes, not actuall signal values')
                for cc_t in np.arange(len(indices_cutoff)):
                    my_ax.axvline(x=time_steps[indices_cutoff[cc_t]], color='k',
                                  linestyle='--', linewidth=1)  # vertical lines

        my_ax.grid(True)
        handles, labels = my_ax.get_legend_handles_labels()
        fig.legend(handles, labels, loc='upper right')
        filename_bb = os.path.join(dir_save_subfolder, 'Cluster_centres')
        fig.savefig(filename_bb+'.png', dpi=100, figsize=(16.0, 10.0), format='png')
        if flags.if_save_eps:
            fig.savefig(filename_bb+'.eps', transparent=False,
                        dpi=100, figsize=(16.0, 10.0), format='eps')

    plt.close('all')

# %%
@register_method
def _plot_and_save_bbox_discrete(my_bbox, dir_save_bb,
                                 sup_title=[], limits=[], colours=[]):
    """Plots continuous bbox
    when elemnts are continuous values (such as mean)
    default color pallete is default (virdis), 0 will be navy and 1 will be yellow.

    Parameters
    ----------
    my_bbox: 'numpy.ndarray'
    dir_save_bb: 'str'
        path to save folder
    suptitle: 'str' optional
        used to title plots
    limits: 'list' ['float']
    colours: 'list', matplotlib colors

    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    import numpy as np
    import os
    [aa_d, bb_d, cc_d] = np.shape(my_bbox)
#    plt.close('all')
    my_vmax = np.max(np.unique(my_bbox))
#    colours_all = colours
#    colours_selected = colours_all[0:my_vmax+2]
    colours_selected = colours
    cmap = ListedColormap(colours_selected)

    for cc3 in np.arange(cc_d):
        fig, my_ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 8))
        my_matrix = my_bbox[:, :, cc3]
        mat = my_ax.matshow(my_matrix, cmap=cmap, vmin=-1,
                            vmax=my_vmax, origin='upper', aspect='equal')
        if my_vmax == 0:
            cbar = fig.colorbar(mat, ticks=np.arange(0, my_vmax+2), shrink=0.4)
            labels = ['Representative Voxels']
        else:
            cbar = fig.colorbar(mat, ticks=np.arange(0, my_vmax+2), shrink=0.9)
            labels = list(np.arange(0, my_vmax+2))
            labels = ['Cluster'+str(x+1) for x in labels[0:-1]]
            labels = labels+[' ']

        cbar.ax.set_yticklabels(labels)
        xticks = [x - 0.5 for x in np.arange(my_matrix.shape[1])][1:]
        yticks = [y - 0.5 for y in np.arange(my_matrix.shape[0])][1:]
        my_ax.set_xticks(xticks)
        my_ax.set_yticks(yticks)
        my_ax.set_xticks(np.arange(my_matrix.shape[1]), minor=True)
        my_ax.set_yticks(np.arange(my_matrix.shape[0]), minor=True)

        my_ax.set_xticklabels(np.arange(my_matrix.shape[1])+1, minor=True)
        my_ax.set_yticklabels(np.arange(my_matrix.shape[0])+1, minor=True)
        my_ax.set_yticklabels([])
        my_ax.set_xticklabels([])
        my_ax.grid(color='w', linewidth=0.2)

        filename = 'Axis_3_Slice_'+str(cc3+1).zfill(3)
        filename = os.path.join(dir_save_bb, filename)
        # fig.suptitle(sup_title+'- > '+'Axis 3, Slice '+str(cc3+1).zfill(2) )
        fig.savefig(filename+'.png', dpi=100, figsize=(20.0, 15.0), format='png')
        if flags.if_save_eps:
            fig.savefig(filename + '.eps', dpi=100, figsize=(20, 15), format='eps')
        fig.clf()

    plt.close('all')

# %%
@register_method
def _plot_and_save_bbox_continuous(my_bbox, dir_save_bb,
                                   sup_title=[], v_min=0.0, v_max=1.0):
    """Plots continuous bbox
    when elemnts are continuous values (such as mean)
    default color pallete is default (virdis), 0 will be navy and 1 will be yellow.

    Parameters
    ----------
    my_bbox: 'numpy.ndarray'
    dir_save_bb: 'str'
        pth to save folder
    suptitle: 'str' optional
        used to title plots

    """
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib import cm
    [aa_d, bb_d, cc_d] = np.shape(my_bbox)


    plt.close('all')
    for cc3 in np.arange(cc_d):
        fig, my_ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 8))
        #fig.suptitle(sup_title+': Signal mean value - >  Axis 3, Slice '+str(cc3+1).zfill(2))
        h_ = my_ax.pcolor(my_bbox[:, :, cc3], vmin=v_min, vmax=v_max, cmap=cm.gist_gray)
        my_ax.set_aspect(1)
        fig.colorbar(h_)
        filename = 'Axis_3_Slice_'+str(cc3+1).zfill(3)
        filename = os.path.join(dir_save_bb, filename)
        #fig.savefig(filename, dpi=100, figsize=(16.0, 10.0))
        fig.savefig(filename, dpi=100, figsize=(16.0, 10.0), format='png')
        try:
            fig.savefig(filename+'_eps', dpi=100, figsize=(16.0, 10.0), format='eps')
        except:
            pass
        fig.clf()
    plt.close('all')


# %%
@register_method
def function1(self, arg1, arg2, arg3):
    """returns (arg1 / arg2) + arg3

    This is a longer explanation, which may include math with latex syntax
    :math:`\\alpha`.
    Then, you need to provide optional subsection in this order (just to be
    consistent and have a uniform documentation. Nothing prevent you to
    switch the order):

      - parameters using ``:param <name>: <description>``
      - type of the parameters ``:type <name>: <description>``
      - returns using ``:returns: <description>``
      - examples (doctest)
      - seealso using ``.. seealso:: text``
      - notes using ``.. note:: text``
      - warning using ``.. warning:: text``
      - todo ``.. todo:: text``

    **Advantages**:
     - Uses sphinx markups, which will certainly be improved in future
       version
     - Nice HTML output with the See Also, Note, Warnings directives


    **Drawbacks**:
     - Just looking at the docstring, the parameter, type and  return
       sections do not appear nicely

    :param arg1: the first value
    :param arg2: the first value
    :param arg3: the first value
    :type arg1: int, float,...
    :type arg2: int, float,...
    :type arg3: int, float,...
    :returns: arg1/arg2 +arg3
    :rtype: int, float

    :Example:

    >>> import template
    >>> a = template.MainClass1()
    >>> a.function1(1,1,1)
    2

    .. note:: can be useful to emphasize
        important feature
    .. seealso:: :class:`MainClass2`
    .. warning:: arg2 must be non-zero.
    .. todo:: check that arg2 is non zero.
    """
    return arg1/arg2 + arg3
