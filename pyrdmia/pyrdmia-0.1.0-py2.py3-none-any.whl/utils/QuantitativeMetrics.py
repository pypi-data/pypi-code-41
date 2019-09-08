from ..core import Rdmia as rdmia
from ..core import Rdm
from ..utils import RMath as ria
import numpy as np

__all__ = ["QuantitativeMetrics"]

class QuantitativeMetrics(object):
	
	#Performs the average interval method on the input data set.
	@staticmethod
	def average(intervalList):
		averageResult = rdmia.number(0.0)
		for i in range(len(intervalList)):
			averageResult += intervalList[i]/(len(intervalList))
		return averageResult

	#The default sort operation of Python on the lists of the lower and upper limits is used. 
	#After performing the median on the input data set.
	@staticmethod
	def median(intervalList):
		#lowers = []
		#uppers = []
		item = []
		for i in range(len(intervalList)):
			#lowers.append(intervalList[i].lower())
			#uppers.append(intervalList[i].upper())
			item.append(intervalList[i])
		
		#lowers.sort()
		#uppers.sort()
		item.sort()

		half=int(len(intervalList)/2)

		if((len(intervalList)%2) == 0):
			#lower = (lowers[half] + lowers[half-1])/2
			#upper = (uppers[half] + uppers[half-1])/2
			median = (item[half] + item[half-1])/2
			#Average = rdmia.number(lower,upper)
		else:
			#lower = lowers[half]
			#upper = uppers[half]
			median = (item[half])
			#Average = rdmia.number(lower,upper)
		#return Average
		return median

	#Performs the full span operation in the input data set.
	@staticmethod
	def fullSpan(intervalList):
		fspan = rdmia.number(0.0)
		#lowers = []
		#uppers = []
		item = []

		for i in range(len(intervalList)):
			#lowers.append(0)
			#uppers.append(0)
			item.append(0)
			#lowers[i] = intervalList[i].lower()
			#uppers[i] = intervalList[i].upper()
			item[i] = intervalList[i]

		#lowers.sort()
		#uppers.sort()
		item.sort()

		#if(intervalList[len(intervalList)-1].lower() > intervalList[0].upper()):
		#	upper = uppers[len(uppers)-1] - uppers[0]
		#	lower = lowers[len(lowers)-1] - lowers[0]
		#	fspan = rdmia.number(lower,upper)
		#else:
		#	upper = lowers[len(intervalList)-1] - lowers[0]
		#	fspan = rdmia.number(0, upper)
		fspan = item[len(intervalList)-1] - item[0]
		return fspan

	#The variance operation is used the average operation of that class, getting a list of inervalares values.
	@staticmethod
	def variance(intervalList):
		variance = rdmia.number(0.0)
		for i in range(len(intervalList)):
			variance += (intervalList[i] - QuantitativeMetrics.average(intervalList))**2.0
		variance = variance/len(intervalList)
		return variance

	#The standard deviation depends of the variance applied to the data set received to perform the calculation.
	@staticmethod
	def stdDeviation(intervalList):
		standardDeviation = ria.sqrt(QuantitativeMetrics.variance(intervalList))
		return standardDeviation

	#The coefficient of variation depends on the mean and standard deviation operations.
	@staticmethod
	def coefVariance(intervalList):
		coefVariance = QuantitativeMetrics.stdDeviation(intervalList)/QuantitativeMetrics.average(intervalList)
		return coefVariance

	#This method has dependence of the average operation to correct performance of its calculation.
	#Two lists of data are necessary.
	@staticmethod
	def coVariance(intervalListOne, intervalListTwo):
		coVariance = rdmia.number(0.0,0.0)
		AverageX = QuantitativeMetrics.average(intervalListOne)
		AverageY = QuantitativeMetrics.average(intervalListTwo)

		if((len(intervalListOne)) <= (len(intervalListTwo))):
			n = len(intervalListOne)
		else:
			n = len(intervalListTwo)

		for i in range(n):
			#productXlow = intervalListOne[i].lower() - AverageX.upper()
			productX = intervalListOne[i] - AverageX
			#productXupp = intervalListOne[i].upper() - AverageX.lower()
			#productYlow = intervalListTwo[i].lower() - AverageY.upper()
			productY = intervalListTwo[i] - AverageY
			#productYupp = intervalListTwo[i].upper() - AverageY.lower()
			#X = rdmia.number(productXlow,productXupp)
			#Y = rdmia.number(productYlow,productYupp)
			#coVariance+=X*Y
			coVariance+=productX * productY
		return coVariance/(n)

	#This method contains dependence of the correlation coefficient used when needed to determine the correlation between two sets of data
	@staticmethod
	def coefCorrelation(intervalListOne, intervalListTwo):
		coefCorrelation = QuantitativeMetrics.coVariance(intervalListOne, intervalListTwo)/(QuantitativeMetrics.stdDeviation(intervalListOne)*QuantitativeMetrics.stdDeviation(intervalListTwo))
		return coefCorrelation