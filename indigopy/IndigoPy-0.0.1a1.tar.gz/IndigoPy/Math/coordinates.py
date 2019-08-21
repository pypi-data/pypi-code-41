#!/usr/bin/python3
# -*- coding: UTF-8-*-

import math
import numpy as np
import numpy.linalg


def make_basis_matrix(basis):
	return np.mat([[basis[0][0],basis[1][0],basis[2][0]],[basis[0][1],basis[1][1],basis[2][1]],[basis[0][2],basis[1][2],basis[2][2]]])


#Position can be a point or a vector
class Position():
	def __init__(self,pos):
		self.pos=np.mat([[pos[0]],[pos[1]],[pos[2]]])
	def __getitem__(self, key):
		return self.pos[key,0]
	def __setitem__(self, key, value):
		self.pos[key]=value
	def __iter__(self):
		return iter([self[0],self[1],self[2]])

	def __sub__(self, other):
		if isinstance(other,np.matrix):
			temm=self.pos-other
			return Position((temm[0,0],temm[1,0],temm[2,0]))
		try:
			tem=other[0]
			return Position((self[0]-other[0],self[1]-other[1],self[2]-other[2]))
		except:
			return NotImplemented
	def __rsub__(self, other):
		if isinstance(other,np.matrix):
			temm=other-self.pos
			return Position((temm[0,0],temm[1,0],temm[2,0]))
		return Position((other[0]-self[0],other[1]-self[1],other[2]-self[2]))


	def __add__(self, other):
		if isinstance(other,np.matrix):
			temm=self.pos+other
			return Position((temm[0,0],temm[1,0],temm[2,0]))
		try:
			tem=other[0]
			return Position((self[0]+other[0],self[1]+other[1],self[2]+other[2]))
		except:
			return NotImplemented
	def __radd__(self, other):
		if isinstance(other,np.matrix):
			temm=other+self.pos
			return Position((temm[0,0],temm[1,0],temm[2,0]))
		return Position((other[0]+self[0],other[1]+self[1],other[2]+self[2]))

	# value*Position,Position*value and Position/value is a multiplying or dividing. Position_A*Position_A is the dot product of the two vector
	def __mul__(self, other):
		if isinstance(other,np.matrix):
			return self.pos*other
		try: 
			tem=other[0]
			return self[0]*other[0]+self[1]*other[1]+self[2]*other[2]
		except:
			return Position((self[0]*other,self[1]*other,self[2]*other))
	def __rmul__(self, other):
		if isinstance(other,np.matrix):
			temm=other*self.pos
			return Position((temm[0,0],temm[1,0],temm[2,0]))
		try: 
			tem=other[0]
			return other[0]*self[0]+other[1]*self[1]+other[2]*self[2]
		except:
			return Position((other*self[0],other*self[1],other*self[2]))
	def __truediv__(self, other):
		return Position((self[0]/other,self[1]/other,self[2]/other))

	#position**2 is the square of the vector, but position_A**position_B is the cross product of the two vector
	def __pow__(self, other):
		if other==2:
			return self[0]*self[0]+self[1]*self[1]+self[2]*self[2]
		else:
			return Position((self[1]*other[2]-self[2]*other[1],self[2]*other[0]-self[0]*other[2],self[0]*other[1]-self[1]*other[0]))
	def __rpow__(self, other):
		return Position((other[1]*self[2]-other[2]*self[1],other[2]*self[0]-other[0]*self[2],other[0]*self[1]-other[1]*self[0]))

	def __abs__(self):
		return math.sqrt(self[0]*self[0]+self[1]*self[1]+self[2]*self[2])
	def __pos__(self):
		return Position((self[0],self[1],self[2]))
	def __neg__(self):
		return Position((-self[0],-self[1],-self[2]))

	def unit(self):
		return self/abs(self)
	def __str__(self):
		return str((self[0],self[1],self[2]))

# basis is a list of Positions or coordinates, or you can give a matrix or a inversed matrix.
	def linear_trans(self,basis,inverse=False):
		if isinstance(basis,np.matrix)==False:
			tem=np.mat([[basis[0][0],basis[1][0],basis[2][0]],[basis[0][1],basis[1][1],basis[2][1]],[basis[0][2],basis[1][2],basis[2][2]]])
		else:
			tem=basis
		if inverse==False:
			tem=np.linalg.inv(tem)
		return tem*self


class Plane():
	def __init__(self, plane, warn=0):
		try:
			self.normal=(plane[2]-plane[1])**(plane[2]-plane[3]).unit()
			self.points=list(plane)
			self.equation=[self.normal[0],self.normal[1],self.normal[2],0-(self.normal[0]*self.points[0][0])-(self.normal[1]*self.points[0][1])-(self.normal[2]*self.points[0][2])]
			self.warn=warn
			if self.warn==1:
				print('3 points are given')
		except:
			self.normal=(plane[0]).unit()
			self.points=[plane[1]]
			self.equation=[self.normal[0],self.normal[1],self.normal[2],0-(self.normal[0]*self.points[0][0])-(self.normal[1]*self.points[0][1])-(self.normal[2]*self.points[0][2])]
			self.warn=warn
			if self.warn==1:
				print('a normal vector and a point are given')

	# Plane-Position is the distance between the point and the plane. 
	def __sub__(self, other):
		try:
			tem=other[0]
			return abs((self.points[0]-other)*self.normal)
		except:
			if self.equation[0]==other.equation[0] and self.equation[1]==other.equation[1] and self.equation[2]==other.equation[2]:
				return self.equation[3]-other.equation[3]
			else:
				raise ArithmeticError('two intersecting plane don not hava a distance')

	def __rsub__(self, other):
		try:
			tem=other[0]
			return abs((self.points[0]-other)*self.normal)
		except:
			if self.equation[0]==other.equation[0] and self.equation[1]==other.equation[1] and self.equation[2]==other.equation[2]:
				return other.equation[3]-self.equation[3]
			else:
				raise ArithmeticError('two intersecting plane don not hava a distance')


	# Plane+Position is the projection of the point onto the plane. 
	def __add__(self, other):
		ln=(self.points[0]-other)*self.normal
		return Position((ln*self.normal[0]+other[0],ln*self.normal[1]+other[1],ln*self.normal[2]+other[2]))
	def __radd__(self, other):
		ln=(self.points[0]-other)*self.normal
		return Position((ln*self.normal[0]+other[0],ln*self.normal[1]+other[1],ln*self.normal[2]+other[2]))

	# [Warning][] This function has a Low Precision, rewrite it with a higher one or just pass a argument 'warn=0' to ignore this warning.
