from pyrdmia import Rdmia
from pyrdmia import Rdm
from pyrdmia.utils import QualitativeMetrics as qm
import numpy as np
import math

class RLS(object):
	
	def __init__(self):
		__model = 0.0
		__coefDetermination = 0.0
		__rmse = 0.0
		self._predictors = []
		self._predictorsLow = []
		self._predictorsUp = []
		self._isMult = False


	def __str__(self):
		status = ''
		status = "R^2 :" + str(self._coefDetermination) + "\n"
		status += "RMSE :" + str(self._rmse) + "\n"
		return status
	
	def _optimizations(self,x,pred_low,pred_up,y_min,y_max):

		opt_min = 0.0
		opt_max = 0.0

		for val in range(len(x)):
			resultLow = sum([pred_low.data[i]*x[val][i].lower() for i in range(len(pred_low.data))])
			resultUp = sum([pred_up.data[i]*x[val][i].upper() for i in range(len(pred_up.data))])
			opt_min+= abs(resultLow - y_min.data[val])
			opt_max+= abs(resultUp - y_max.data[val])
		
		return opt_min[0],opt_max[0]

	def predict(self,x):
		r_list = []
		if(self._isMult):
			for val in range(len(x)):
				resultLow = sum([self._predictorsLow.data[i]*x[val][i].lower() for i in range(len(self._predictorsLow.data))])
				resultUp = sum([self._predictorsUp.data[i]*x[val][i].upper() for i in range(len(self._predictorsUp.data))])
				r_list.append(Rdmia.number(resultLow,resultUp))
		else:
			for val in range(len(x)):
				result = sum([self._predictors.data[i]*x[val][i] for i in range(len(self._predictors.data))])
				r_list.append(result)
				#r = qm.midpoint(self._predictors.data[0] + self._predictors.data[1]*x.data[val][1])
		
		return r_list


	def fit(self,x_data,y_data,kernel='std',alpha=0.1):
		#x_1 = (inv_by_adjugate(midPointMatrix(x.T.dot(x))))
		#self._preProcessingData(x,y)

		#First part of method minimum square
		if(kernel == 'std'):
			x = Rdmia.array(x_data)
			y = Rdmia.array(y_data)

			x_1 = x.T.dot(x).midPointMatrix

			x_1 = x_1.I
			
			#y_2 = midPointMatrix(x.T.dot(y))
			y_2 = x.T.dot(y).midPointMatrix


			#Calculated predictors beta
			z = (x_1).dot(y_2)

			self._predictors = Rdmia.array([z.data[i][0] for i in range(len(z.data))])
		elif(kernel == 'multidimensional'):
			self._isMult = True

			opt_minium = 0.0
			opt_maximum = 0.0
			for i in np.arange(0.0, 1.0, alpha):
				x = Rdmia.arrayAlpha(x_data,i)
				y_min,y_max = Rdmia.arrayMinMax(y_data)

				x_1 = x.T.dot(x)
				
				x_1 = x_1.I


				#y_2 = midPointMatrix(x.T.dot(y))
				y_2_min = x.T.dot(y_min)
				y_2_max = x.T.dot(y_max)
				
				#Calculated predictors beta
				z_min = (x_1).dot(y_2_min)
				z_max = (x_1).dot(y_2_max)
				
				#print(z.data)


				#self._predictorsLow = (Rdmia.array([z_min.data[i][0] for i in range(len(z_min.data))]))
				#self._predictorsUp = (Rdmia.array([z_max.data[i][0] for i in range(len(z_max.data))]))
				
				opt_min,opt_max = self._optimizations(x_data,(Rdmia.array([z_min.data[i][0] for i in range(len(z_min.data))])),
				(Rdmia.array([z_max.data[i][0] for i in range(len(z_max.data))])),y_min,y_max)

				if(i==0):
					self._predictorsLow = (Rdmia.array([z_min.data[i][0] for i in range(len(z_min.data))]))
					self._predictorsUp = (Rdmia.array([z_max.data[i][0] for i in range(len(z_max.data))]))
					opt_minimum = opt_min
					opt_maximum = opt_max
				elif(opt_min < opt_minium):
					self._predictorsLow = (Rdmia.array([z_min.data[i][0] for i in range(len(z_min.data))]))
					opt_minimum = opt_min
				elif(opt_max < opt_maximum):
					self._predictorsUp = (Rdmia.array([z_max.data[i][0] for i in range(len(z_max.data))]))
					opt_maximum = opt_max
			
			
		#Calculte Status
		y_pred = self.predict(x_data)
		self._coefDetermination = self._coefDetermination(y_data,y_pred)
		self._rmse = self._RMSE(y_data,y_pred)
		print ("### STATISTICS OF MODEL ###")
		print ("# RMSE: ",self._rmse)
		print ("# Coefficiente of Determination: ",self._coefDetermination)
		print ("#")


	def _preProcessingData(self,x,y):
		for i in range(len(y.data)):
			for k in range(len(x.data[0])):
				if(type(x.data[i][k]) is not Rdm):
					x.data[i][k] = Rdmia.number(x.data[i][k])
			if(type(y.data[i]) is not Rdm):
				y.data[i][0] = Rdmia.number(y.data[i][0])
		
	def _mean(self,d):
		mean = Rdmia.number(0.0)
		for val in d:
			mean+=val[0]

		return mean/len(d)


	def _coefDetermination(self,y,y_pred):
		y_mean = self._mean(y)
		num = 0.0
		den = 0.0
		for val in range(len(y)):
			den+=qm.midpoint(((y[val][0]) - y_mean)**2)
			num+=qm.midpoint(((y_pred[val]) - y_mean)**2)
		return num/den
	
	def _RMSE(self,y,y_pred):
		lower = 0.0
		upper = 0.0
		tot = 0.0
		for val in range(len(y)):
			lower+=(y[val][0].lower() - y_pred[val].lower())	
			upper+=(y[val][0].upper() - y_pred[val].upper())
		
		lower = (lower**2.0/len(y))**(1.0/2.0)
		upper = (upper**2.0/len(y))**(1.0/2.0)
		return lower,upper
	
