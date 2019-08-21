import numpy as np
import matplotlib
import matplotlib.pyplot as plt


def functionviewer(afunction,brange): 
	x = np.arange(brange[0],brange[1],(brange[1]-brange[0])/100)
	y = np.zeros(len(x)) 
	for i in range(len(x)):
		y[i]=afunction(x[i])
	plt.plot(x,y)
	plt.show()