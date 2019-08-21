
from __future__ import absolute_import, division, print_function
import tensorflow as tf
import numpy as np
import os

import tensorflow.keras.backend as K
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.layers import Dense, Dropout, Activation, BatchNormalization, MaxPooling2D, GlobalAveragePooling2D


def trans_shape_in(N, H, W, C, data):
        ts = np.zeros((N,H,W,C))
        count = 0
        for i in range(N):
            for j in range(H):
                for k in range(W):
                    for n in range(C):
                        ts[i][j][k][n] = data[count]
                        count += 1
        ts = np.array(ts, np.float32)
        return ts


def trans_shape_w(H, W, ic, oc, data):
        ts = np.zeros((H,W,ic,oc))
        count = 0
        for i in range(oc):
            for j in range(ic):
                for k in range(H):
                    for n in range(W):
                        ts[k][n][j][i] = data[count]
                        count += 1
        ts = np.array(ts, np.float32)
        return ts


def compute_conv(input, weight, integer_bias=None):
    conv = K.conv2d(input,
                    weight, 
                    strides=(1, 1), 
                    padding='same', 
                    data_format='channels_last',
                    dilation_rate=(1,1))

    if not integer_bias is None:
        conv_sum_bn = conv + integer_bias
        return(conv_sum_bn)
    else:
        return(conv)
############################################################################################################
##   train, valid data set
(x_train, y_train), (x_valid, y_valid) = cifar10.load_data()

x_train = x_train.astype('float32')
y_train = y_train.astype('int32')
x_valid = x_valid.astype('float32')
y_valid = y_valid.astype('int32')

y_train = np.squeeze(y_train)
y_valid = np.squeeze(y_valid)

print('*'*100)
print('numpy raw data')
print('train_x(type, dtype, shape) : ', type(x_train),'\t', x_train.dtype,'\t', x_train.shape)
print('train_y(type, dtype, shape) : ', type(y_train),'\t', y_train.dtype,'\t', y_train.shape)
print('valid_x(type, dtype, shape)  : ', type(x_valid),'\t', x_valid.dtype,'\t', x_valid.shape)
print('valid_y(type, dtype, shape)  : ', type(y_valid),'\t', y_valid.dtype,'\t', y_valid.shape)
print('*'*100)

############################################################################################################

# weight, bn, fc load
weight_0_path = os.path.join('device_group/conv0W.txt')
weight_1_path = os.path.join('device_group/conv1W.txt')
weight_2_path = os.path.join('device_group/conv2W.txt')
weight_3_path = os.path.join('device_group/conv3W.txt')
weight_4_path = os.path.join('device_group/conv4W.txt')
weight_5_path = os.path.join('device_group/conv5W.txt')
bn_0_path = os.path.join('device_group/b0_BNFb.txt')
bn_1_path = os.path.join('device_group/b1_BNFb.txt')
bn_2_path = os.path.join('device_group/b2_BNFb.txt')
bn_3_path = os.path.join('device_group/b3_BNFb.txt')
bn_4_path = os.path.join('device_group/b4_BNFb.txt')
bn_5_path = os.path.join('device_group/b5_BNFb.txt')
bn_6_path = os.path.join('device_group/b6_BNFb.txt')
fc_path = os.path.join('device_group/fc0W.txt')


weight_0 = np.loadtxt(weight_0_path)
weight_1 = np.loadtxt(weight_1_path)
weight_2 = np.loadtxt(weight_2_path)
weight_3 = np.loadtxt(weight_3_path)
weight_4 = np.loadtxt(weight_4_path)
weight_5 = np.loadtxt(weight_5_path)
bn_0 = np.loadtxt(bn_0_path)
bn_1 = np.loadtxt(bn_1_path)
bn_2 = np.loadtxt(bn_2_path)
bn_3 = np.loadtxt(bn_3_path)
bn_4 = np.loadtxt(bn_4_path)
bn_5 = np.loadtxt(bn_5_path)
bn_6 = np.loadtxt(bn_6_path)
fc = np.loadtxt(fc_path)

# weight 0 -> -1 trans
weight_0 = np.where(weight_0 == 0, -1, 1)
weight_1 = np.where(weight_1 == 0, -1, 1)
weight_2 = np.where(weight_2 == 0, -1, 1)
weight_3 = np.where(weight_3 == 0, -1, 1)
weight_4 = np.where(weight_4 == 0, -1, 1)
weight_5 = np.where(weight_5 == 0, -1, 1)

# fc 0 -> -1 trans
#fc = np.where(fc == 0, -1, 1)
#fc = np.where(fc == 0, -256, 256)

# weight, fc reshape
weight_0 = trans_shape_w(3,3,3,64, weight_0)
weight_1 = trans_shape_w(3,3,64,64, weight_1)
weight_2 = trans_shape_w(3,3,64,128, weight_2)
weight_3 = trans_shape_w(3,3,128,128, weight_3)
weight_4 = trans_shape_w(3,3,128,256, weight_4)
weight_5 = trans_shape_w(3,3,256,256, weight_5)
fc = fc.reshape((256,10), order='F')


batch_size = 50
test_step = int(x_valid.shape[0]/batch_size)
count = 0
for i in range(test_step):    
    output = compute_conv(x_valid[i*batch_size:i*batch_size+batch_size], weight_0, integer_bias=bn_0)
    output = np.sign(np.sign(output) + 1e-8)
    output = compute_conv(output, weight_1, integer_bias=bn_1)
    output = np.sign(np.sign(output) + 1e-8)
    output = MaxPooling2D()(np.copy(output))

    output = compute_conv(output, weight_2, integer_bias=bn_2)
    output = np.sign(np.sign(output) + 1e-8)
    output = compute_conv(output, weight_3, integer_bias=bn_3)
    output = np.sign(np.sign(output) + 1e-8)
    output = MaxPooling2D()(np.copy(output))

    output = compute_conv(output, weight_4, integer_bias=bn_4)
    output = np.sign(np.sign(output) + 1e-8)
    output = compute_conv(output, weight_5, integer_bias=bn_5)
    output = np.sign(np.sign(output) + 1e-8)
    output = MaxPooling2D()(np.copy(output))
    output = GlobalAveragePooling2D()(np.copy(output))
    output = np.sign(np.sign(output) + 1e-8)

    output = np.dot(output, fc) + bn_6

    #print(output)

    output = output.argmax(axis=1)

    target = np.copy(y_valid[i*batch_size:i*batch_size+batch_size])

        
    for j in range(batch_size):
        if output[j] == target[j]:
            count += 1
    
    if i % 10 == 0:
        print(str(i)+'/'+str(test_step), '\t', count/(batch_size*(i+1)))

print(count/x_valid.shape[0])