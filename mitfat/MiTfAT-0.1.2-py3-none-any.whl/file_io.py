#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 14:55:19 2018

@author: vbokharaie

This module includes methods of fmri_dataset class used for I/O operations.

"""
# pylint: disable=line-too-long

from mitfat import _Lib
__methods__ = [] # self is a DataStore
register_method = _Lib.register_method(__methods__)

#%%
@register_method
def save_clusters(self, X_train, data_label, cluster_labels, cluster_centroids):
    """Saves cluster to excel file
    Parameters
    ----------
    X_train: 'numpy.ndarray', (N_clustered_data, N_voxels)
                    N_clustered_data can be N_time_steps, 1, or N_segments
    data_label: 'str'
                used in establishing save folders
    cluster_labels: 'numpy.ndarray', (N_voxels, 1)
    cluster_centroids: 'numpy.ndarray', (N_clusters, N_clustered_data)
    """

    import pandas as pd
    import numpy as np
    import os
    no_clusters = np.unique(cluster_labels).shape[0]
    dir_save_subfolder = os.path.join(self.dir_save, \
                                      '02_clusters', \
                                      data_label+'_clusters_'+str(no_clusters))
    if not os.path.exists(dir_save_subfolder):
        os.makedirs(dir_save_subfolder)
    centroid_length = np.shape(cluster_centroids)[1]

    column_names = []
    my_index = np.arange(centroid_length)
    df_centroids = pd.DataFrame(columns=column_names, index=my_index)

    if centroid_length == self.num_time_steps:
        df_centroids['Time'] = self.time_steps
    elif centroid_length == 1:
        df_centroids['Index'] = 1
    else:
        my_indices = np.arange(centroid_length) + 1
        df_centroids['Segments'] = my_indices

    for cc_ in np.arange(no_clusters):
        df_centroids['Cluster_'+str(cc_+1)] = cluster_centroids[cc_, :]

    filename_csv = os.path.join(dir_save_subfolder, 'Cluster_centres.xlsx')
    df_centroids.to_excel(filename_csv, index=False)

# %% just print a template for info files
def print_info(filename_info=None):
    text_info = """
## This is a template for input files for the MiTfAT library,
#  				a pyhton-based fMRI analysis tool.
# In which line you write the info is irrelevant.
# every line not starting with a valid keyword is ignored.
# There should be at least one blank space between the keyword and the following input values.
# The only obligatory keywords are the DATA_FILE and MASK_FILE.
# The rest will be assigned default values or just ignored if not defined.

# REQUIRED keywords are:
# 'DATA_FILE:' -> (REQUIRED) name of the nifty data files
# 'MASK_FILE:' -> (REQUIRED) nifty file including the mask file.
                   0 elements in this file means ignore the voxel, non-zero means read the voxel.

# OPTIONAL Keywords:
# 'TIME_FILE:' -> file including time points for each data point.
                  If left blank, indices of data points are used as time-steps, starting from 1.
# 'EVENT_TIMES' -> can be any events of interest.
                    should be numbers (float or integer), comma separated.
                    They'd be irrelevant if TIME_FILE does not exist.
                    They do not need to match exact values of time steps.
# 'DIR_SOURCE:' -> Absolute or relative path to source directory.
                   default is 'datasets' subfolder inside the folder in which this file exists.
# 'DIR_SAVE' -> Absolute or relative path to directory used to save the outputs.
                default is used: 'output' subfolder inside the current python folder,
		(not necessarily folder containing this file).
# 'MOL_NAME:' -> Molecule name. Used in molecular fMRI experiments.
                 If not left blank will be used to establish DIR_SAVE name.
# 'EXP_NAME:' -> Experiment name.
                 If not left blank will be used to establish DIR_SAVE name.
# 'DESC:'-> A free style text with info about the dataset.
# 'DS_NO:' -> An integer number assigned to identify the dataset.
             If not left blank will be used to establish DIR_SAVE name.
# 'SIGNAL_NAME:' -> can be T1w, FISP, T2* or any arbitrary string.

## Here is a sample info file:
# obligatiry info:
DATA_FILE: sample_data_T1w.nii.gz
MASK_FILE: sample_data_mask.nii.gz

