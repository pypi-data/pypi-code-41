
import torch.nn as nn

activation_dict = {'relu' : nn.ReLU(), 'linear' : None}

def Dense(no_of_neurons,activation= 'linear'):
    return 'Dense',no_of_neurons, activation_dict[activation]

def Dropout(p):
    return 'Dropout', p ,None





