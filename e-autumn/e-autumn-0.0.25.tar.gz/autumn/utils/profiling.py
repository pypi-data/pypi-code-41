
import time
import copy
import matplotlib
import progressbar
import numpy as np
from loguru import logger

try:
    matplotlib.use('TKAgg')
    from matplotlib import pyplot as plt
except:
    pass


class Profiling(object):
    """
    The class Profiling is designed for perfomance test.

    Example:
        def fibonacci(i):
            if i > 0 and isinstance(i, int):
                num_list = [0, 1]
                if i < 2:
                    return num_list[i]
                elif i >= 2:
                    return (fibonacci(i - 2) + fibonacci(i - 1))
            else:
                return -1

        p = Profiling(action=fibonacci)

        @p.inputs_generator(name="g1", TYPE="A", MIN=1000, MAX=10000, STEP=1000)
        def generator1(index):
            return 11

        @p.inputs_generator(name="g2", TYPE="B", PER=1, GROUP=30)
        def generator2(index):
            return index

        p.run(generator_name="g1", times=5)
        p.run(generator_name="g2", times=5)
        p.plot("g2", 'g2.png')
        p.plot("g1", 'g1.png')

    :param action: the function that will be profiled
    """

    def __init__(self, action=None):
        self.action = action or (lambda x: x)
        self.generator = dict()
        self.pbar = progressbar.ProgressBar(
            max_value=progressbar.UnknownLength)

    def inputs_generator(self, name, TYPE, MIN=10, MAX=100, STEP=10, PER=1, GROUP=1):
        '''
        Decorator for function to generate the inputs

        Example:
            p = Profiling(action=fibonacci)

            @p.inputs_generator(name="g1", TYPE="A", MIN=1000, MAX=10000, STEP=1000)
            def generator1(index):
                return 11


            @p.inputs_generator(name="g2", TYPE="B", PER=1, GROUP=30)
            def generator2(index):
                return index

        :param name: the name of generator
        :param TYPE: the type of generator, and the value could only be ``A`` or ``B``.
            If type is ``A``, ``MIN``, ``MAX`` and ``STEP`` are required. And if type is ``B``, ``PER`` and ``GROUP`` are required
        :param MIN: the minimal call times
        :param MAX: the maximal call times
        :param STEP: the increment times of every step
        :param PER: the call time of every group
        :param GROUP: the mumber of groups

        :returns: Profiling.generator
        '''
        def wrapper(func):
            self.generator[name] = {
                "generator": func,
                "type": TYPE,
                "result": []
            }

            if TYPE == "A":
                self.generator[name]["min"] = MIN if MIN >= 0 else 0
                self.generator[name]["max"] = MAX if MIN <= MAX else MIN
                self.generator[name]["step"] = STEP if STEP <= MAX - \
                    MIN else MAX - MIN
            elif TYPE == "B":
                self.generator[name]["per"] = PER if PER >= 0 else 0
                self.generator[name]["group"] = GROUP if GROUP >= 1 else 1

        return wrapper

    def run(self, generator_name, times=1):
        """
        Schedule the profiling program to run

        :param generator_name: the name of generator 
        :param times: the running times for report
        """
        params = self.generator[generator_name]

        for k in range(times):
            result = {
                "x": [],
                "y": []
            }
            current = 0
            if params["type"] == "A":

                total = sum(
                    list(range(params["min"], params["max"], params["step"])))
                self.pbar = progressbar.ProgressBar(
                    max_value=total)
                logger.info(
                    "Selected generator[name:{}], times: {},  Total call times: {}", generator_name, k+1, total)
                for i in range(params["min"], params["max"], params["step"]):
                    start = time.time()
                    for j in range(i):
                        self.action(params["generator"](index=i))
                        current += 1
                        self.pbar.update(current)
                    time_cost = time.time() - start
                    result["x"].append(i)
                    result["y"].append(time_cost)
                self.generator[generator_name]["result"].append(
                    copy.deepcopy(result))

            elif params["type"] == "B":
                total = params["group"] * params["per"]
                logger.info(
                    "Selected generator[name:{}], times: {},  Total call times: {}", generator_name, k+1, total)
                self.pbar = progressbar.ProgressBar(
                    max_value=total)
                for i in range(params["group"]):
                    start = time.time()
                    for j in range(params["per"]):
                        self.action(params["generator"](index=i))
                        current += 1
                        self.pbar.update(current)
                    time_cost = time.time() - start
                    result["x"].append(i)
                    result["y"].append(time_cost)
                self.generator[generator_name]["result"].append(
                    copy.deepcopy(result))

    def plot(self, name, outfile=None):
        """
        Plot the profiling figure

        :param name: the name of generator 
        :param outfile: the filepath of output figure
        """
        plt.cla()
        plt.title(name)
        plt.ylabel("time cost(s)")
        for data in self.generator[name]["result"]:
            plt.plot(data["x"], data["y"])
        if outfile:
            plt.savefig(outfile)
        else:
            plt.show()
