"""
Jacob Thompson

Clustering.py
"""

import numpy as np
import scipy as sp
import scipy.stats
from matplotlib import pyplot as plot

from collections import defaultdict
import warnings

from JT.Utils import ProgressBar

def FindElbow(y):
    slope = np.diff(y)
    slope_0 = np.hstack([slope, slope[-1]])
    slope_1 = np.hstack([slope[0], slope])
    out = np.arctan(-abs(1 / slope_0)) + np.arctan(-abs(slope_1)) + np.pi / 2
    out[np.where(np.isnan(out))] = 1
    return np.argmin(out)

def GetCentroids(x, cats, centroids):
    for i in range(centroids.shape[0]):
        if x[np.where(cats == i)].size:
            centroids[i] = np.mean(x[np.where(cats == i)], axis = 0)
    return centroids

# Silhouette Analysis
def SilhouetteValues(x, cats, centroids):
    silhouette_values = np.ones(cats.shape) * -1
    for i in range(centroids.shape[0]):
        b = np.sum((x - centroids[i])[np.where(cats == i)] ** 2) / np.sum(cats == i)
        a = 0
        for j in range(centroids.shape[0]):
            if j != i:
                a += np.sum((x - centroids[j])[np.where(cats == i)] ** 2, axis = 1)
        if centroids.shape[0] > 1:
            a /= centroids.shape[0] - 1
            silhouette_values[np.where(cats == i)] = (a - b) / np.max(np.vstack([a, np.ones(a.shape) * b]), axis=0)
    return silhouette_values

def SilhouettePlot(x, cats, centroids):
    silhouette_values = SilhouetteValues(x, cats, centroids)
    y = []
    for i in range(centroids.shape[0]):
        y_i = silhouette_values[np.where(cats == i)]
        y_i.sort()
        y_i = np.flip(y_i)
        y.append(y_i)
    y = np.hstack(y)
    cats.sort()
    plot.scatter(np.arange(y.shape[0]), y, c=cats)

# Loss Functions
class HardLoss:
    def __init__(self):
        self.name = 'Average Distance Loss'
        self.optimization_method = FindElbow

    def __call__(self, x, cats, centroids):
        cost = 0
        for i in range(len(centroids)):
            diff = (x - centroids[i])[np.where(cats == i)]
            dist = (np.sum(diff * diff, axis=1, keepdims=True))
            cost += np.sum(dist)
        return cost

class SoftLoss:
    def __init__(self, beta):
        self.name = 'Responsibility Distance Loss'
        self.beta = beta
        self.optimization_method = FindElbow

    def __call__(self, x, cats, centroids):
        cost = 0
        for i in range(centroids.shape[0]):
            if np.sum(np.where(cats == i)) > 0:
                # print('sum:', np.sum(np.where(cats == i)))
                # print('centroids[i]:', centroids[i])
                diff = (x - centroids[i])[np.where(cats == i)]
                # print('diff:', diff)
                dist = (np.sum(diff * diff, axis=1, keepdims=True))
                # print('dist:', dist)
                a = np.exp(-self.beta * dist)
                # print('a:', np.sum(a / (sum(a) + 1e-40)))
                responsibility = a / (np.sum(a) + 1e-40)
                # print('responsibility:', responsibility)
                cost += np.sum(responsibility * dist)
                # print(cost)

        return cost / centroids.shape[0]

class DBI:
    def __init__(self):
        self.optimization_method = np.argmin
        self.name = 'Davies Bouldin Index'

    def __call__(self, x, cats, centroids):
        def Sig(i):
            n = np.sum(cats == i)
            return np.sum((x - centroids[i])[np.where(cats == i)] ** 2) / n

        out = 0
        for k in range(centroids.shape[0]):
            inside_max = 0
            sig_k = Sig(k)
            for j in range(centroids.shape[0]):
                if j != k:
                    sig_j = Sig(j)
                    dist = np.sum((centroids[k] - centroids[j]) ** 2)
                    inside = (sig_k + sig_j) / dist
                    if inside > inside_max:
                        inside_max = inside

            out += inside_max
        if out == 0:
            return np.inf
        else:
            return out / centroids.shape[0]
