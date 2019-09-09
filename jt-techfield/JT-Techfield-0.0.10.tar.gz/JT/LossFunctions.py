"""
Jacob Thompson

LossFunctions.py
"""
import numpy as np
import JT.ActivationFunctions

class Loss:
	"""
	Parent class that holds aliases
	"""
	def __init__(self):
		self.hyperparameters = {}
	
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
		self.activation.SetHyperParameters(next_dict)
		
	def GetHyperParameters(self):
		out = {}
		for param in self.hyperparameters:
			out[param] = getattr(self, param)
		out.update(self.activation.GetHyperParameters())
		return out
			
class SumOfSquaredResidual(Loss):
	"""
	Class that contains the formula for calculating the L1 and L2 Penalized Sum of Squared Residual (aka Sum of Squared Error) (aaka ElasticNet)
	"""
	def __init__(self, reg_rate = 0, l1_ratio = 0):
		"""
		Initializes the object and stores the parameter for:
			lambda_1 - the penalty modifier for L1 penalization
			lambda_2 - the penalty modifier for L2 penalization
		"""
		self.reg_rate = reg_rate
		self.l1_ratio = l1_ratio
		self.lamb_1 = reg_rate * l1_ratio
		self.lamb_2 = reg_rate * (1-l1_ratio)
		self.hyperparameters = {'reg_rate', 'l1_ratio'}
		self.name = 'L1 and L2 Penalized Sum of Squared Residuals'
		self.activation = JT.ActivationFunctions.Activation
		
	def Evaluate(self, y, y_hat, w_hat = None):
		"""
		Evaluates the loss function given all the arguments
		"""
		
		if not w_hat is None:
			penalty = (
						self.lamb_1 * np.sum(abs(w_hat)) + 								# This is the formula for the L1 penalty
						self.lamb_2 * (w_hat.T @ w_hat).trace()							# This is the formula for the L2 penalty
						)
		else:
			penalty = 0
			
		return (
			((y - y_hat).T @ (y - y_hat)).trace() + 	# This is the formula for the typical Sum of Squared Residual
			penalty)
			
	def Derivative(self, w_hat, x, y, y_hat):
		"""
		Evaluates the derivative of the loss function given all the arguments
		"""
		return (
			x.T @ (y_hat - y) + 				# This is the formula for the typical Sum of Squared Residual derivative
			self.lamb_1 * np.sign(w_hat) + 		# This is the formula for the L1 penalty derivative
			self.lamb_2 * w_hat					# This is the formula for the L2 penalty derivative
			)
			
class SumOfSquaredError(SumOfSquaredResidual):
	"""
	Alias for L1L2SumOfSquaredResidual
	"""
	pass
			
class ElasticNet(SumOfSquaredResidual):
	"""
	Alias for L1L2SumOfSquaredResidual
	"""
	pass
	
class Binary_Cross_Entropy(Loss):
	def __init__(self, reg_rate = 0, l1_ratio = 0):
		self.name = 'Binary Cross Entropy'
		self.reg_rate = reg_rate
		self.l1_ratio = l1_ratio
		self.lamb_1 = reg_rate * l1_ratio
		self.lamb_2 = reg_rate * (1-l1_ratio)
		self.activation = JT.ActivationFunctions.Sigmoid()
		self.hyperparameters = {'reg_rate', 'l1_ratio'}
	
	def Evaluate(self, y, y_hat, w_hat = None):
		p_hat = self.activation(y_hat)
		
		if not (w_hat is None):
			penalty = (
						self.lamb_1 * np.sum(abs(w_hat)) + 								# This is the formula for the L1 penalty
						self.lamb_2 * (w_hat.T @ w_hat).trace()							# This is the formula for the L2 penalty
						)
		else:
			penalty = 0
			
		return (
			-np.sum(y * np.log(p_hat) + (1 - y) * np.log(1 - p_hat)) +
			self.lamb_1 * np.sum(abs(w_hat)) + 								# This is the formula for the L1 penalty
			self.lamb_2 * (w_hat.T @ w_hat).trace()	
			)
		
	def Derivative(self, w_hat, x, y, y_hat):
		p_hat = self.activation(y_hat)
		
		return (
			x.T @ (p_hat - y) + 
			self.lamb_1 * np.sign(w_hat) + 						# This is the formula for the L1 penalty derivative
			self.lamb_2 * w_hat	
			)
			
	# def Core(self, y_hat):
		# p_hat = self.activation(y_hat)
		# p_hat += (p_hat < 0.001) * 0.001
		# p_hat -= (p_hat > 0.999) * 0.001
		# return p_hat - y
	
class Cross_Entropy(Loss):
	def __init__(self, reg_rate = 0, l1_ratio = 0):
		self.name = 'Cross Entropy'
		self.lamb_1 = reg_rate * l1_ratio
		self.lamb_2 = reg_rate * (1-l1_ratio)
		self.activation = JT.ActivationFunctions.Softmax()
		self.hyperparameters = {'reg_rate', 'l1_ratio'}
		
	def Evaluate(self, y, y_hat, w_hat = None):
		p_hat = self.activation(y_hat)
		if not (w_hat is None):
			penalty = (
						self.lamb_1 * np.sum(abs(w_hat)) + 								# This is the formula for the L1 penalty
						self.lamb_2 * (w_hat.T @ w_hat).trace()							# This is the formula for the L2 penalty
						)
		else:
			penalty = 0
		return -np.sum(y * np.log(p_hat)) + penalty
			
			
	def Derivative(self, w_hat, x, y, y_hat):
		p_hat = self.activation(y_hat)
		return (
			x.T @ (p_hat - y) + 
			self.lamb_1 * np.sign(w_hat) + 						# This is the formula for the L1 penalty derivative
			self.lamb_2 * w_hat									# This is the formula for the L2 penalty derivative
			)
			


class Cross_Entropy2(Loss):
	def __init__(self, reg_rate = 0, l1_ratio = 0):
		self.name = 'Cross Entropy'
		self.lamb_1 = reg_rate * l1_ratio
		self.lamb_2 = reg_rate * (1-l1_ratio)
		self.activation = JT.ActivationFunctions.Softmax()
		self.hyperparameters = {'reg_rate', 'l1_ratio'}
		
	def Evaluate(self, y, p_hat, w_hat = None):
		if not (w_hat is None):
			penalty = (
						self.lamb_1 * np.sum(abs(w_hat)) + 								# This is the formula for the L1 penalty
						self.lamb_2 * (w_hat.T @ w_hat).trace()							# This is the formula for the L2 penalty
						)
		else:
			penalty = 0
		return -np.sum(y * np.log(p_hat)) + penalty
			
			
	def Derivative(self, w_hat, x, y, p_hat):
		return (
			x.T @ (p_hat - y) + 
			self.lamb_1 * np.sign(w_hat) + 						# This is the formula for the L1 penalty derivative
			self.lamb_2 * w_hat									# This is the formula for the L2 penalty derivative
			)
