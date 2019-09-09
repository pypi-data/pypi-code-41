"""
Jacob Thompson

Layers.py
"""

from collections import defaultdict
from copy import copy

import numpy as np
from scipy.signal import correlate

import JT.Initializers
import JT.Gradients

class Layer:
    def InitWeights(self):
        pass
    def Forward(self, z_in):
        pass
    def Backward(self, core_in, learn_rate):
        pass
    def Predict(self, z_in):
        pass

class Hidden_Layer(Layer):
    def __init__(self, activation, size, normalize_output = None, next_layer = None, prev_layer = None, batch_norm_parameter = 0.1, initializer = JT.Initializers.Initializer(), gradient = JT.Gradients.Gradient()):
        self.activation = activation
        self.next_layer = next_layer
        self.prev_layer = prev_layer
        self.size = size
        self.normalize_output = normalize_output
        self.InitWeights()
        self.mu_h = 0
        self.sig_h = 1
        self.alpha = batch_norm_parameter
        self.gradient = gradient
        self.initializer = initializer

        
    def Forward(self, z_in):
        self.z_in = z_in
        self.h = self.z_in @ self.weights + self.bias
        if self.normalize_output == 'before':
            mu_batch     = np.mean(self.h, axis = 0, keepdims = True)
            sig_batch    = np.std(self.h, axis = 0, keepdims = True)
            self.mu_h    = self.alpha * mu_batch  + (1 - self.alpha) * self.mu_h
            self.sig_h   = self.alpha * sig_batch + (1 - self.alpha) * self.sig_h
            self.denom   = np.sqrt(self.sig_h ** 2 + 1e-7)
            self.h_bar_0 = (self.h - self.mu_h) / self.denom
            self.h_bar_1 = self.gamma * self.h_bar_0 + self.beta
            self.z_out   = self.activation(self.h_bar_1)
            
        else:
            self.z_out = self.activation(self.h)
        
        if self.normalize_output == 'after':
            self.mu_z = np.mean(self.z_out, axis = 1, keepdims = True)
            self.sig_z = np.std(self.z_out, axis = 1, keepdims = True)
            self.denom = np.sqrt(self.sig_z ** 2 )
        
            self.z_out = (self.z_out - self.mu_z) / self.denom    
        return self.next_layer.Forward(self.z_out)
        
        
    def Predict(self, z_in):
        h = z_in @ (self.weights - self.gradients['weights'].change) + (self.bias - self.gradients['bias'].change)
        
        if self.normalize_output == 'before':
            h_bar_0 = (h - self.mu_h) / self.denom
            h_bar_1 = (self.gamma - self.gradients['gamma'].change) * h_bar_0 + (self.beta - self.gradients['beta'].change)
            z_out   = self.activation(h_bar_1)
        else:
            z_out = self.activation(h)
        
        if self.normalize_output == 'after':
            z_out = (z_out - self.mu_z) / self.denom
        
        return self.next_layer.Predict(z_out)
        
    def Backward(self, core_in, learn_rate):
        core = core_in * self.activation.D(self.h)
        
        
        if not (self.normalize_output is None):

            gamma_grad = np.sum(core * self.h_bar_0, axis = 0, keepdims = True)
            beta_grad = np.sum(core, axis = 0, keepdims = True)

            core *= (self.gamma / self.denom)
            
            self.gamma -= self.gradients['gamma'].Evaluate(gamma_grad, learn_rate)
            self.beta -= self.gradients['beta'].Evaluate(beta_grad, learn_rate)
            
            
        core_out = core @ self.weights.T
        
        weights_grad = self.z_in.T @ core
        bias_grad = np.sum(core, axis = 0, keepdims = True)
        self.weights -= self.gradients['weights'].Evaluate(weights_grad, learn_rate)
        self.bias -= self.gradients['bias'].Evaluate(bias_grad, learn_rate)
        
        self.prev_layer.Backward(core_out, learn_rate)
    
    def InitWeights(self):
        if not self.prev_layer is None:
        
            self.weights = self.initializer.Initialize(self.prev_layer.size, self.size)
            
            self.bias = np.random.randn(1, self.size)
            self.gamma = np.random.randn(1, self.size)
            self.beta = np.random.randn(1, self.size)

            self.gradients = defaultdict(lambda: copy(self.gradient))
        
    
        
