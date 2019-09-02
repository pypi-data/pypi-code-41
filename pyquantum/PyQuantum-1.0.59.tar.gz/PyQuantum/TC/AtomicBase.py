import numpy as np
import itertools


class AtomicBasis:
    def __init__(self, count, n_levels=2):
        self.basis = itertools.product(range(n_levels), repeat=count)

        self.basis = [list(i) for i in list(self.basis)]

        self.get_energy()

    def get_energy(self):
        self.base = []

        for i in self.basis:
            self.base.append([i, np.sum(i)])
            # print(np.sum(i))

    def print(self):
        for i in self.base:
            print(i)
