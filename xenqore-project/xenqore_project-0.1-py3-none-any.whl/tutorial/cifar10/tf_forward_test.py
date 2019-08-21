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

import tensorflow.keras.backend as K

from tensorflow.keras.layers import Dense, Dropout, Activation, BatchNormalization, MaxPooling2D, GlobalAveragePooling2D

#tf.enable_eager_execution()
tf.executing_eagerly()



saved_model = 'cifar10_result/mymodel_407.h5'
model = tf.keras.models.load_model(saved_model)
model.summary()

def compute_conv(input, weight, bias, gamma, beta, mean, variance):
    conv = K.conv2d(input,
                    weight, 
                    strides=(1, 1), 
                    padding='same', 
                    data_format='channels_last',
                    dilation_rate=(1,1))

    
    conv_out = tf.nn.bias_add(conv, bias, data_format='NHWC')
    #conv_sum_bn = gamma * (conv - mean) / np.sqrt(variance + 1e-4) + beta
    #conv_sum_bn = conv + beta
    #tf_mean, tf_variance = tf.nn.moments(conv_out, axes=[0, 1, 2])

    """

    conv_sum_bn = tf.nn.batch_normalization(conv_out, mean,
                                            variance,
                                            beta, #offset,
                                            gamma, #scale,
                                            1e-4, #variance_epsilon,
                                            )

    cc = gamma * ((conv_out - mean) / np.sqrt(variance + 1e-4)) + beta

    #print('*'*50)
    #print(conv_sum_bn)
    #print(cc)

    


    return(conv_sum_bn)
    """
    return conv_out

"""
def compute_conv(input_data, weight, bias, gamma, beta, mean, variance):
    #print(input_data.shape)
    #print(weight.shape)
    #print(bias.shape)
    #print(gamma.shape)
    #print(beta.shape)
    #print(mean.shape)
    #print(variance.shape)
    conv = K.conv2d(input_data,
                    weight, 
                    strides=(1, 1), 
                    padding='same', 
                    data_format='channels_last',
                    dilation_rate=(1,1)
                    )

    
    BatchBias1d = bias + ((np.sqrt(variance) * beta) / (gamma + 1e-8)) - mean
    #Scale_sign = np.sign(np.sign(gamma) + 1e-8)
    #BatchBias1d = Scale_sign * BatchBias1d

    conv_sum_bn = conv + BatchBias1d

    return(conv_sum_bn)
"""
"""
def compute_conv(input, weight, bn=None):
    conv = K.conv2d(input,
                    weight, 
                    strides=(1, 1), 
                    padding='same', 
                    data_format='channels_last',
                    dilation_rate=(1,1))

    if not bn is None:
        conv_sum_bn = conv + bn
        return(conv_sum_bn)
    else:
        return(conv)
"""

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
(x_train, y_train), (x_valid, y_valid) = tf.keras.datasets.cifar10.load_data()

train_dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train))
train_dataset = train_dataset.shuffle(10000).batch(network_config.batch_size).repeat()
valid_dataset = tf.data.Dataset.from_tensor_slices((x_valid, y_valid))
valid_dataset = valid_dataset.batch(network_config.batch_size).repeat()




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



weight_0 = tf.cast(weight[0].numpy(), tf.float32) 
weight_1 = tf.cast(weight[1].numpy(), tf.float32) 
weight_2 = tf.cast(weight[2].numpy(), tf.float32) 
weight_3 = tf.cast(weight[3].numpy(), tf.float32) 
weight_4 = tf.cast(weight[4].numpy(), tf.float32) 
weight_5 = tf.cast(weight[5].numpy(), tf.float32) 

bias_0 = tf.cast(bias[0].numpy(), tf.float32) 
bias_1 = tf.cast(bias[1].numpy(), tf.float32) 
bias_2 = tf.cast(bias[2].numpy(), tf.float32) 
bias_3 = tf.cast(bias[3].numpy(), tf.float32) 
bias_4 = tf.cast(bias[4].numpy(), tf.float32) 
bias_5 = tf.cast(bias[5].numpy(), tf.float32) 
bias_6 = tf.cast(bias[6].numpy(), tf.float32) 

beta_0 = tf.cast(bn_beta[0].numpy(), tf.float32) 
beta_1 = tf.cast(bn_beta[1].numpy(), tf.float32) 
beta_2 = tf.cast(bn_beta[2].numpy(), tf.float32) 
beta_3 = tf.cast(bn_beta[3].numpy(), tf.float32) 
beta_4 = tf.cast(bn_beta[4].numpy(), tf.float32) 
beta_5 = tf.cast(bn_beta[5].numpy(), tf.float32) 
beta_6 = tf.cast(bn_beta[6].numpy(), tf.float32) 

gamma_0 = tf.cast(bn_gamma[0].numpy(), tf.float32) 
gamma_1 = tf.cast(bn_gamma[1].numpy(), tf.float32) 
gamma_2 = tf.cast(bn_gamma[2].numpy(), tf.float32) 
gamma_3 = tf.cast(bn_gamma[3].numpy(), tf.float32) 
gamma_4 = tf.cast(bn_gamma[4].numpy(), tf.float32) 
gamma_5 = tf.cast(bn_gamma[5].numpy(), tf.float32) 
gamma_6 = tf.cast(bn_gamma[6].numpy(), tf.float32) 

