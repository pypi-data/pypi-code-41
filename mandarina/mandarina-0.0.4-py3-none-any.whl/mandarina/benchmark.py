"""
This module contains benchmarking tools for functions.
"""

import random
import time
import sys
import statistics


class Benchmark:
    """
    This class runs a benchmark on a function passed to the
    run method. It calls the function a specified number of times
    and calculates the mean and standard deviation across all runs.
    """

    @staticmethod
    def run(function, runs, print_output=True):
        """
        The run method prints the benchmark statistics when called
        with a function as parameter. If you set print_output to False,
        the function will only return the final value without printing
        anything to the console.

        :param function: The function to benchmark
        :return: The mean running time in seconds and its standard
                 deviation.

        Example
        >>> Benchmark.run(lambda: time.sleep(1), 100)

        """
        timings = []
        if print_output:
            print("Runs Median Mean Stddev")
        for i in range(runs):
            startTime = time.time()
            function()
            seconds = time.time() - startTime
            timings.append(seconds)
            median = statistics.median(timings)
            mean = statistics.mean(timings)
            if print_output:
                if i < 10 or i % 10 == 9:
                    print(
                        "{0}\t{1:3.2f}\t{2:3.2f}\t{3:3.2f}".format(
                            1 + i,
                            median,
                            mean,
                            statistics.stdev(timings, mean) if i > 1 else 0,
                        )
                    )
        return (median, mean, statistics.stdev(timings, mean))
