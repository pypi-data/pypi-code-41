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
Designed Neural Networks structure for the Xenqore API library package for Python.

Copyright (C) 2018-2019 by nepes Corp. All Rights Reserved

To use, simply 'import xenqore'
"""


import os

import xenqore

import numpy as np

import tensorflow as tf


def trans_weight_ordering(weight):
    """The weight ordering transform tensorflow to device"""

    tf_weight = weight.numpy()
    tf_weight = ((np.sign(np.sign(tf_weight) + 1e-8) + 1 ) / 2).astype(np.int)
    
    device_weight = []        
    print('weight.shape : ', len(tf_weight.shape))
    if len(tf_weight.shape) == 2:
        
        H = tf_weight.shape[0]
        W = tf_weight.shape[1]        
        for i in range(W):
            for j in range(H):
                device_weight.append(tf_weight[j][i])            

    elif len(tf_weight.shape) == 4:
        
        H = tf_weight.shape[0]
        W = tf_weight.shape[1]
        ic = tf_weight.shape[2]
        oc = tf_weight.shape[3]        
        for i in range(oc):
            for j in range(ic):
                for k in range(H):
                    for n in range(W):
                        device_weight.append(tf_weight[k][n][j][i])

    device_weight = np.array(device_weight)
    
    return device_weight


def transform_model_to_device(model, save_path='DeviceSavePath'):
    """
    integer bias is made by using batch_normalization's beta, gamma, mean and variance.  
    Each layer's weight and integer bias based on tensorflow are transformed to use in device.
    """
    
    try:
        if not(os.path.isdir(save_path)):
            os.makedirs(os.path.join(save_path))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print('Failed to create directory!!!!')
            raise

    weight =[]
    bias = []
    bn_beta = []
    bn_gamma = []
    bn_mean = []
    bn_variance = []

    for var in model.variables:
        if 'kernel' in var.name:
            weight.append(var)
        elif 'bias' in var.name:
            bias.append(var)
        elif 'beta' in var.name:
            bn_beta.append(var)
        elif 'gamma' in var.name:
            bn_gamma.append(var)
        elif 'mean' in var.name:
            bn_mean.append(var)
        elif 'variance' in var.name:
            bn_variance.append(var)
    
    for i in range(len(weight)):
        if i == (len(weight) - 1):
            weight_file_path = os.path.join(save_path, 'fc0W.txt')
            
        else:
            weight_file_path = os.path.join(save_path, 'conv' + str(i) + 'W.txt')            
        
        integer_bias_file_path = os.path.join(save_path, 'b' + str(i) + '_BNFb.txt')
        
        trans_weight = trans_weight_ordering(weight[i])

        
        integer_bias = bias[i].numpy() + ((np.sqrt(bn_variance[i].numpy() + 0.001) * bn_beta[i].numpy()) / (bn_gamma[i].numpy()) ) - bn_mean[i].numpy()
        Scale_sign = np.sign(np.sign(bn_gamma[i].numpy()) + 1e-8)
        integer_bias = Scale_sign * integer_bias
        integer_bias = np.floor(integer_bias)

        integer_bias = np.where(integer_bias == np.inf, 9999, integer_bias)
        integer_bias = integer_bias.astype(np.int16)


        np.savetxt(weight_file_path, trans_weight, fmt="%d", delimiter=",", newline="\n")
        np.savetxt(integer_bias_file_path, integer_bias, fmt="%d", delimiter=",", newline="\n")
        
        
    

