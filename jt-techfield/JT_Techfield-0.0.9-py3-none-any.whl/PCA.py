import numpy as np

def Eigen(x):
    eigen_values, eigen_vectors = np.linalg.eig(x.T @ x)
    sort_indices = np.argsort(eigen_values)[::-1]
    return eigen_values[sort_indices], eigen_vectors[:, sort_indices]

class PCA:
    def Train(self, x):
        self.eigen_values, self.eigen_vectors = np.linalg.eig(x.T @ x)
        self.sort_indices = np.argsort(self.eigen_values)[::-1]

    def Encode(self, x, components):
        return x @ self.eigen_vectors[:, self.sort_indices[:components]]

    def Decode(self, x):
        return x @ self.eigen_vectors[:, self.sort_indices[:x.shape[-1]]].T

    def Filter(self, x, components):
        return self.Decode(self.Encode(x, components))



