"""
Jacob Thompson

MakeSet.py
"""

import numpy as np

def Line(m, b, num = 50, noise_deviation = 1, span = (-10, 10)):
	"""
	Makes a set of x's and y's in the shape of a parabola following the equation:
		y = m * x + b
	
	Adds noise and returns both x and y
	
	Note: The returned values are sorted in ascending order by the x's
	"""
	x = np.random.rand(num, 1) * (span[1] - span[0]) + span[0]
	x[:, 0].sort()
	noise = np.random.randn(num, 1) * noise_deviation
	y = x @ [[m]] + b + noise
	return x, y
	
def Parabola(a, b, c, num = 50, noise_deviation = 1, span = (-10, 10)):
	"""
	Makes a set of x's and y's shaped in a parabola of the form:
		y = ax^2 + bx + c

	Adds noise and returns both x and y
	"""
	x = np.random.rand(num, 1) * (span[1] - span[0]) + span[0]	# Generates random smattering of x's
	x[:, 0].sort()												# Sort the x's
	noise = np.random.randn(num, 1) * noise_deviation			# Generate a column of random noise
	X = np.hstack((np.ones((num, 1)), x, x ** 2))				# Generate the X array by combining ones, x, and x^2
	w = [[c], [b], [a]]											# Builds the weight vector from a, b, and c
	y = X @ w + noise											# Calculates y
	
	return x, y
	
def MultiLine(weights, num = 50, noise_deviation = 1, span = (-10, 10)):
	if type(weights) != np.array:
		weights = np.array(weights)
	
	dims = weights.shape[0] - 1
	# print(dims)
	x = np.random.rand(num, dims) * (span[1] - span[0]) + span[0]
	bias = np.ones([num, 1])
	x = np.hstack((bias, x))
	noise = np.random.randn(num, 1) * noise_deviation
	# print('x:', x.shape)
	# print('w:', weights.shape)
	y = x @ weights + noise	
	# print('y:', y.shape)
	return x, y


def TriCluster(num = 6000, scale = 1, skew = False):
	if skew:
		cov1 = np.random.randn(2, 2)
		cov2 = np.random.randn(2, 2)
		cov3 = np.random.randn(2, 2)
	else:
		cov1 = np.eye(2)
		cov2 = np.eye(2)
		cov3 = np.eye(2)

	x1 = np.random.randn(num // 3, 2) * scale @ cov1 + np.array([[0, -6]])
	x2 = np.random.randn(num // 3, 2) * scale @ cov2 + np.array([[8, 0]])
	x3 = np.random.randn(num // 3, 2) * scale @ cov3 + np.array([[0, 6]])

	cat_1 = np.hstack([
		x1,
		np.ones([x1.shape[0], 1]),
		np.zeros([x1.shape[0], 1]),
		np.zeros([x1.shape[0], 1]),
	])
	cat_2 = np.hstack([
		x2,
		np.zeros([x1.shape[0], 1]),
		np.ones([x1.shape[0], 1]),
		np.zeros([x1.shape[0], 1]),
	])
	cat_3 = np.hstack([
		x3,
		np.zeros([x1.shape[0], 1]),
		np.zeros([x1.shape[0], 1]),
		np.ones([x1.shape[0], 1]),
	])

	data = np.vstack([cat_1, cat_2, cat_3])

	np.random.shuffle(data)

	x = data[:, [0, 1]]
	y = data[:, 2:]

	return x, y

def SpanSpace(x, num = 100):
	"""
	:param x: Input data arranged in columns.
	:param num: number of points along each axis to create.
	:return: Simulated input data that spans the input data on each features.

	Works like an n-dimensional np.linspace() except the upper/lower bounds are
	determined by the max/min of the data along each of it's features.
	"""
	step = 1 / num
	n = x.shape[1]
	grid = np.mgrid[[slice(0, 1, step)] * n]
	return np.reshape(grid, (n, -1)).T * (x.max(axis = 0) - x.min(axis = 0)) + x.min(axis = 0)