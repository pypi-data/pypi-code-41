# Copyright (C) 2018-2019 by nepes Corp. All Rights Reserved
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
 
"""
Test script for the Neuromem API library.

"""


import xenqore
import numpy as np
import tensorflow as tf

saved_model = 'cifar10_result/mymodel_407.h5'
model = tf.keras.models.load_model(saved_model)
model.summary()


def create_dataset(data, batch_size, training):
    '''Dataset remake to use batch, repeat and shuffle method.'''

    images, labels = data
    dataset = tf.data.Dataset.from_tensor_slices((images, labels))
    dataset = dataset.repeat()
    if training:
        dataset = dataset.shuffle(10000)
    dataset = dataset.batch(batch_size)
    return dataset

# networks parameter setting
network_config = xenqore.utils.NetworkConfig()
print('####### NetworkConfig ######')
print('batch_size : ', network_config.batch_size)
print('initial_lr : ', network_config.initial_lr)
print('var_decay  : ', network_config.var_decay)
print('epochs     : ', network_config.epochs)
print('classes    : ', network_config.classes)
print('############################')

# dataset load and creat tensorflow dataset format
train_data, valid_data = tf.keras.datasets.cifar10.load_data()
train_dataset = create_dataset(train_data, network_config.batch_size, True)
valid_dataset = create_dataset(valid_data, network_config.batch_size, False)

model.evaluate(valid_dataset, steps=valid_data[1].shape[0] // network_config.batch_size, verbose=1)

#my_array = np.array([1,2,3,4,5])
#np.savetxt("my_array.txt", my_array, fmt="%d", delimiter=",", newline="\n")
xenqore.device.transform_model_to_device(model)