class CHI:
    def __init__(self):
        self.optimization_method = np.argmax
        self.name = 'Calinski-Haribasz Index'

    def __call__(self, x, cats, centroids):
        total_mean = np.mean(x, axis=0, keepdims=True)
        top = 0
        bot = 0
        for k in range(centroids.shape[0]):
            n = np.sum(cats == k)
            if n > 0:
                top += np.sum((centroids[k] - total_mean) ** 2) * n
                bot += np.sum((x - centroids[k])[np.where(cats == k)] ** 2)
        return (top / bot) * (x.shape[0] - centroids.shape[0]) / (centroids.shape[0])

class GaussianLoss:
    def __init__(self):
        self.optimization_method = FindElbow
        self.name = 'Gaussian Mixture Loss'

    def __call__(self, x, cats, centroids):
        densities = []
        pis = []
        for i in range(centroids.shape[0]):
            if np.sum(cats == i) <= 1:
                density = np.zeros((x.shape[0]))
                density[np.where(cats == i)] = 1
            else:
                covariance = np.cov(x[np.where(cats == i)].T)
                gaussian = (sp.stats.multivariate_normal(mean=centroids[i], cov=covariance, allow_singular=True))
                density = gaussian.pdf(x)

            pi = np.sum(cats == i) / x.shape[0]
            pis.append(pi)
            densities.append(density)

        densities = np.stack(densities).T
        pis = np.stack(pis)
        return -np.sum(np.log(np.sum(pis * densities, axis = 1) + 1e-99))

class SilhouetteLoss:
    def __init__(self):
        self.optimization_method = FindElbow
        self.name = 'Average Silhouette Value'

    def __call__(self, x, cats, centroids):
        return np.mean(SilhouetteValues(x, cats, centroids))


class SilhouetteLogLoss:
    def __init__(self):
        self.optimization_method = FindElbow
        self.name = 'Average Log Silhouette Value'

    def __call__(self, x, cats, centroids):
        return np.mean(np.log(SilhouetteValues(x, cats, centroids) + 1.0001))

# Clustering Methods
def HardKMeans(x, num=3):
    warnings.warn("deprecated: use the class method Hard_K_Means instead", DeprecationWarning)
    centroids = x[np.random.choice(np.arange(x.shape[0]), num), :]
    cent_diff = np.inf
    iteration = 0
    while cent_diff > 0.001 and iteration < 11:
        iteration += 1
        cent_diff = 0
        dists = []
        for centroid in centroids:
            diff = x - centroid
            dist = np.sqrt(np.sum(diff * diff, axis=1, keepdims=True))
            dists.append(dist)

        dists = np.hstack(dists)
        cats = np.argmin(dists, axis=1)
        cost = 0
        for i in range(centroids.shape[0]):
            centroid = np.mean(x[np.where(cats == i)], axis=0)
            cent_diff += np.sum(np.abs(centroid - centroids[i]))
            centroids[i] = centroid

            diff = (x - centroid)[np.where(cats == i)]
            dist = np.sqrt(np.sum(diff * diff, axis=1, keepdims=True))
            cost += np.sum(dist)

    return np.array([cats]).T, centroids, cost

class Hard_K_Means:
    def __init__(self):
        self.loss_func = HardLoss()
    def GetDistances(self, x):
        distances = []
        for centroid in self.centroids:
            difference = x - centroid
            distance = np.sqrt(np.sum(difference * difference, axis=1, keepdims=True))
            distances.append(distance)
        return np.hstack(distances)

    def Predict(self, x):
        return np.argmax(self.GetDistances(x), axis = 1)

    def Train(self, x, clusters, max_iterations = 1000, stop_difference = 1e-6):
        self.centroids = x[np.random.choice(np.arange(x.shape[0]), clusters), :]
        self.losses = [np.inf]

        for iteration in range(max_iterations):
            y_hat = self.Predict(x)
            self.centroids = GetCentroids(x, y_hat, self.centroids)
            self.losses.append(self.loss_func(x, y_hat, self.centroids))
            loss_diff = abs((self.losses[-1] - self.losses[-2]) / self.losses[-1])
            print(self.losses[-1])
            print('\rHard K-Means | Iterations: {:>7} | Loss Difference: {:>9,.4} | Loss: {:>9,.4}'.format(iteration, loss_diff, self.losses[-1]),ProgressBar(np.log(loss_diff) / np.log(stop_difference)), end = '')
            if loss_diff < stop_difference:
                break

        print()
        y_hat = self.Predict(x)
        return y_hat, self.centroids, self.losses[-1]


