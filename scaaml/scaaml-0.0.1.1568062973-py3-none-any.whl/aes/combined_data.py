# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from collections import defaultdict, namedtuple
from multiprocessing import Pool
from pathlib import Path

import colorama
import h5py
import numpy as np
import tensorflow as tf
from tensorflow.keras.utils import to_categorical  # nopep8 pylint: disable=import-error

from termcolor import cprint

from .aes import AES

try:
    class_name = get_ipython().__class__.__name__
    if "Terminal" in class_name:
        IS_NOTEBOOK = False
    else:
        IS_NOTEBOOK = True

except NameError:
    IS_NOTEBOOK = False

if IS_NOTEBOOK:
    from tqdm import tqdm_notebook as tqdm
    from IPython.display import HTML
else:
    from tqdm import tqdm

colorama.init()

# Create a named tuple for shard data, for ease of passing the data around.
#Shard = namedtuple("Shard", ["x", "y", "key", "ct", "pt"])


class Shard(object):
    def __init__(self, x, y, key, ct, pt, predictions=None):
        self.x = x
        self.y = y
        self.key = key
        self.ct = ct
        self.pt = pt
        self.predictions = predictions

        self.__iterindex = 0

    def __len__(self):
        return len(self.x)

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        self.__iterindex


def load_shard(filename, attack_point, byte_idx):
    """Load a single shard of data from an HDF5 file.

    Arguments:
        filename {str} - - Filename of the HDF5 file to load.
        model_type {str} - - "cnn" | "lstm"
        lstm_rows {int} - - Number of "rows" of data to format the input trace into.
        attack_point {str} - - "key" | "sub_bytes_in" | "sub_bytes_out" - the type
            of byte we are trying to attack.

    Returns:
        Shard - - A Shard containing the data.
    """

    with h5py.File(filename, "r") as train:
        x_train = train['x'][:]
        y_train = train[attack_point][:, byte_idx][:]

        key = train['key'][:]
        ct_train = train['ciphertext'][:]
        pt_train = train['plaintext'][:]

        return Shard(x=x_train, y=y_train, key=key, ct=ct_train, pt=pt_train)


def shard_to_dict(batch):
    """Given a batch of data from the holdout_batch_generator, transform it into
    a simple dictionary of np.ndarrays.

    Arguments:
        batch {list[tuple]} -- The batch of items.

    Returns:
        dict[str -> np.ndarray] -- the dictionary of name to array.
    """

    output = defaultdict(list)

    for idx in range(len(batch)):
        output['x'].append(batch.x[idx])
        output['y'].append(batch.y[idx])
        output['key'].append(batch.key[idx])
        output['ct'].append(batch.ct[idx])
        output['pt'].append(batch.pt[idx])

    for k, v in output.items():
        output[k] = np.array(v)

    return output


def holdout_batch_generator(holdout_shard):
    """Given a holdout shard, generate a set of batches, where each batch
    contains the data for a single key.

    Arguments:
        holdout_shard {Shard} -- Shard containing holdout data.
        
    Returns:
        generator -- Generator which produces one batch of items at a time.
    """
    last = None

    pb = tqdm(desc="Computing holdout batches", total=holdout_shard.x.shape[0])

    shard = Shard([], [], [], [], [], [])

    for x, y, key, ct, pt in zip(holdout_shard.x, holdout_shard.y,
                                 holdout_shard.key, holdout_shard.ct,
                                 holdout_shard.pt):
        pb.update(1)

        if last is None or not np.array_equal(last, key):
            last = key

            old_shard = shard
            shard = Shard([], [], [], [], [], [])
            if len(old_shard):
                yield old_shard

        shard.x.append(x)
        shard.y.append(y)
        shard.key.append(key)
        shard.ct.append(ct)
        shard.pt.append(pt)

    if len(shard):
        yield shard

    pb.close()
    return None
