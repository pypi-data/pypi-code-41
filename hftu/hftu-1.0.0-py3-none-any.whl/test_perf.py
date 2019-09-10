import time
from random import randint
from sklearn.datasets import make_blobs
from test import support
import unittest
from .optimization import heuristic_optimizer_random_parallel
from .optimization import legacy_optimizer_random_parallel
from .hftu import HFTU
# from .oblas import get_num_threads
import os


def gen_data(n, d, n_clusters, n_rep):
    for i in range(n_rep):
        X, _ = make_blobs(n_samples=n,
                          n_features=d,
                          centers=n_clusters,
                          random_state=i)
        yield X


class TestPerf(unittest.TestCase):
    def setUp(self):
        self.n_rep = 5
        self.n = 100000
        self.d = 5
        self.n_clusters = 2
        self.n_init = 10
        # print("\nNumber of OpenBLAS threads:", get_num_threads())

    def test_legacy_variance_fit(self):
        H = HFTU()
        a = time.time()
        for X in gen_data(self.n, self.d, self.n_clusters, self.n_rep):
            H.fit(X, method='legacy', init='variance')
        b = time.time()
        print("{:.2f} it/s".format(self.n_rep / (b - a)))

    def test_legacy_random_fit(self):
        H = HFTU()
        a = time.time()
        for X in gen_data(self.n, self.d, self.n_clusters, self.n_rep):
            H.fit(X, method='legacy', init='random', n_init=self.n_init)
        b = time.time()
        print("{:.2f} it/s".format(self.n_rep / (b - a)))

    def test_heuristic_random_fit(self):
        H = HFTU()
        a = time.time()
        for X in gen_data(self.n, self.d, self.n_clusters, self.n_rep):
            H.fit(X, method='heuristic', init='random', n_init=self.n_init)
        b = time.time()
        print("{:.2f} it/s".format(self.n_rep / (b - a)))

    def test_heuristic_variance_fit(self):
        H = HFTU()
        a = time.time()
        for X in gen_data(self.n, self.d, self.n_clusters, self.n_rep):
            H.fit(X, method='heuristic', init='variance')
        b = time.time()
        print("{:.2f} it/s".format(self.n_rep / (b - a)))

    def test_heuristic_random_parallel_fit(self):
        H = HFTU()
        a = time.time()
        for X in gen_data(self.n, self.d, self.n_clusters, self.n_rep):
            H.fit(X, method='heuristic', init='random', n_init=self.n_init, n_jobs=4)
        b = time.time()
        print("{:.2f} it/s".format(self.n_rep / (b - a)))

    def test_legacy_random_parallel_fit(self):
        H = HFTU()
        a = time.time()
        for X in gen_data(self.n, self.d, self.n_clusters, self.n_rep):
            H.fit(X, method='legacy', init='random', n_init=self.n_init, n_jobs=4)
        b = time.time()
        print("{:.2f} it/s".format(self.n_rep / (b - a)))

    # def test_parallel_heuristic(self):
    #     a = time.time()
    #     # PH = ParallelHeuristic(4, 30, 1e-5)
    #     for X in gen_data(self.n, self.d, self.n_clusters, self.n_rep):
    #         # parallel_heuristic(X, 8, 15, 1e-4)
    #         heuristic_optimizer_random_parallel(
    #             X=X, n_init=self.n_init, max_ite=30, tol=1e-4, n_jobs=4)
    #         # PH = ParallelHeuristic(X, 15, 1e-4)
    #         # PH.run(X, 10)
    #     b = time.time()
    #     print("{:.2f} it/s".format(self.n_rep / (b - a)))

    # def test_parallel_legacy(self):
    #     a = time.time()
    #     for X in gen_data(self.n, self.d, self.n_clusters, self.n_rep):
    #         legacy_optimizer_random_parallel(
    #             X=X, n_init=self.n_init, slsqp_opt={'maxiter': 300}, n_jobs=4)
    #     b = time.time()
    #     print("{:.2f} it/s".format(self.n_rep / (b - a)))


if __name__ == '__main__':
    unittest.main()
