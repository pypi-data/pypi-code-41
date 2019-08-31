import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as mp3d

def functionviewer(afunction,brange): 
	x = np.arange(brange[0],brange[1],(brange[1]-brange[0])/100)
	y = np.zeros(len(x)) 
	for i in range(len(x)):
		y[i]=afunction(x[i])
	plt.plot(x,y)
	plt.show()

def pointviewer(pointlists):
	colorlist=['r','b','k','g','y','c','m','gold','dodgerblue','orange']
	fig = plt.figure()
	ax = mp3d.Axes3D(fig)
	for l in range(len(pointlists)):
		for p in pointlists[l]:
			ax.scatter(p[0], p[1], p[2], c=colorlist[l])
	plt.show()