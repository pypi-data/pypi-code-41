import math

#===================================================Useful functions=====================================================

#Pleas see Doc/Protein/pdb.md for the usage of this function
def longtail(extremum, extreme_point, yield_point):
	a=(extreme_point/(yield_point-extreme_point))*(extreme_point/(yield_point-extreme_point))
	b=a/extreme_point
	c=extremum*((b*math.e/a)**a)
	def outfunc(ainput):
		return c*(ainput**a)*math.e**(-ainput*b)
	return outfunc


#Pleas see Doc/Protein/pdb.md for the usage of this function
def quadratic(intercept_left,extremum,intercept_right):
	a=4*extremum/(intercept_right-intercept_left)/(intercept_left-intercept_right)
	b=-a*(intercept_right+intercept_left)
	c=a*intercept_left*intercept_right
	def outfunc(ainput):
		return a*ainput*ainput+b*ainput+c
	return outfunc

def hill(aMax, amin, startpoint, **kargs):
	H=aMax-amin
	reverse=kargs.get('reverse',(False))
	hill_coefficient=kargs.get('hill_coefficient',None)
	halflife=kargs.get('halflife',None)
	if halflife==None:
		if hill_coefficient==None:
			try:
				a=kargs['point1'][0]
				A=kargs['point1'][1]
				b=kargs['point2'][0]
				B=kargs['point2'][1]
			except:
				raise ValueError("You must give two points(argument 'point1' and 'point2' in tuple) on the curve if you don't give a halflife and a hill coefficient")
			a=a-startpoint
			b=b-startpoint
			A=(A-amin)/H
			B=(B-amin)/H
			if reverse==False:
				hill_coefficient=math.log(((1-B)*A)/((1-A)*B),a/b)
				halflife=(((1-A)/A)**(1/hill_coefficient))*a-startpoint
				def outfunc(ainput):
					return amin+H*((ainput-startpoint)**hill_coefficient)/(((ainput-startpoint)**hill_coefficient)+(halflife**hill_coefficient))
				return outfunc
			else:
				A=1-((A-amin)/H)
				B=1-((B-amin)/H)
				hill_coefficient=math.log(((1-B)*A)/((1-A)*B),a/b)
				halflife=(((1-A)/A)**(1/hill_coefficient))*a-startpoint
				def outfunc(ainput):
					return amin+H*(halflife**hill_coefficient)/(((ainput-startpoint)**hill_coefficient)+(halflife**hill_coefficient))
				return outfunc
		else:
			try:
				a=kargs['point1'][0]
				A=kargs['point1'][1]
			except:
				raise ValueError("You must give one points(argument 'point1' in tuple) on the curve if you don't give a halflife")
			a=a-startpoint
			A=(A-amin)/H
			if reverse==False:
				halflife=(((1-A)/A)**(1/hill_coefficient))*a-startpoint
				def outfunc(ainput):
					return amin+H*((ainput-startpoint)**hill_coefficient)/(((ainput-startpoint)**hill_coefficient)+(halflife**hill_coefficient))
				return outfunc
			else:
				A=1-((A-amin)/H)
				B=1-((B-amin)/H)
				halflife=(((1-A)/A)**(1/hill_coefficient))*a-startpoint
				def outfunc(ainput):
					return amin+H*(halflife**hill_coefficient)/(((ainput-startpoint)**hill_coefficient)+(halflife**hill_coefficient))
				return outfunc
	else:
		halflife-=startpoint
		if hill_coefficient==None:
			try:
				a=kargs['point1'][0]
				A=kargs['point1'][1]
			except:
				raise ValueError("You must give two points(argument 'point1' and 'point2' in tuple) on the curve if you don't give a halflife and a hill coefficient")
			a=a-startpoint
			A=(A-amin)/H
			if reverse==False:
				hill_coefficient=math.log(((1-A)/A),halflife/a)
				def outfunc(ainput):
					return amin+H*((ainput-startpoint)**hill_coefficient)/(((ainput-startpoint)**hill_coefficient)+(halflife**hill_coefficient))
				return outfunc
			else:
				A=1-((A-amin)/H)
				hill_coefficient=math.log(((1-A)/A),halflife/a)
				def outfunc(ainput):
					return amin+H*(halflife**hill_coefficient)/(((ainput-startpoint)**hill_coefficient)+(halflife**hill_coefficient))
				return outfunc
		else:
			if reverse==False:
				def outfunc(ainput):
					return amin+H*((ainput-startpoint)**hill_coefficient)/(((ainput-startpoint)**hill_coefficient)+(halflife**hill_coefficient))
				return outfunc
			else:
				def outfunc(ainput):
					return amin+H*(halflife**hill_coefficient)/(((ainput-startpoint)**hill_coefficient)+(halflife**hill_coefficient))
				return outfunc






