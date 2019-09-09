import numpy as np
import scipy as sp
from scipy import stats

# TODO: Write this entire module

'''
## Standard K-NN
y_hat = []
k = 0
for point in x_sim:
    diff = x - point
    dist = np.sqrt(np.sum(diff * diff, axis = 1))
    nearest = np.argsort(dist)[:k]
    cat = sp.stats.mode(np.argmax(y[nearest], axis = 1))
    y_hat.append(cat.mode[0])
plot.scatter(x_sim[:, 0], x_sim[:, 1], c = y_hat)
'''

def Nothing(dist):
    return dist

class KNearest:
    def __init__(self, x, y, method = None):
        self.x = x
        self.y = y
        self.method = method

    def Predict(self, x, k):
        y_hat = []
        for point in x:
            diff = self.x - point
            dist = np.sqrt(np.sum(diff * diff, axis = 1))
            nearest = np.argsort(dist)[:k]
            w = self.method(dist[nearest])