# optional time file, and event times
TIME_FILE: sample_data_time_T1w.txt
EVENT_TIMES: 123,181

# other optional info
MOL_NAME: SCA
SIGNAL_NAME: T1w
DS_NO: 1
EXP_NAME: Exp1
DESC: Just a sample dataset.
"""
    if not filename_info:
        print(text_info)
    else:
        with open(filename_info, 'w') as file:
            file.write(text_info)
        import pathlib
        print('info file template saved in:', pathlib.Path(filename_info).resolve())
        print(pathlib.Path(__file__).resolve())

# %% just print a template for info files
def test_script(filename=None):
    import pathlib
    import os
    from shutil import copyfile
    file_io_path = pathlib.Path(__file__).parent
    src = os.path.join(file_io_path, 'test_script.py')
    if not filename:
        filename = 'MiTfAT_test_script.py'
    dst = os.path.join(os.getcwd(), filename)
    copyfile(src, dst)


# %%
def read_data(info_file_name):
    """Reads the input dataset info from a file,
    returns a fmri_dataset object including all those files.

    Parameters
    ----------
    info_file_name:     str
        an os.path filename object

    Returns
    -------
    fmri_dataset: obj

    Raises
    ------

    """
    from mitfat.file_io import main_get_data
    from mitfat.fmri_dataset import fmri_dataset
    # read the data from file
    data_masked, mask_numpy, time_steps, signal_name,\
        indices_cutoff, experiment_name, dataset_no, mol_name,\
        dir_source, dir_save, description = main_get_data(info_file_name)

    # establish the fmri_dataset object
    fmri_object = fmri_dataset(data_masked, mask_numpy, time_steps, signal_name,
                               indices_cutoff,
                               experiment_name, dataset_no, mol_name,
                               dir_source, dir_save,
                               description)

    return fmri_object


#%%
def convert_real_time_to_index(times_files, cutoff_times_to_convert):
    """returns index values for first time steps bigger than input time-values.
    Parameters
    ----------
    times_files: 'str'
                path to file including values of time-steps
    cutoff_times_to_convert: 'list' of 'float'

    Returns
    -------
    output_list: 'list' if 'int'
                indices for time values

    """
    import numpy as np
    text_file = open(times_files, "r")
    time_steps = text_file.read().strip().split('\n')
    n_last = len(time_steps)-1
    n_0 = 0
    times_all = np.zeros(len(time_steps))
    for cc23, one_line in enumerate(time_steps):
        times_all[cc23] = np.float(one_line)
    output_list = []
    for idx, my_time in enumerate(cutoff_times_to_convert):
        bb_d = [i for i, v in enumerate(times_all) if v > my_time]
        output_list.append(bb_d[0])
    output_list.insert(0, n_0)
    output_list.append(n_last)
    return output_list



#%% read info file
def read_info_file(info_file_name):
    """reads the config file.
    assigns default values to fmri_dataset object if not defined in config file.
    A 'sample_info_file.txt' accompanying the library includes standrard format.
    Parameters
    ----------
    info_file_name: 'str'
                path to config file

    Returns
    -------
    data_file_name: 'str'
    mask_file_name: 'str'
    time_file_name: 'str'
    dir_source: 'str'
    dir_save: 'str'
    mol_name: 'str'
    exp_name: 'str'
    dataset_no: 'int'
    cutoff_times: 'list' of 'float'
    description: 'str'
    signal_name: 'str'
    """
    import os
    import pathlib
    # dir_path = os.path.dirname(os.path.realpath(__file__))
    # info_file_name = os.path.join(dir_path, info_file_name)
    try:
        with open(info_file_name) as f:
            info_file_content = f.readlines()
    except FileNotFoundError:
         dir_script = pathlib.Path(__file__)
         info_file_name = os.path.join(dir_script, info_file_name)
         with open(info_file_name) as f:
             info_file_content = f.readlines()

    dir_info_file = dir_infofile = os.path.dirname(info_file_name)
    dir_file_parent = pathlib.Path(__file__).parent
    print('---------------------------------------')
    print('Config file:', info_file_name)

    # %%
    info_file_content = [x.strip() for x in info_file_content]  # remove '\n'
    info_file_content = [x.lstrip() for x in info_file_content] # remove leading white space
    flag_data_file = False
    flag_mask_file = False
    flag_time_file = False
    flag_dir_source = False
    flag_dir_save = False
    flag_mol_name = False
    flag_exp_name = False
    flag_dataset_no = False
    flag_description = False
    flag_cutoff_times = False
    flag_signal_name = False

    for line in info_file_content:
        if line[:9].lower() == 'DATA_FILE'.lower():
            data_file_name = line[10:].strip()
            flag_data_file = True
        elif line[:9].lower() == 'MASK_FILE'.lower():
            mask_file_name = line[10:].strip()
            flag_mask_file = True
        elif line[:9].lower() == 'TIME_FILE'.lower():
            time_file_name = line[10:].strip()
            flag_time_file = True
        elif line[:10].lower() == 'DIR_SOURCE'.lower():
            dir_source = line[11:].strip()
            dir_source = pathlib.Path(dir_source)
            assert dir_source.is_dir(),\
                "'DIR_SOURCE' not a valid folder path."
            if not dir_source.is_absolute():
                dir_source = dir_source.resolve()

#            if dir_source[:2] == './':
#                dir_source = dir_source[2:]
#                dir_source = os.path.join(dir_info_file, dir_source)
#            elif dir_source[:3] == '../':
#                dir_source = dir_source[3:]
#                dir_source = os.path.join(dir_file_parent, dir_source)
            flag_dir_source = True
        elif line[:8].lower() == 'DIR_SAVE'.lower():
            dir_save = line[9:].strip()
            dir_save = pathlib.Path(dir_save)
            assert dir_save.is_dir(),\
                "'DIR_SOURCE' not a valid folder path."
            if not dir_save.is_absolute():
                dir_save = dir_save.resolve()

#            if dir_save[:2] == './':
#                dir_save = dir_save[2:]
#                dir_save = os.path.join(dir_info_file, dir_save)
#            elif dir_save[:3] == '../':
#                dir_save = dir_save[3:]
#                dir_save = os.path.join(dir_file_parent, dir_save)

            flag_dir_save = True
        elif line[:8].lower() == 'MOL_NAME'.lower():
            mol_name = line[9:].strip()
            flag_mol_name = True
        elif line[:8].lower() == 'EXP_NAME'.lower():
            exp_name = line[9:].strip()
            flag_exp_name = True
        elif line[:5].lower() == 'DS_NO'.lower():
            dataset_no = line[6:].strip()
            try:
                dataset_no = int(dataset_no)
            except ValueError:
                raise TypeError("Only integers are allowed for DS_NO in " + info_file_name)
            flag_dataset_no = True
        elif line[:4].lower() == 'DESC'.lower():
            description = line[5:].strip()
            flag_description = True
        elif line[:11].lower() == 'SIGNAL_NAME'.lower():
            signal_name = line[12:].strip()
            flag_signal_name = True
        elif line[:11].lower() == 'EVENT_TIMES'.lower():
            cutoff_times_raw = line[12:].strip()
            if cutoff_times_raw == '':
                pass
            else:
                cutoff_times_raw = cutoff_times_raw.split(",")
                cutoff_times = []
                for el in cutoff_times_raw:
                    current_time = float(el.strip())
                    cutoff_times.append(current_time)
            flag_cutoff_times = True
    if not flag_dir_source:
        # dir_path = os.path.dirname(os.path.realpath(__file__))
        # dir_path = pathlib.Path(dir_path)
        # dir_path = dir_path.resolve()
        # dir_parent = dir_path.parent
        # dir_source = os.path.join(dir_parent, 'resources', 'datasets')
        dir_source = os.path.join(dir_info_file, 'datasets')
    if not flag_dir_save:
        # dir_path = os.path.dirname(os.path.realpath(__file__))
        # dir_path = pathlib.Path(dir_path)
        # dir_path = dir_path.resolve()
        # dir_parent = dir_path.parent
        # dir_save_main = os.path.join(dir_parent, 'resources', 'output')
        dir_path = os.getcwd()
        dir_save_main = os.path.join(dir_path, 'output')
    if not flag_data_file:
        raise('Data file name is missing in info file')
    else:
        data_file_name = os.path.join(dir_source, data_file_name)
    if not flag_mask_file:
        raise('Mask file name is missing in info file')
    else:
        mask_file_name = os.path.join(dir_source, mask_file_name)
    if not flag_time_file:
        time_file_name = ''
    else:
        time_file_name = os.path.join(dir_source, time_file_name)


    if not flag_dataset_no:
        dataset_no = ''
        dir_save_ds = ''
    else:
        dir_save_ds = 'DS_' + str(dataset_no)

    if not flag_exp_name:
        exp_name = 'noname'
    dir_save_ds = dir_save_ds + '_exp_'+exp_name

    if not flag_mol_name:
        mol_name = ''
    else:
        dir_save_ds = dir_save_ds + '_mol_' + mol_name

    if not flag_signal_name:
        signal_name = 'unknown_signal'
    dir_save = os.path.join(dir_save_main, dir_save_ds, signal_name)
    if not flag_description:
        description = ''
    if not flag_cutoff_times:
        cutoff_times = ''


    return data_file_name, mask_file_name, time_file_name, dir_source, dir_save, \
        mol_name, exp_name, dataset_no, cutoff_times, description, signal_name

#%%
def main_get_data(info_file_name):
    """reads actual data based on info_file_name.
    uses read_info_file to read the config file and then loads the data.

    A 'sample_info_file.txt' accompanying the library includes standrard format.

    Parameters
    ----------
    info_file_name: 'str'
                path to config file

    Returns
    -------
    data_nii_masked: 'numpy.ndarray', (N_time_steps, N_voxels)
    mask_roi_numpy: 'numpy.ndarray', (d1, d2, d3)
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
    import nibabel

    from mitfat import flags

    mask_roi = []
    mask_roi_numpy = []

    data_file_name, mask_file_name, time_file_name, dir_source, dir_save, \
        mol_name, experiment_name, dataset_no, cutoff_times, description, signal_name = \
            read_info_file(info_file_name)

    print('----------------------------------------')
    print('reading data from: ', dir_source)
    print('outputs will be saved in: ', dir_save)
    print('----------------------------------------')


    data_roi = nibabel.load(data_file_name)
    mask_roi = nibabel.load(mask_file_name)
    mask_roi_numpy = mask_roi.get_data()
    # following line added in case mask values are not set at 1.
    mask_roi_numpy[mask_roi_numpy != 0] = 1;
    ## applying the mask and storing data in 2D format in a list
    from nilearn.masking import apply_mask
    data_nii_masked = apply_mask(data_roi, mask_roi)
    if flags.if_debug:
        from mitfat.func_tests import check_how_nilearn_apply_mask_works
        check_how_nilearn_apply_mask_works(data_nii_masked, data_roi)

    data_nii_masked = np.abs(data_nii_masked) # in case data is recorded as negative values
    print('Masked data shape: ')
    print('Number of time_steps: ', data_nii_masked.shape[0])
    print('Number of voxels ', data_nii_masked.shape[1])
    print('----------------------------------------')

    if not time_file_name == '':
        text_file = open(time_file_name, "r")
        time_steps_raw = text_file.read().strip().split('\n')
        time_steps = np.zeros(len(time_steps_raw))
        for cc23, one_line in enumerate(time_steps_raw):
            time_steps[cc23] = np.float(one_line)
        text_file.close()
    else:
        time_steps = np.arange(data_nii_masked.shape[0])+1

    if not (time_file_name == '' and cutoff_times == ''):
        time_steps_min = np.min(time_steps)
        time_steps_max = np.max(time_steps)
        for el in cutoff_times:
            if el < time_steps_min or el > time_steps_max:
                raise ValueError('EVENT_TIMES exceed time step values in TIME_FILE in '+\
                                 info_file_name)
        indices_cuttoff = \
            convert_real_time_to_index(time_file_name, cutoff_times)
    else:
        indices_cuttoff = [0, data_nii_masked.shape[0]-1]




    return data_nii_masked, mask_roi_numpy, time_steps, signal_name,\
                 indices_cuttoff, \
                 experiment_name, dataset_no, mol_name, \
                 dir_source, dir_save, \
                 description