class Output_Layer(Layer):
    def __init__(self, size, activation, prev_layer = None, initializer = JT.Initializers.Initializer()):
        self.size = size
        self.prev_layer = prev_layer
        self.activation = activation
        self.initializer = initializer
        
    def Forward(self, z_in):
        self.z_in = z_in
        self.h = self.z_in @ self.weights + self.bias
        self.p_hat = self.activation(self.h)
        return self.p_hat
        
    def Predict(self, z_in):
        h = z_in @ self.weights + self.bias
        p_hat = self.activation(h)
        return p_hat
        
    def Backward(self, p_hat, y, learn_rate):
        core = (p_hat - y)
        core_out = core @ self.weights.T
        self.weights -= learn_rate * self.z_in.T @ core
        self.bias -= learn_rate * np.sum(core, axis = 0, keepdims = True)
        
        self.prev_layer.Backward(core_out, learn_rate)
        
    def InitWeights(self):
        if not self.prev_layer is None:
            self.weights = self.initializer.Init(self.prev_layer.size, self.size)
            self.bias = np.random.randn(1, self.size)
        
class Input_Layer(Layer):
    def __init__(self, size, next_layer = None):
        self.size = size
        self.next_layer = next_layer
        
    def Forward(self, x):
        if x.shape[1] != self.size:
            raise NameError('Input not correct shape')
            
        return self.next_layer.Forward(x)
        
    def Backward(self, *args):
        pass
        
    def Predict(self, x):
        if x.shape[1] != self.size:
            raise NameError('Input not correct shape')
        
        return self.next_layer.Predict(x)

class Normalize_Layer(Layer):
    """
    ADD GAMMA AND BETA
    """
    def __init__(self, eta = 1e-8, next_layer = None, prev_layer = None):
        self.eta = eta
        self.next_layer = next_layer
        self.prev_layer = prev_layer
    
    def Forward(self, z_in):
        self.z_in = z_in
        self.mu = np.mean(self.z_in, axis = 1, keepdims = True)
        self.sig = np.std(self.z_in, axis = 1, keepdims = True)
        self.denominator = np.sqrt(self.sig ** 2 + self.eta)
        
        self.z_out = (self.z_in - self.mu) / self.denominator
        return self.next_layer.Forward(self.z_out)
        
    def Backward(self, core_in, learn_rate):
        core_out = core_in / self.denominator
        self.prev_layer.Backward(core_out, learn_rate)
        
    def Predict(self, z_in):
        self.z_out = (z_in - self.mu) / self.denominator
        return self.next_layer.Forward(self.z_out)
        
    def InitWeights(self):
        self.size = self.prev_layer.size
            
class Noise_Injector(Layer):
    def __init__(self, noise_param = 0.1, moving_avg_param = 0.1, next_layer = None, prev_layer = None):
        self.noise_param = noise_param
        self.moving_avg_param = moving_avg_param
        self.next_layer = next_layer
        self.prev_layer = prev_layer
        self.mu = 0
        self.sigma = 1
        
        
    def Forward(self, z_in):
        mu_batch     = np.mean(z_in, axis = 0, keepdims = True)
        sig_batch    = np.std(z_in, axis = 0, keepdims = True)
        
        self.mu      = self.moving_avg_param * mu_batch  + (1 - self.moving_avg_param) * self.mu
        self.sigma     = self.moving_avg_param * sig_batch + (1 - self.moving_avg_param) * self.sigma
        
        noise = self.noise_param * (np.random.randn(*z_in.shape) * self.sigma + self.mu)
        z_out = z_in + noise
        return self.next_layer.Forward(z_out)
        
    def Backward(self, core_in, learn_rate):
        self.prev_layer.Backward(core_in, learn_rate)
        
    def Predict(self, z_in):
        return self.next_layer.Predict(z_in)
        
    def InitWeights(self):
        self.size = self.prev_layer.size
        
class Dropout_Layer(Layer):
    def __init__(self, dropout_rate = 0.1, next_layer = None, prev_layer = None):
        self.dropout_rate = dropout_rate
        self.next_layer = next_layer
        self.prev_layer = prev_layer
        
    def Forward(self, z_in):
        z_out = z_in * (np.random.random(z_in.shape) > self.dropout_rate)
        return self.next_layer.Forward(z_out)
        
    def Backward(self, core_in, learn_rate):
        self.prev_layer.Backward(core_in, learn_rate)
        
    def Predict(self, z_in):
        z_out = z_in * (1 - self.dropout_rate)
        return self.next_layer.Predict(z_out)
        
    def InitWeights(self):
        self.size = self.prev_layer.size
        
class Convolution_Layer(Layer):
    def __init__(self, kernel_size, kernel_num, next_layer = None, prev_layer = None):
        self.kernel_size = kernel_size
        self.kernel_num = kernel_num
        self.next_layer = next_layer
        self.prev_layer = prev_layer

    def InitWeights(self):
        self.depth = self.prev_layer.kernel_num
        self.kernels = np.random.rand(self.kernel_num, self.kernel_size, self.kernel_size, self.depth)

    def Forward(self, z_in):
        out = []
        for kernel in self.kernels:
            out.append(correlate(z_in, kernel, mode = 'same')[:, :, (self.depth // 2):-(self.depth // 2)])
        return np.dstack(out)

    def Backward(self, core_in, learn_rate):
        # TODO: Write this backward method
        pass
    







