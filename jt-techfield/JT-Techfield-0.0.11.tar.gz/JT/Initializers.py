"""
Jacob Thompson

Weight Initialization
"""
import numpy as np


class Initializer:
	def __init__(self):
		self.Init = self.Initialize
		self.__call__ = self.Initialize

	def __init_subclass__(cls):
		cls.Init = cls.Initialize
		cls.__call__ = cls.Initialize
		
	def Initialize(self, size_in, size_out):
		return np.random.randn(size_in, size_out)


class Xavier(Initializer):
	def __init__(self, numerator = 1):
		"""
		numerator:	The value to use as the numerator for adjusting the weights
						Use 1 if using a ReLU activation
						Use 2 if using a tanh activation
		"""
		self.numerator = numerator
		
	def Initialize(self, size_in, size_out):
		return np.random.randn(size_in, size_out) * np.sqrt(self.numerator / size_in)


class He(Initializer):
	def Initialize(self, size_in, size_out):
		return np.random.randn(size_in, size_out) * np.sqrt(1 / (size_in + size_out))
