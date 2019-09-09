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


import multiprocessing
import os
from collections import defaultdict
from pathlib import Path

import colorama
import h5py
import numpy as np
from tensorflow.keras.utils import to_categorical  # nopep8 pylint: disable=import-error
from tqdm import tqdm

from termcolor import cprint

from .aes import AES

colorama.init()

NUM_AVAILABLE_TRACES = 4
ATTACK_POINTS = ['key', 'sub_bytes_in', 'sub_bytes_out']


def load_shards(shards, num_stacked_traces, attack_point, target_byte,
                data_type, lstm_rows):
    "Load a collection of shards"
    num_shards = len(shards)
    pb = tqdm(total=num_shards,
              desc='loading %s shards' % data_type,
              unit='shard')
    data = defaultdict(list)
    data['metadata'] = defaultdict(list)
    for path in shards:
        params = [
            path, num_stacked_traces, attack_point, target_byte, lstm_rows
        ]  # nopep8
        # loading data
        shard_data = load_shard(params)

        # accumulating
        for k in ['x', 'y']:
            data[k].extend(shard_data[k])

        for k, v in shard_data['metadata'].items():
            data['metadata'][k].extend(v)

        pb.update()
    pb.close()
    # swapping x axis
    # (examples, traces, trace_data, 1) > (traces, examples, trace_data, 1)\
    data['x'] = np.array(data['x'])
    data['x'] = np.swapaxes(data['x'], 0, 1)
    data['metadata']['ct'] = np.array(data['metadata']['ct'])
    data['metadata']['pt'] = np.array(data['metadata']['pt'])
    data['metadata']['key'] = np.array(data['metadata']['key'])
    return data


