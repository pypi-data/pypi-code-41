"""
Jacob Thompson

Trees.py
"""


from copy import copy
import numpy as np
import scipy as sp
import scipy.stats

def Gini(y, axis = 0):
    out = 0
    for cat in np.unique(y):
        out += np.sum(y == cat, axis = axis, keepdims = True) / y.shape[0] + (1 - np.sum(y == cat, axis = axis, keepdims = True) / y.shape[0])
    return out


def InformationGain(x_k, y, t):
    z_0 = x_k < t
    z_1 = x_k >= t
    return Gini(y) - (Gini(y[np.where(z_0)]) * np.sum(z_0) + Gini(y[np.where(z_1)]) * np.sum(z_1)) / y.shape[0]

def Mode(z, axis = 0):
    return sp.stats.mode(z, axis = axis).mode


class Tree:
    def __init__(self, error_func=Gini, decision_func=Mode, stop_gain=0, max_depth=5, steps=-1):
        self.error_func = error_func
        self.decision_func = decision_func
        self.max_depth = max_depth
        self.stop_gain = stop_gain
        self.steps = steps

    def Train(self, x, y):
        self.x = x
        self.y = y
        self.size = y.shape[1]
        self.out = np.zeros(y.shape)
        if self.steps < 0:
            self.steps = self.x.shape[0]
        self.root = self.Node(self, np.where(np.ones(y.shape, dtype=bool))[0], self.max_depth)
        self.root.Split()
        del self.x
        del self.y
        return self.out

    def Predict(self, x):
        self.x = x
        self.out = np.zeros((x.shape[0], self.size))
        self.root.Predict(np.where(np.ones(x.shape[0], dtype=bool))[0])
        return self.out

    class Node:
        def __init__(self, parent, mask, height):
            self.size = np.sum(mask)
            self.height = height
            self.parent = parent
            if self.height == 0 or self.size == 1 or np.unique(self.y[mask]).size == 1:
                self.y_hat = self.decision_func(self.y[mask])
                self.out[mask] = self.y_hat
            else:
                self.mask = mask
                self.y_hat = None
                self.error = self.error_func(self.y[self.mask], axis = 0)

        def __getattr__(self, name):
            return self.parent.__getattribute__(name)

        def Split(self):
            if self.y_hat is None:
                max_gain = -np.inf
                y_mask = self.y[self.mask]
                opt_left = None
                opt_right = None
                for col in range(self.x.shape[1]):
                    x_col = self.x[self.mask, col]
                    for t in np.linspace(np.min(x_col), np.max(x_col), self.steps):
                        left = x_col > t
                        right = ~left

                        error_left = self.error_func(y_mask[left], axis = 0)
                        n_left = np.sum(left)

                        error_right = self.error_func(y_mask[right], axis = 0)
                        n_right = np.sum(right)

                        gain = self.error - (error_right * n_right + error_left * n_left) / self.size
                        #                         gains.append(gain)
                        if np.sum(gain) > max_gain:
                            opt_left = left
                            opt_right = right
                            self.opt_col = col
                            self.opt_t = t
                            max_gain = np.sum(gain)
                del x_col
                del y_mask
                if np.any(opt_left) and np.any(opt_right) and max_gain > self.stop_gain:
                    # print(self.mask)
                    # print(np.where(opt_right)[0])
                    mask_right = self.mask[np.where(opt_right)[0]]
                    mask_left = self.mask[opt_left]
                    del self.mask

                    self.left = self.Node(self.parent, mask_left, self.height - 1)
                    self.left.Split()
                    self.right = self.Node(self.parent, mask_right, self.height - 1)
                    self.right.Split()
                else:
                    self.y_hat = self.decision_func(self.y[self.mask], axis = 0)
                    self.out[self.mask] = self.y_hat
                    # print(self.y_hat)
                    del self.mask



        def Predict(self, mask):
            if self.y_hat is None:
                # print(mask)
                left = self.x[mask, self.opt_col] > self.opt_t
                right = ~left
                self.left.Predict(mask[np.where(left)[0]])
                self.right.Predict(mask[np.where(right)[0]])


            else:
                # print(self.y_hat)
                # print(mask.shape)
                self.out[mask] = self.y_hat


class Forest:
    def __init__(self, num, sample_size, subset_proportion=1, root_tree=Tree()):
        self.num = num
        self.root_tree = root_tree
        self.subset_proportion = subset_proportion
        self.sample_size = sample_size
        self.decision_func = self.root_tree.decision_func

    def Train(self, x, y):
        self.trees = []
        subsets = int(np.ceil(x.shape[1] * self.subset_proportion))
        self.subsets = []
        for i in range(self.num):
            self.subsets.append(np.random.choice(np.arange(x.shape[1]), size=subsets, replace=False))
            sample_indices = np.random.randint(0, x.shape[0], size=self.sample_size)
            self.trees.append(copy(self.root_tree))
            self.trees[-1].Train(x[sample_indices, :][:, self.subsets[-1]], y[sample_indices])

    def Predict(self, x):
        y_hats = []
        for i in range(self.num):
            y_hats.append(self.trees[i].Predict(x[:, self.subsets[i]]))

        y_hats = np.stack(y_hats)
        y_hat = self.decision_func(y_hats, axis=0)
        return y_hat