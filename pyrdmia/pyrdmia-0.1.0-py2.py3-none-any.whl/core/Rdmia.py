# PyPython Library 2018
# RDM-IA implementation by
# Dirceu Maraschin Jr
# Lucas Tortelli

'''
This file is responsible for creating RDM numbers and setting the 
precision of operation in calculations using Py
'''
from __future__ import print_function
from .Rdm import *
from ..utils import QualitativeMetrics as qm
import itertools, copy

_precision = 0.5

def precision():
	return _precision

def setDotPrecision(val):
	_precision = val #10**(-val)
	print ("defined precision: %s" % _precision)

def one():
	return Rdm(1.0,None,_precision)

def zero():
	return Rdm(0.0,None,_precision)

def number(x,y=None):
	if y is None:
		return Rdm(x,None,_precision)
	else:
		if x>y:
			raise TypeIntervalError("Improper interval defined!")
		else:
			return Rdm(x,y,_precision)


def isiterable(data):
	try:
		chkit = iter(data)
	except TypeError:
		return False
	return True

def arrayAlpha(data,alpha):
	arr = SimpleArray()
	arr.shape = []

	dataAux = []
	if not isiterable(data):
		raise ValueError("Input must be iterable")
	for i in range(len(data)):
		aux = []
		for k in range(len(data[0])):
			aux.append(data[i][k].getNumber(alpha))
		dataAux.append(aux)	
	arr._ValidateShape(dataAux, 0)
	arr.data = dataAux
	arr.shape = tuple(arr.shape)
	return arr

def array(data):
	arr = SimpleArray()
	arr.shape = []
	if not isiterable(data):
		raise ValueError("Input must be iterable")
	arr._ValidateShape(data, 0)
	arr.data = data
	arr.shape = tuple(arr.shape)
	return arr

def arrayMinMax(data):
	arrLow = SimpleArray()
	arrLow.shape = []
	arrUp = SimpleArray()
	arrUp.shape = []

	lowers = []
	uppers = []
	if not isiterable(data):
		raise ValueError("Input must be iterable")
	for i in range(len(data)):
		auxLow = []
		auxUp = []
		for k in range(len(data[0])):
			auxLow.append(data[i][k].lower())
			auxUp.append(data[i][k].upper())
		lowers.append(auxLow)
		uppers.append(auxUp)	
	arrLow._ValidateShape(lowers, 0)
	arrLow.data = lowers
	arrLow.shape = tuple(arrLow.shape)

	arrUp._ValidateShape(uppers, 0)
	arrUp.data = uppers
	arrUp.shape = tuple(arrUp.shape)
	return arrLow,arrUp

def zeros(shape):
	arr = SimpleArray()
	arr.shape = tuple(shape)
	if not isiterable(shape):
		raise ValueError("Shape must be iterable")
	arr.data = []
	def GenData(shape, leafs):
		dim = shape.pop(0)
		newLeafs = []
		if len(shape) == 0:
			for l in leafs:
				for i in range(dim):
					l.append(0.0)
		else:
			for l in leafs:
				for i in range(dim):
					nl = []
					l.append(nl)
					newLeafs.append(nl)
			GenData(shape, newLeafs)
			
	GenData(list(arr.shape)[:], [arr.data])
	return arr


def identity(dim):
	mat = zeros((dim, dim))
	for i in range(dim):
		mat.data[i][i] = 1.0
	return mat