def load_shard(params):
    shard_path, num_stacked_traces, attack_point, target_byte, lstm_rows = params
    h5_file = h5py.File(shard_path)
    data = {}
    round_idx = '1'
    # X
    # Input shape is: [num_traces, trace_value]
    # Output shape is: [num_key_pt, num_traces, trace_values]
    x = h5_file.get('x')
    num_pairs = (x.shape[0] // NUM_AVAILABLE_TRACES)
    # Reshape
    if lstm_rows:
        row_size = int(lstm_rows / num_pairs)
        x = np.reshape(x,
                       (num_pairs, NUM_AVAILABLE_TRACES, lstm_rows, row_size))
    else:
        # CNN
        x = np.reshape(x, [num_pairs, NUM_AVAILABLE_TRACES, -1])
        x = np.expand_dims(x, 3)  # CNN 1d
    # efficient way to clip X to n_traces
    data['x'] = x[:, :num_stacked_traces, :, :]
    # Y
    # The key is in the 'metadata' dataset, not the precomputed
    # intermediates in 'y' dataset
    # intemediate need to be remapped to match byte_idx
    t = h5_file.get('y')
    # find the right value
    if attack_point == 'key':
        values = h5_file['metadata']['key'][..., target_byte]
    else:
        dataset_byte_idx = str(AES.intermediate_map[target_byte])
        values = list(t[round_idx][attack_point][dataset_byte_idx])
    # recall there are NUM_AVAILABLE_TRACES per example so we need to 'jump'
    # some values as they are just duplicates.
    data['y'] = []
    for trace_idx in range(x.shape[0]):
        position = trace_idx * NUM_AVAILABLE_TRACES
        categorical_value = to_categorical(values[position], 256)
        data['y'].append(categorical_value)
    # metadata
    mt = h5_file.get('metadata')
    data['key'] = mt[0][1]
    metadata = {"ct": [], "pt": [], "key": []}
    for idx in range(x.shape[0]):
        metadata['pt'].append(mt[idx * NUM_AVAILABLE_TRACES][0])
        metadata['ct'].append(mt[idx * NUM_AVAILABLE_TRACES][2])

    key = data['key']
    array_with_single_key = np.expand_dims(key, axis=0)
    repeated_key = np.repeat(array_with_single_key, len(data['x']), axis=0)
    metadata['key'].extend(repeated_key)

    data['metadata'] = metadata
    return data


def load_data(dataset_name,
              data_type='train',
              num_shards=500,
              num_validation_shards=0,
              target_byte=0,
              attack_point='key',
              num_stacked_traces=1,
              lstm_rows=False):
    """Load the needed data to train or evaluate a given SCAAML attack
    Args:
        dataset_name (str): dataset to use
        data_type (str, optional): type of data to load. Either 'train' or
        'holdout'. Defaults to 'train'.
        num_shards (int, optional): number of shard to load -- each shard hold
        100 traces in train mode. 1000 in holdout.
        num_validation_shards (int, optional): number of validation shard to
        load -- each shard hold 100 traces.
        target_byte (int, optional): byte to attack. Defaults to 0.
        attack_point (str, optional): which attack point to target. Available
        points are: {'key', 'sub_byte_in', 'sub_byte_out'}. Defaults to 'key'.
        num_stacked_traces (int, optional): how many stacked trace to use for
        each example. Max is 4. Paper use 3. Defaults to 1.
        lsmt_rows (int, optional): num of LSTM cells. Defaults to 0. If 0 then
        data is returned in CNN version
    Returns
        list: x, y
    """
    # basic checks
    assert data_type in ['train', 'holdout']
    if data_type == 'holdout':
        cprint('[Warning] NEVER USE HOLDOUT FOR TRAINING', 'yellow')
    if data_type == 'holdout' and num_validation_shards:
        cprint(
            "[Error] holdout is for attack testing not training\
             -- validation_shards are meaningless in this setting", 'red')
        quit()
    assert attack_point in ATTACK_POINTS
    dataset_path = '%s/dataset/%s/' % (dataset_name, data_type)
    if not os.path.exists(dataset_path):
        cprint("[Error] %s path not found -- dataset downloaded?" %
               dataset_path, 'red')  # nopep8
        quit()
    cprint("[Loading %s data from: %s]" % (data_type, dataset_name), 'blue')
    shards = list(Path(dataset_path).glob('*.h5'))
    # shuffle shard
    np.random.shuffle(shards)
    available_shards = len(shards)
    cprint('|- %d available shards' % available_shards, 'green')
    # training shards
    num_shards = min(available_shards, num_shards)
    shards_to_load = shards[:num_shards]
    data = load_shards(shards_to_load, num_stacked_traces, attack_point,
                       target_byte, data_type, lstm_rows)
    results = [np.array(data['x']), np.array(data['y']), data['metadata']]
    if num_validation_shards:
        shards_to_load = shards[num_shards:num_shards + num_validation_shards]
        data = load_shards(shards_to_load, num_stacked_traces, attack_point,
                           target_byte, 'validation', lstm_rows)
        results.extend(
            [np.array(data['x']),
             np.array(data['y']), data['metadata']])
    # casting and returning
    return results


def load_attack_validation_data(dataset_name,
                                num_shards=500,
                                target_byte=0,
                                attack_point='key',
                                num_stacked_traces=1,
                                lstm_rows=False,
                                workers=0):
    """Load the needed data to train or evaluate a given SCAAML attack
    Args:
        dataset_name (str): dataset to use
        num_shards (int, optional): number of shard to load -- each shard hold
        100 traces in train mode. 1000 in holdout.
        target_byte (int, optional): byte to attack. Defaults to 0.
        attack_point (str, optional): which attack point to target. Available
        points are: {'key', 'sub_byte_in', 'sub_byte_out'}. Defaults to 'key'.
        num_stacked_traces (int, optional): how many stacked trace to use for
        each example. Max is 4. Paper use 3. Defaults to 1.
        lsmt_rows (int, optional): num of LSTM cells. Defaults to 0. If 0 then
        data is returned in CNN version
    Returns
        list 
    """

    data_type = 'holdout'
    dataset_path = '%s/dataset/%s/' % (dataset_name, data_type)

    # basic sanity checks.
    assert attack_point in ATTACK_POINTS
    if not os.path.exists(dataset_path):
        raise ValueError("Path not found '%s' -- is the dataset downloaded?" %
                         dataset_path)

    cprint("[Loading %s data from: %s]" % (data_type, dataset_name), 'blue')
    shards = list(Path(dataset_path).glob('*.h5'))

    available_shards = len(shards)
    num_shards = min(available_shards, num_shards)
    shards_to_load = shards[:num_shards]
    cprint('|- %d available shards' % available_shards, 'green')
    cprint('|- %d shards to load' % num_shards, 'green')

    output_shards = []
    params = []

    for shard in shards_to_load:
        params.append(
            (shard, num_stacked_traces, attack_point, target_byte, lstm_rows))

    if workers:
        pool = multiprocessing.Pool()
        for shard in tqdm(pool.imap_unordered(load_shard, params),
                          desc="Loading",
                          unit=" Shard",
                          total=len(params)):
            output_shards.append(shard)
    else:
        for shard_params in tqdm(params, desc="Loading", unit=" Shard"):
            output_shards.append(load_shard(shard_params))

    return output_shards
