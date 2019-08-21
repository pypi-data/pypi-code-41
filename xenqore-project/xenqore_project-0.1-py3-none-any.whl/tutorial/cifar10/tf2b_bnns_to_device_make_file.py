from __future__ import absolute_import, division, print_function
import tensorflow as tf
import numpy as np
import xenqore
#import quant_layer
import matplotlib.pyplot as plt


from tensorflow.keras.activations import softmax
from tensorflow.keras.layers import Activation, Dropout, MaxPool2D, GlobalAveragePooling2D, BatchNormalization
from tensorflow.python.framework import function
import tensorflow.keras.backend as K
from tensorflow.keras.models import Sequential
from collections import OrderedDict
import codecs, json


def trans_tf_to_device(weight):

    tf_weight = weight.numpy()
    tf_weight = ((np.sign(np.sign(tf_weight + 1e-8)) + 1 ) / 2).astype(np.int)
    

    device_weight = []        
    print('weight.shape : ', len(tf_weight.shape))
    if len(tf_weight.shape) == 2:
        H = tf_weight.shape[0]
        W = tf_weight.shape[1]
        print('H : ', H)
        print('W : ', W)
        for i in range(H):
            for j in range(W):
                device_weight.append(tf_weight[i][j])
        #print(tf_weight[0])
        #print(device_weight[0:10])
    
    elif len(tf_weight.shape) == 4:
        print(tf_weight.shape)
        H = tf_weight.shape[0]
        W = tf_weight.shape[1]
        ic = tf_weight.shape[2]
        oc = tf_weight.shape[3]
        print('H : ', H)
        print('W : ', W)
        print('ic : ', ic)
        print('oc : ', oc)
        for i in range(oc):
            for j in range(ic):
                for k in range(H):
                    for n in range(W):
                        device_weight.append(tf_weight[k][n][j][i])
    device_weight = np.array(device_weight)
    
    return device_weight

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
# weight 0 -> -1 trans
#weight = np.where(weight_0 == 0, -1, 1)


batch_size = 50

#train_dataset = create_dataset(train_data, batch_size, True)
#test_dataset = create_dataset(test_data, batch_size, False)


new_model = tf.keras.models.load_model('cifar10_result/mymodel_407.h5')
#new_model = tf.keras.experimental.load_from_saved_model('t3_result/1560240552')
new_model.summary()





weight =[]
bias = []
bn_beta = []
bn_gamma = []
bn_mean = []
bn_variance = []


for var in new_model.variables:
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












tf_model_dict = OrderedDict()

epsilon = 1e-8
for i in range(len(weight)):


    if i == (len(weight) - 1):
        weight_file_path = 'save_file/fc0W.txt'
    else:
        weight_file_path = 'save_file/conv' + str(i) + 'W.txt'
    integer_bias_file_path = 'save_file/b' + str(i) + '_BNFb.txt'

    trans_weight_ordering = trans_tf_to_device(weight[i])
    if i == 0:
        tt = trans_shape_w(3,3,3,64,trans_weight_ordering)
        print(tt[0][0][0])
    

    
    #####

    #integer_bias = (bias[i].numpy() - bn_mean[i].numpy() + (np.sqrt(bn_variance[i].numpy() + epsilon) / bn_gamma[i].numpy()) * bn_beta[i].numpy())#.astype(np.int16)
    #integer_bias = integer_bias.astype(np.int16)
    integer_bias = bias[i].numpy() + ((np.sqrt(bn_variance[i].numpy()) * bn_beta[i].numpy()) / (bn_gamma[i].numpy() + 1e-8)) - bn_mean[i].numpy()
    Scale_sign = np.sign(np.sign(bn_gamma[i].numpy()) + 1e-8)
    integer_bias = np.round(integer_bias)
    integer_bias = Scale_sign * integer_bias
    integer_bias = integer_bias.astype(np.int16)
    print(integer_bias)

    with open(weight_file_path, 'w') as f:
        for t in trans_weight_ordering:
            f.write(str(t) + '\n')
    
    with open(integer_bias_file_path, 'w') as f:
        for t in integer_bias:
            f.write(str(t) + '\n')
    
    


    bias_list = bias[i].numpy().tolist()
    beta_list = bn_beta[i].numpy().tolist()
    gamma_list = bn_gamma[i].numpy().tolist()
    mean_list = bn_mean[i].numpy().tolist()
    variance_list = bn_variance[i].numpy().tolist()


    binary_weight = np.sign(np.sign(weight[i].numpy())+ 1e-8)
    tf_model_dict['binarized_weight' + str(i)] = binary_weight.tolist()
    tf_model_dict['integer_bias' + str(i)] = integer_bias.tolist()
    tf_model_dict['bias' + str(i)] = bias_list
    tf_model_dict['beta' + str(i)] = beta_list
    tf_model_dict['gamma' + str(i)] = gamma_list
    tf_model_dict['mean' + str(i)] = mean_list
    tf_model_dict['variance' + str(i)] = variance_list
    
    

#file_path = "save_file/tf_bnn_model_to_json.json"
#json.dump(tf_model_dict, codecs.open(file_path, 'w', encoding='utf-8'))




