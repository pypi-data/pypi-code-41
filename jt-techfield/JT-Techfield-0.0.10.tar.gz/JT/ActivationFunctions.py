"""
Jacob Thompson

Activation Functions
"""
import numpy as np

class Activation:
	def __init__(self):
		self.hyperparameters = {}
		self.Eval = self.Evaluate
		self.__call__ = self.Evaluate

		self.D = self.Derivative
		
	def __init_subclass__(cls):
		cls.Eval = cls.Evaluate
		cls.__call__ = cls.Evaluate
		
		cls.D = cls.Derivative
		
	def SetHyperParameters(self, param_dict):
		next_dict = dict()
		for key, value in param_dict.items():
			if key in self.hyperparameters:
				setattr(self, key, value)
			else:
				next_dict[key] = value
				
	def GetHyperParameters(self):
		out = {}
		for param in self.hyperparameters:
			out[param] = getattr(self, param)
		return out
		
	def Evaluate(self, z):
		return z

	def Derivative(self, z):
		return 1
				
	
class Sigmoid(Activation):
	def Evaluate(self, z):
		"""
		Evaluates the sigmoid of z:
			1 / (1 + e^(-z))
		"""
		p_hat = 1 / (1 + np.exp(-z))
		p_hat += (p_hat < 0.0001) * 0.0001
		p_hat -= (p_hat > 0.9999) * 0.0001
		return p_hat
		
	def Derivative(self, z):
		"""
		Evaluates the derivative of sigmoid of z:
			Sigmoid(z) * (1 - Sigmoid(z))
		"""
		sig = self.Evaluate(z)
		return sig * (1 - sig)

class Softmax(Activation):
	def Evaluate(self, h):
		e_h = np.exp(h)
		p_hat = e_h / np.sum(e_h, axis = 1, keepdims = True)
		p_hat += (p_hat < 0.0001) * 0.0001
		p_hat -= (p_hat > 0.9999) * 0.0001
		return p_hat
		
	def Derivative(self, h):
		"""
		=== WIP ===
		"""
		pass
		
		
class Tanh(Activation):
	def Evaluate(self, h):
		return (np.exp(h) - np.exp(-h)) / (np.exp(h) + np.exp(-h))
		
	def Derivative(self, h):
		return 1 - (self.Evaluate(h) ** 2)
		
		
class ReLU(Activation):
	def Evaluate(self, h):
		return h * (h > 0)
		
	def Derivative(self, h):
		return h > 0
		
		
class LeakyReLU(Activation):
	def __init__(self, leak_coefficient):
		self.leak_coefficient = leak_coefficient
		self.hyperparameters = {'leak_coefficient'}
		
	def Evaluate(self, h):
		return (h * (h > 0)) + (self.leak_coefficient * h * (h < 0))
		
	def Derivative(self, h):
		return (h > 0) + (self.leak_coefficient * (h < 0))
		
class Softplus(Activation):
	def Evaluate(self, h):
		return np.log(1 + np.exp(h))
		
	def Derivative(self, h):
		return 1 / (1 + np.exp(-h))