def SoftKMeans(x, beta=1., num=3, loss_func=HardLoss(), loss_threshold = 1e-6):
    warnings.warn("deprecated: use the class method Soft_K_Means instead", DeprecationWarning, stacklevel = 2)
    centroids = x[np.random.choice(np.arange(x.shape[0]), num), :]

    loss_new = 1.
    loss_diff = np.inf
    iteration = 0
    # print('\rSoft K-Means | Iterations: {:>7} | Loss Difference: {:>9,.4} | Loss: {:>9,.4}'.format(iteration, loss_diff, loss_new), ProgressBar(0 / np.log(loss_threshold)), end = '')
    while loss_diff > loss_threshold and iteration < 100:

        loss_old = loss_new
        iteration += 1
        responsibilities = []
        for centroid in centroids:
            diff = x - centroid
            dist = (np.sum(diff * diff, axis=1, keepdims=True))
            responsibility = np.exp(-beta * dist) / np.sum(np.exp(-beta * dist))
            responsibilities.append(responsibility)
        responsibilities = np.hstack(responsibilities)

        cats = np.argmax(responsibilities, axis=1, )
        centroids = GetCentroids(x, cats, centroids)

        loss_new = loss_func(x, cats, centroids)
        loss_diff = abs((loss_new - loss_old) / loss_new)
        print('\rSoft K-Means | Iterations: {:>7} | Loss Difference: {:>9,.4} | Loss: {:>9,.4}'.format(iteration, loss_diff, float(loss_new)), ProgressBar(np.log(loss_diff) / np.log(loss_threshold)), end = '')
    print()
    return cats, centroids, loss_new

class Soft_K_Means:
    def __init__(self, beta = 1.):
        self.beta = beta
        self.loss_func = HardLoss()#beta = self.beta)

    # def GetCentroids(self, x):

    def GetResponsibilities(self, x):
        responsibilities = []
        for centroid in self.centroids:
            diff = x - centroid
            dist = (np.sum(diff * diff, axis=1, keepdims=True))
            responsibility = np.exp(-self.beta * dist) / np.sum(np.exp(-self.beta * dist))
            responsibilities.append(responsibility)
        # print(np.hstack(responsibilities).shape)
        return np.hstack(responsibilities)

    def Predict(self, x):
        return np.argmax(self.GetResponsibilities(x), axis=1)

    def Train(self, x, clusters, max_iterations = 1000, stop_difference = 1e-6):
        self.centroids = x[np.random.choice(np.arange(x.shape[0]), clusters), :]
        self.losses = [np.inf]
        print('\rSoft K-Means | Iterations: {:>7} | Loss Difference: {:>9,.4} | Loss: {:>9,.4}'.format(0, np.inf, self.losses[-1]), ProgressBar(0 / np.log(stop_difference)), end = '')
        for iteration in range(max_iterations):
            y_hat = self.Predict(x)
            self.centroids = GetCentroids(x, y_hat, self.centroids)
            print(x.shape)
            self.losses.append(self.loss_func(x, y_hat, self.centroids))
            loss_diff = abs((self.losses[-1] - self.losses[-2]) / self.losses[-1])
            # print(self.losses[-1])
            print('\rSoft K-Means | Iterations: {:>7} | Loss Difference: {:>9,.4} | Loss: {:>9,.4}'.format(iteration, loss_diff, float(self.losses[-1])), ProgressBar(np.log(loss_diff) / np.log(stop_difference)), end = '')
            if loss_diff < stop_difference:
                break
        print()
        y_hat = self.Predict(x)
        return y_hat, self.centroids, self.losses[-1]