if __name__=="__main__":

	Rdmia.setDotPrecision(2)
	'''
	x = Rdmia.array([[Rdmia.number(1),Rdmia.number(90,100)],
	[Rdmia.number(1),Rdmia.number(90,130)],
	[Rdmia.number(1),Rdmia.number(140,180)],
	[Rdmia.number(1),Rdmia.number(110,142)],
	[Rdmia.number(1),Rdmia.number(90,100)],
	[Rdmia.number(1),Rdmia.number(130,160)],
	[Rdmia.number(1),Rdmia.number(60,100)],
	[Rdmia.number(1),Rdmia.number(130,160)],
	[Rdmia.number(1),Rdmia.number(110,190)],
	[Rdmia.number(1),Rdmia.number(138,180)],
	[Rdmia.number(1),Rdmia.number(110,150)]])


	x = [[Rdmia.number(1),Rdmia.number(90,100)],
	[Rdmia.number(1),Rdmia.number(90,130)],
	[Rdmia.number(1),Rdmia.number(140,180)],
	[Rdmia.number(1),Rdmia.number(110,142)],
	[Rdmia.number(1),Rdmia.number(90,100)],
	[Rdmia.number(1),Rdmia.number(130,160)],
	[Rdmia.number(1),Rdmia.number(60,100)],
	[Rdmia.number(1),Rdmia.number(130,160)],
	[Rdmia.number(1),Rdmia.number(110,190)],
	[Rdmia.number(1),Rdmia.number(138,180)],
	[Rdmia.number(1),Rdmia.number(110,150)]]

	y = Rdmia.array([[Rdmia.number(44,68)],
	[Rdmia.number(60,72)],
	[Rdmia.number(56,90)],
	[Rdmia.number(70,112)],
	[Rdmia.number(54,72)],
	[Rdmia.number(70,100)],
	[Rdmia.number(63,75)],
	[Rdmia.number(72,100)],
	[Rdmia.number(76,98)],
	[Rdmia.number(86,96)],
	[Rdmia.number(86,100)]
	])

	y = [[Rdmia.number(44,68)],
	[Rdmia.number(60,72)],
	[Rdmia.number(56,90)],
	[Rdmia.number(70,112)],
	[Rdmia.number(54,72)],
	[Rdmia.number(70,100)],
	[Rdmia.number(63,75)],
	[Rdmia.number(72,100)],
	[Rdmia.number(76,98)],
	[Rdmia.number(86,96)],
	[Rdmia.number(86,100)]
	]
	'''

		
	y = Rdmia.array([[25],[13],[8],[20]])


	regressor = RLS()
	regressor.fit(x,y)
	ypred = regressor.predict(y)
	print (regressor)
	