mean_0 = tf.cast(bn_mean[0].numpy(), tf.float32)
mean_1 = tf.cast(bn_mean[1].numpy(), tf.float32)
mean_2 = tf.cast(bn_mean[2].numpy(), tf.float32)
mean_3 = tf.cast(bn_mean[3].numpy(), tf.float32)
mean_4 = tf.cast(bn_mean[4].numpy(), tf.float32)
mean_5 = tf.cast(bn_mean[5].numpy(), tf.float32)
mean_6 = tf.cast(bn_mean[6].numpy(), tf.float32)

variance_0 = tf.cast(bn_variance[0].numpy(), tf.float32)
variance_1 = tf.cast(bn_variance[1].numpy(), tf.float32)
variance_2 = tf.cast(bn_variance[2].numpy(), tf.float32)
variance_3 = tf.cast(bn_variance[3].numpy(), tf.float32)
variance_4 = tf.cast(bn_variance[4].numpy(), tf.float32)
variance_5 = tf.cast(bn_variance[5].numpy(), tf.float32)
variance_6 = tf.cast(bn_variance[6].numpy(), tf.float32)

fc = tf.cast(weight[6].numpy(), tf.float32)


"""
output1 = model.get_layer(name='Qconv2D_0')(tf.cast(x_valid[:1], tf.float32))
print(output1)
output2 = compute_conv(x_valid[:1], weight_0, bias_0, gamma_0, beta_0, mean_0, variance_0)
print(output2)
"""

#model.evaluate(valid_dataset, steps=x_valid.shape[0] // 50, verbose=1)



"""
batch_size = 50
test_step = int(x_valid.shape[0]/batch_size)
count = 0
for i in range(test_step):    
    #output = compute_conv(x_valid[i*batch_size:i*batch_size+batch_size], weight_0, bn_0)
    output = compute_conv(x_valid[i*batch_size:i*batch_size+batch_size], weight_0, bias_0, gamma_0, beta_0, mean_0, variance_0)
    output = np.sign(np.sign(output) + 1e-8)

    #output = compute_conv(output, weight_1, bn_1)
    output = compute_conv(output, weight_1, bias_1, gamma_1, beta_1, mean_1, variance_1)
    output = np.sign(np.sign(output) + 1e-8)
    output = MaxPooling2D()(np.copy(output))

    #output = compute_conv(output, weight_2, bn_2)
    output = compute_conv(output, weight_2, bias_2, gamma_2, beta_2, mean_2, variance_2)
    output = np.sign(np.sign(output) + 1e-8)
    #output = compute_conv(output, weight_3, bn_3)
    output = compute_conv(output, weight_3, bias_3, gamma_3, beta_3, mean_3, variance_3)
    output = np.sign(np.sign(output) + 1e-8)
    output = MaxPooling2D()(np.copy(output))

    #output = compute_conv(output, weight_4, bn_4)
    output = compute_conv(output, weight_4, bias_4, gamma_4, beta_4, mean_4, variance_4)
    output = np.sign(np.sign(output) + 1e-8)
    #output = compute_conv(output, weight_5, bn_5)
    output = compute_conv(output, weight_5, bias_5, gamma_5, beta_5, mean_5, variance_5)
    output = np.sign(np.sign(output) + 1e-8)
    output = MaxPooling2D()(np.copy(output))
    output = GlobalAveragePooling2D()(np.copy(output))
    output = np.sign(np.sign(output) + 1e-8)

    #output = np.dot(output, fc) + bn_6
    output = tf.matmul(output, fc)
    #output = K.bias_add(output, b_6)
    
    #print(output.dtype)

    #output = ((gamma_6 * (np.dot(output, fc) + b_6 - mean_6)) / (np.sqrt(variance_6 + 1e-4))) + beta_6
    #output = gamma_6 * (np.dot(output, fc) + b_6) + beta_6
    #tf_mean_6, tf_variance_6 = tf.nn.moments(output, axes=[0])

    

    #BatchBias1d_6 = bias_6 + ((np.sqrt(variance_6 + 1e-4) * beta_6) / (gamma_6)) - mean_6
    #Scale_sign_6 = np.sign(np.sign(gamma_6) + 1e-8)
    #BatchBias1d_7 = Scale_sign_6 * BatchBias1d_6

    #output = output + BatchBias1d_6#.astype(np.int32)
    


    


    output = tf.nn.batch_normalization(output, mean_6,
                                            variance_6,
                                            beta_6, #offset,
                                            gamma_6, #scale,
                                            1e-4 #variance_epsilon,
                                            )
    

    #output = output.argmax(axis=1)
    output = np.argmax(output, axis=1)

    target = np.copy(y_valid[i*batch_size:i*batch_size+batch_size])

        
    for j in range(batch_size):
        print(output[j], target[j])
        if output[j] == target[j]:
            count += 1
    
    if i % 10 == 0:
        print(str(i)+'/'+str(test_step), '\t', count/(batch_size*(i+1)))

print(count/x_valid.shape[0])

"""