class SimpleArray(object):
	def __init__(self):
		self.shape = []
		self.data = None

	def _ValidateShape(self, data, ind):
		if not isiterable(data):
			return
		if ind >= len(self.shape):
			self.shape.append(len(data))
		else:
			if self.shape[ind] != len(data):
				raise ValueError("Inconsistent shape")
		for val in data:
			self._ValidateShape(val, ind+1)

	def __repr__(self):
		return (self.__class__.__name__+"("+self.data+")")

	@property
	def midPointMatrix(self):

		for i in range(len(self.data)):
			for k in range(len(self.data[0])):
				if(type(self.data[i][k]) is Rdm):
					self.data[i][k] = qm.midpoint(self.data[i][k])
		return self

	def __str__(self):
		#print (self.data)
		matrix = ''
		for row in self.data:
			matrix += str(row)+"\n"
		return matrix

	def dot(self, rhs):
		#This also standard matrix multiplication
		if not isinstance(rhs, self.__class__) and isiterable(rhs):		
			rhs = array(rhs)
		if len(self.shape) != 2 or len(rhs.shape) != 2:
			raise NotImplementedError("Only implemented for 2D matricies")
		if self.shape[1] != rhs.shape[0]:
			raise ValueError("Matrix size mismatch")
		m = self.shape[1]
		result = zeros((self.shape[0], rhs.shape[1]))
		for i in range(result.shape[0]):
			for j in range(result.shape[1]):
				tot = 0.0
				for k in range(m):
					aik = self.data[i][k]
					bkj = rhs.data[k][j]
					tot += aik * bkj
				result.data[i][j] = tot
		return result

	def __add__(self, rhs):
		if not isinstance(rhs, self.__class__) and isiterable(rhs):		
			rhs = array(rhs)
		if self.shape != rhs.shape:
			raise ValueError("Matrix size mismatch")
		result = zeros(self.shape)
		def AddFunc(ind, a, b, out):
			if ind == len(self.shape):
				raise ValueError("Invalid matrix")
			if ind == len(self.shape) - 1:
				for i, (av, bv) in enumerate(zip(a, b)):
					out[i] = av + bv
			else:
				ind += 1
				for ar, br, outr in zip(a, b, out):
					AddFunc(ind, ar, br, outr)		
		AddFunc(0, self.data, rhs.data, result.data)
		return result

	def __mul__(self, rhs):
		if not isinstance(rhs, self.__class__) and isiterable(rhs):		
			rhs = array(rhs)

		if isinstance(rhs, self.__class__):
			#Do element-wise matrix multiplication
			if self.shape != rhs.shape:
				raise ValueError("Matrix size mismatch")
			result = zeros(self.shape)
			def MultFunc(ind, a, b, out):
				if ind == len(self.shape):
					raise ValueError("Invalid matrix")
				if ind == len(self.shape) - 1:
					for i, (av, bv) in enumerate(zip(a, b)):
						out[i] = av * bv
				else:
					ind += 1
					for ar, br, outr in zip(a, b, out):
						MultFunc(ind, ar, br, outr)		
			MultFunc(0, self.data, rhs.data, result.data)
			return result
		else:
			#Do scalar multiplication to entire matrix (element-wise)
			result = zeros(self.shape)
			def MultFunc2(ind, a, b, out):
				if ind == len(self.shape):
					raise ValueError("Invalid matrix")
				if ind == len(self.shape) - 1:
					for i, av in enumerate(a):
						out[i] = av * b
				else:
					ind += 1
					for ar, outr in zip(a, out):
						MultFunc2(ind, ar, b, outr)		
			MultFunc2(0, self.data, rhs, result.data)
			return result

	def __sub__(self, rhs):
		if not isinstance(rhs, self.__class__) and isiterable(rhs):		
			rhs = array(rhs)
		if self.shape != rhs.shape:
			raise ValueError("Matrix size mismatch")
		negRhs = rhs * -1
		return self + negRhs

	def conj(self):
		result = zeros(self.shape)
		def AddFunc(ind, a, out):
			if ind == len(self.shape):
				raise ValueError("Invalid matrix")
			if ind == len(self.shape) - 1:
				for i, av in enumerate(a):
					if isinstance(av, complex):
						out[i] = av.conjugate()
					else:
						out[i] = av
			else:
				ind += 1
				for ar, outr in zip(a, out):
					AddFunc(ind, ar, outr)		
		AddFunc(0, self.data, result.data)
		return result

	@property
	def T(self):
		if len(self.shape) <= 1:
			return self
		if len(self.shape) != 2:
			raise NotImplementedError("Only implemented for 1D and 2D matricies")	
		result = zeros((self.shape[1], self.shape[0]))
		for i in range(self.shape[0]):
			for j in range(self.shape[1]):
				result.data[j][i] = self.data[i][j]
		return result

	def copy(self):
		return array(copy.deepcopy(self.data))

	def _delete(self,mat, ind, axis=0):
		if not isinstance(mat, SimpleArray) and isiterable(mat):		
			mat = array(mat)
		newShape = list(mat.shape)[:]
		newShape[axis] -= len(ind)
		result = zeros(newShape)
		def CopyWithDelete(currentAxis, ind, axis, matdata, resultData):
			if currentAxis < len(mat.shape)-1:
				count = 0
				for i, data in enumerate(matdata):
					if currentAxis == axis and i in ind:
						continue
					CopyWithDelete(currentAxis + 1, ind, axis, data, resultData[count])
					count += 1
			else:
				count = 0
				for i, val in enumerate(matdata):
					if currentAxis == axis and i in ind:
						continue
					resultData[count] = val
					count += 1

		CopyWithDelete(0, ind, axis, mat.data, result.data)
		return result


	def _adjugate(self,mat):
		if not isinstance(mat, SimpleArray) and isiterable(mat):		
			mat = array(mat)
		#Find the adjugate matrix
		if len(mat.shape) != 2:
			raise NotImplementedError("Only implemented for 2D matricies")
		result = zeros(mat.shape)
		for i in range(mat.shape[0]):
			for j in range(mat.shape[1]):
				submat = self._delete(mat, [j], 0)
				submat2 = self._delete(submat, [i], 1)
				result.data[i][j] = ((-1)**(i+j))*self._det(submat2)
		return result

	#Implementar internamente quando uma matriz eh mto grande
	@property
	def I(self):
		eps=1e-8
		#Find inverse based on find the adjugate matrix
		#which is inefficient for large matrices.
		if not isinstance(self, SimpleArray) and isiterable(self):		
			mat = array(self)
		if len(self.shape) != 2:
			raise NotImplementedError("Only implemented for 2D matricies")
		if self.shape[0] != self.shape[1]:
			raise ValueError("Matrix must be square")
		mdet = self.D
		if (type(mdet) is Rdm):
			mdet = qm.midpoint(mdet)
		if abs(mdet) < eps:
			raise RuntimeError("Matrix is not invertible (its determinant is zero)")
		return self._adjugate(self.data) * (1.0 / float(mdet))

	@property
	def D(self):
		return self._det(self)

	def _det(self,arr):
		if not isinstance(arr.data, SimpleArray) and isiterable(arr.data):		
			arr.data = array(arr.data)
		if len(arr.data.shape) != 2:
			raise NotImplementedError("Only implemented for 2D matricies")
		if arr.data.shape[0] != arr.data.shape[1]:
			raise ValueError("Matrix must be square")
		n = arr.data.shape[0]
		
		#Leibniz formula for the determinant
		total2 = 0.0
		for perm in itertools.permutations(range(n)):
			total1 = 1.0
			for i, j in zip(range(n), perm):
				total1 *= arr.data.data[i][j]
			total2 += self._perm_parity(list(perm)) * total1
		return total2
		
	def _perm_parity(self,lst):
		parity = 1
		for i in range(0,len(lst)-1):
			if lst[i] != i:
				parity *= -1
				mn = min(range(i,len(lst)), key=lst.__getitem__)
				lst[i],lst[mn] = lst[mn],lst[i]
		return parity	

	@property
	def inv(self):
	#Find inverse based on gauss-jordan elimination.
		eps=1e-8
		if not isinstance(self.data, SimpleArray) and isiterable(self.data):		
			self.data = array(self.data)
		if len(self.shape) != 2:
			raise NotImplementedError("Only  implemented for 2D matricies")
		if self.shape[0] != self.shape[1]:
			raise ValueError("Matrix must be square")
		mdet = self._det(self)

		if(type(mdet) is Rdm):
			mdet = qm.midpoint(mdet)
		if abs(mdet) < eps:
			raise RuntimeError("Matrix is not invertible (its determinant is zero)")
		#Create aux matrix
		n = self.shape[0]
		auxmat = identity(n)

		#Convert to echelon (triangular) form
		self.data = copy.deepcopy(self.data)
		for i in range(n):
			#Find highest value in this column
			maxv = 0.0
			maxind = None
			for r in range(i, n):
				v = self.data.data[r][i]
				if(type(v) is Rdm):
					v = abs(qm.midpoint(v))
				if maxind is None or abs(v) > maxv:
					if(type(v) is Rdm):
						maxv = abs(qm.midpoint(v))
					else:
						maxv = abs(v)
					maxind = r
			if maxind != i:
				#Swap this to the current row, for numerical stability
				self.data.data[i], self.data.data[maxind] = self.data.data[maxind], self.data.data[i]
				auxmat.data[i], auxmat.data[maxind] = auxmat.data[maxind], auxmat.data[i]
			activeRow = self.data.data[i]
			activeAuxRow = auxmat.data[i]
			for r in range(i+1, n):
				scale = self.data.data[r][i] / self.data.data[i][i]
				cursorRow = self.data.data[r]
				cursorAuxRow = auxmat.data[r]
				for c in range(n):
					cursorRow[c] -= scale * activeRow[c]
					cursorAuxRow[c] -= scale * activeAuxRow[c]
		#Finish elimination
		for i in range(n-1, -1, -1):
			activeRow = self.data.data[i]
			activeAuxRow = auxmat.data[i]
			for r in range(i, -1, -1):
				cursorRow = self.data.data[r]
				cursorAuxRow = auxmat.data[r]
				if r == i:
					scaling = activeRow[i]
					for c in range(n):
						print(cursorRow[c],scaling)
						cursorRow[c] /= scaling
						cursorAuxRow[c] /= scaling
				else:
					scaling = cursorRow[i]
					for c in range(n):
						cursorRow[c] -= activeRow[c] * scaling
						cursorAuxRow[c] -= activeAuxRow[c] * scaling
		return self