#================================================Build a New Function====================================================

def dec_quadratic(extremum, intercept):
	a=-extremum/intercept/intercept
	def outfunc(ainput):
		return a*ainput*ainput+extremum
	return outfunc

def dec_exponential(extremum, halflife):
	t=math.log(2)/halflife
	def outfunc(ainput):
		return extremum*(math.e**(-t*ainput))
	return outfunc

def dec_hill(extremum, halflife, hill_coefficient):
	def outfunc(ainput):
		return extremum*(halflife**hill_coefficient)/((ainput**hill_coefficient)+(halflife**hill_coefficient))
	return outfunc

def dec_linear(extremum, intercept):
	k=extremum/intercept
	def outfunc(ainput):
		return extremum-k*ainput
	return outfunc


def link_linear(left,right):
	k=right-left
	def outfuncl(length):
		def outfunc(ainput):
			return left+k/length*ainput
		return outfunc
	return outfuncl



def link_cos(left,right):
	c=(left+right)/2
	a=(left-right)/2
	def outfuncl(length):
		def outfunc(ainput):
			return c+a*math.cos(math.pi/length*ainput)
		return outfunc
	return outfuncl


def link_pow(left,right,pow):
	a=right-left
	def outfuncl(length):
		def outfunc(ainput):
			return left+a*((ainput/length)**pow)
		return outfunc
	return outfuncl


def move(inputfunc, distance, reflect=1):
	def outfunc(ainput):
		return inputfunc(reflect*(ainput-distance))
	return outfunc

#option: 
#	0b1    no scaling
#	0b10   don't move
#pass a tuple like that ((function1,stop1,reflect1),(constant,stop2),(function2,stop3,reflect3,option(this is optional)),(function3,start,reflect4)
def combinefunc(functionlist):
	length=len(functionlist)-1
	def outfunc(ainput):
		if ainput<functionlist[0][1]:
			if hasattr(functionlist[0][0],'__call__'):
				try:
					option=functionlist[0][3]
					if (option >> 1) & 1==1:
						return functionlist[0][0](ainput)
					else:
						return move(functionlist[0][0],functionlist[0][1],functionlist[0][2])(ainput)
				except:
					return move(functionlist[0][0],functionlist[0][1],functionlist[0][2])(ainput)
			else:
				return functionlist[0][0]
		elif ainput>=functionlist[length][1]:
			if hasattr(functionlist[length][0],'__call__'):
				try:
					option=functionlist[length][3]
					if (option >> 1) & 1==1:
						return functionlist[length][0](ainput)
					else:
						return move(functionlist[length][0],functionlist[length][1],functionlist[length][2])(ainput)
				except:
					return move(functionlist[length][0],functionlist[length][1],functionlist[length][2])(ainput)
			else:
				return functionlist[length][0]
		else:
			for i in range(1,length):
				if ainput<functionlist[i][1]:
					if hasattr(functionlist[i][0],'__call__'):
						try:
							option=functionlist[i][3]
							if (option >> 1) & 1==1:
								if option & 1==1:
									return functionlist[i][0](ainput)
								else:
									temlen=functionlist[i][1]-functionlist[i-1][1]
									return functionlist[i][0](temlen)(ainput)
							else:
								if option & 1==1:
									return move(functionlist[i][0],functionlist[i-1][1],functionlist[i][2])(ainput)
								else:
									temlen=functionlist[i][1]-functionlist[i-1][1]
									return move(functionlist[i][0](temlen),functionlist[i-1][1],functionlist[i][2])(ainput)
						except:
							temlen=functionlist[i][1]-functionlist[i-1][1]
							return move(functionlist[i][0](temlen),functionlist[i-1][1],functionlist[i][2])(ainput)
					else:
						return functionlist[i][0]
	return outfunc