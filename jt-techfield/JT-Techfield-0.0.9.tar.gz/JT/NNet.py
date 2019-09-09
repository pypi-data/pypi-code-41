"""
Jacob Thompson
NNet.py
"""

import numpy as np
import matplotlib.pyplot as plot

import JT.Layers

class Neural_Network:
	def __init__(self, x, y, loss_func, echo = False):
		self.layer_list = []
		self.x = x
		self.y = y
		
		self.loss_func = loss_func
		self.activation = self.loss_func.activation
		
		self.input_layer = JT.Layers.Input_Layer(x.shape[1])
		self.output_layer = JT.Layers.Output_Layer(y.shape[1], self.activation)
	
		self.echo = echo
		
	def Echo(self, *args):
		if self.echo:
			args = list(args)
			for i in range(len(args)):
				if type(args[i]) != 'str':
					args[i] = str(args[i])
			print(' '.join(args))
	
	def AddLayer(self, layer):
		if len(self.layer_list) == 0:
			self.input_layer.next_layer = layer
			layer.prev_layer = self.input_layer
		else:
			self.layer_list[-1].next_layer = layer
			layer.prev_layer = self.layer_list[-1]
		
		layer.InitWeights()
		layer.next_layer = self.output_layer
		self.output_layer.prev_layer = layer
		self.output_layer.InitWeights()
		self.layer_list.append(layer)
		
	def Forward(self, sample_indices = None):
		if sample_indices is None:
			sample_x = self.x
		else:
			sample_x = self.x[sample_indices, :]
			
		self.p_hat = self.input_layer.Forward(sample_x)

	def Backward(self, learn_rate, sample_indices = None):
		if sample_indices is None:
			sample_y = self.y
		else:
			sample_y = self.y[sample_indices, :]
		self.output_layer.Backward(self.p_hat, sample_y, learn_rate)
		
	def Build(self, layer_list):
		for layer in layer_list:
			self.AddLayer(layer)
			
	def Fit(self, max_epochs, learn_rate, init_weights = True):
		if init_weights:
			self.loss = []
			for layer in self.layer_list:
				layer.InitWeights()
			self.output_layer.InitWeights()
			
		for i in range(max_epochs):
			self.Forward()
			self.Backward(learn_rate)
			p_hat = self.Predict(self.x)
			self.loss.append(self.loss_func(self.y, p_hat))
			self.Echo('Iteration:', i, '\tLoss:', self.loss[-1])
	
	def BatchFit(self, max_epochs, learn_rate, init_weights = True, batch_size = 10):
		if init_weights:
			self.loss = []
			for layer in self.layer_list:
				layer.InitWeights()
			self.output_layer.InitWeights()
			
		for i in range(max_epochs):
			sample_indices = (np.random.rand(batch_size) * self.x.shape[0]).astype(int)
			self.Forward(sample_indices = sample_indices)
			self.Backward(learn_rate, sample_indices = sample_indices)
			p_hat = self.Predict(self.x)
			self.loss.append(self.loss_func(self.y, p_hat))
			self.Echo('Iteration:', i, '\tLoss:', self.loss[-1])
	
	def Predict(self, x):
		p_hat = self.input_layer.Predict(x)
		return p_hat
			
	def PlotLoss(self):
		plot.plot(self.loss, label = 'Model Loss')
			
		plot.title('Loss Curve')
		plot.xlabel('Iterations')
		plot.ylabel('Loss')
		plot.legend()
		plot.show()
		
