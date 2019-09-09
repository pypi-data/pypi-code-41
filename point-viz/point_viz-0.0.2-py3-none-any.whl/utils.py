from __future__ import division

import numpy as np
import os
from copy import deepcopy

parula_list = [[53, 42, 135],
               [15, 92, 221],
               [18, 125, 216],
               [7, 156, 207],
               [21, 177, 180],
               [89, 189, 140],
               [165, 190, 107],
               [225, 185, 82],
               [252, 206, 46],
               [249, 251, 14],
               [255, 255, 0]]
parula_list = np.array(parula_list, dtype=np.float32)


def get_parula_color_map_from_ratio(ratio):
    parula_idx = ratio * 10.
    if parula_idx <= 0.:
        return parula_list[0]
    elif parula_idx >= 10.:
        return parula_list[-1]
    parula_idx_lower = int(np.floor(parula_idx))
    parula_idx_upper = parula_idx_lower + 1
    parula_rgb_lower = parula_list[parula_idx_lower]
    parula_rgb_upper = parula_list[parula_idx_upper]
    parula_rgb_range = parula_rgb_upper - parula_rgb_lower
    parula_idx_offset = parula_idx - np.floor(parula_idx)
    parula_rgb = parula_rgb_lower + parula_idx_offset * parula_rgb_range
    return np.array([parula_rgb], dtype=np.float32)


def get_rgb_color_map_from_ratio(ratio):
    if 0. <= ratio < 0.25:
        R = 1. - ratio * 2.
        G = ratio * 4.
        B = 0.
    elif 2.5 <= ratio < 0.5:
        R = 0.
        G = 1.
        B = ratio * 4. - 1.
    elif 0.5 <= ratio < 0.75:
        R = 0.
        G = -4. * ratio + 3.
        B = 1.
    else:
        R = 2. * ratio - 1.
        G = 0.
        B = -4. * ratio + 4.
    return np.array([R, G, B], dtype=np.float32) * 255.


cmp_method_dict = {'parula': get_parula_color_map_from_ratio,
                   'rgb': get_rgb_color_map_from_ratio}


def get_color_from_intensity(intensity, cmp='parula'):
    intensity = deepcopy(intensity)
    assert len(intensity.shape) == 1, \
        "The intensity should be in 1-D, but actually got: {}-D".format(len(intensity.shape))
    intensity -= np.percentile(intensity, 1)
    intensity /= np.percentile(intensity, 99)
    colors = np.zeros((intensity.shape[0], 3), dtype=np.float32)
    for i in range(intensity.shape[0]):
        colors[i, :] = cmp_method_dict[cmp](intensity[i])
    return colors


def get_color_from_coors(coors):
    coors = deepcopy(coors)
    assert len(coors.shape) == 2, \
        "The intensity should be in 2-D, but actually got: {}-D".format(len(coors.shape))
    coors -= np.min(coors, axis=0)
    coors /= np.max(coors, axis=0)
    colors = coors * 255.
    return colors


def get_color_from_height(coors, axis=1, cmp='parula'):
    coors = deepcopy(coors)
    height = coors[:, axis]
    height -= np.percentile(height, 1)
    height /= np.percentile(height, 99)
    colors = np.zeros((coors.shape[0], 3), dtype=np.float32)
    for i in range(coors.shape[0]):
        colors[i, :] = cmp_method_dict[cmp](height[i])
    return colors


def get_color_from_class(labels, random_seed=0):
    assert len(labels.shape) == 1, \
        "The labels should be in 1-D, but actually got: {}-D".format(len(labels.shape))
    label_idxs = np.unique(labels)
    colors = np.zeros((labels.shape[0], 3), dtype=np.float32)
    for idx in label_idxs:
        np.random.seed(int(idx + random_seed))
        color = (np.random.uniform(size=[3]) * 255).astype(np.float32)
        label_idx = np.argwhere(labels == idx)
        colors[label_idx, :] = color
    return colors


def create_dir(path, clean=False):
    try:
        os.makedirs(path)
    except OSError:
        if not clean:
            print("WARNING: {} already exists, operation skipped.".format(path))
        else:
            os.system('rm -r {}'.format(path))
            os.makedirs(path)
            print("WARNING: '{}' already exists, and has been cleaned.".format(path))


def coors_normalize(coors):
    norm = np.max(np.percentile(np.abs(coors), 90, axis=0))
    # norm = 1.
    assert norm != 0
    return coors / norm, norm
