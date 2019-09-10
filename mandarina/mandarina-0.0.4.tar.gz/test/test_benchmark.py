import time
import unittest

from mandarina.benchmark import Benchmark


class TestBenchmark(unittest.TestCase):
    def test(self):
        pass

    def test_benchmark(self):
        execution_time = 0.1
        result = Benchmark.run(lambda: time.sleep(execution_time), 10, print_output=False)
        self.assertAlmostEqual(result[0], execution_time, 2)
        self.assertAlmostEqual(result[1], execution_time, 2)