class Gaussian_Mixture:
    def __init__(self):
        self.loss_func = GaussianLoss()

    def Train(self, x, clusters, max_iterations = 1000, stop_difference = 1e-6, prime = True):
        if prime:
            primer = Soft_K_Means()
            y_hat, self.centroids, loss = primer.Train(x, clusters = clusters, stop_difference = 1e-2)
        else:
            self.centroids = x[np.random.choice(np.arange(x.shape[0]), clusters),:]
        m = np.random.rand(clusters, x.shape[1], x.shape[1])
        self.covariances = m @ m.transpose((0, 2, 1))
        # self.covariances = np.stack([np.eye(x.shape[1])] * clusters)
        self.losses = [np.inf]
        for iteration in range(max_iterations):

            y_hat = self.Predict(x)

            self.losses.append(self.loss_func(x, y_hat, self.centroids))

            loss_diff = abs((self.losses[-1] - self.losses[-2]) / self.losses[-1])
            iteration += 1
            print('\rGaussian Mixture | Iterations: {:>7} | Loss Difference: {:>9,.4} | Loss: {:>9,.4}'.format(iteration, loss_diff, self.losses[-1]), ProgressBar(np.log(loss_diff) / np.log(stop_difference)), end = '')
            if loss_diff < stop_difference:
                break
            covariances = []
            for cluster in range(clusters):
                if x[np.where(y_hat == cluster)].size:
                    self.centroids[cluster] = np.mean(x[np.where(y_hat == cluster)], axis=0)

                covariance = np.cov(x[np.where(y_hat == cluster)].T)
                if np.isnan(covariance).any():
                    covariance = np.eye(covariance.shape[0])
                covariances.append(covariance)

            self.covariances = np.stack(covariances)

        pis = []
        for cluster in range(clusters):
            pi = np.sum(y_hat == cluster) / x.shape[0]
            pis.append(pi)
        self.pis = np.stack(pis)
        y_hat = self.Predict(x)
        print()
        return y_hat

    def Predict(self, x):
        return np.argmax(self.GetDensities(x), axis = 0)

    def GetDensities(self, x):
        self.densities = []
        for i in range(self.centroids.shape[0]):
            gaussian = (
                    sp.stats.multivariate_normal(mean=self.centroids[i], cov=self.covariances[i], allow_singular=True))
            density = gaussian.pdf(x)
            self.densities.append(density)
        return np.stack(self.densities)

    def Compress(self, x):
        y_hat = self.Predict(x)
        return self.centroids[y_hat]

    def Generate(self, num):
        sample_sizes = np.random.multinomial(num, pvals=self.pis)

        samples = []
        for i, clusters in enumerate(sample_sizes):
            samples.append(np.random.multivariate_normal(mean=self.centroids[i, :], cov=self.covariances[i, :, :], size=clusters))
        samples = np.vstack(samples)
        return samples

# Analysis

def ClusterAnalysis(x, start = 1, stop = 25, attempts = 5, beta = 0.1, loss_functions = (HardLoss(), DBI(), CHI(), SilhouetteLoss(), SilhouetteLogLoss(), GaussianLoss())):

    losses_dict = defaultdict(list)

    for i in range(start, stop):
        cats, centroids, cost = SoftKMeans(x, beta, i)
        for loss_func in loss_functions:
            nans = 0
            loss_agg = 0
            for _ in range(attempts):
                try:
                    loss = loss_func(x, cats, centroids)
                    if np.isnan(loss):
                        nans += 1
                    else:
                        loss_agg += loss
                except:
                    nans += 1
            if (attempts - nans) > 0:
                loss_avg = loss_agg / (attempts - nans)
            else:
                loss_avg = np.nan
            losses_dict[loss_func.name].append(loss_avg)

    plot.figure(figsize = (10, 5 * len(loss_functions)))

    predictions = []
    i = 0

    for loss_func in loss_functions:
        i += 1
        losses = losses_dict[loss_func.name]

        predictions.append(loss_func.optimization_method(losses))

        plot.figure(figsize = (10, 5))
        plot.plot(np.arange(1, len(losses) + 1), losses)
        plot.scatter(predictions[-1] + 1, losses[predictions[-1]], c='r', marker='X')
        plot.title(loss_func.name)
        plot.xlim(1, len(losses))

    return sp.stats.mode(predictions)



class Gaussian_Mixture_Model:
    def __init__(self, x):
        self.x = x
        self.loss_func = GaussianLoss()

    # def Train(self, clusters):










