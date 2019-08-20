'''
Harmony Search  Optimization Algorithm (HS)
@author: zzw
@reference:
@log: 2019.6.9, create
'''
from soio.core.algorithm import Algorithm
from soio.core.solution import Solution
from soio.core.problem import FloatProblem
import time
import random

class HarmonySearch(Algorithm):

    def __init__(self,
                 problem: FloatProblem,
                 harmony_memory_size: int,
                 memory_consider_rate: float,
                 pitch_adjust_rate: float,
                 band_width: float,
                 max_nfes: int):

        self.problem = problem
        self.HMS = harmony_memory_size
        self.HMCR = memory_consider_rate
        self.PAR = pitch_adjust_rate
        self.bw = band_width
        self.max_nfes = max_nfes

        self.best_solution = None
        self.HM = None # Harmony Memory

    def get_worst_harmony_idx(self):
        worst_harmony_idx = 0
        for idx in range(1,self.HMS):
            if self.HM[idx].objective > self.HM[worst_harmony_idx].objective:
                worst_harmony_idx = idx
        return worst_harmony_idx

    def run(self):
        """ Execute the algorithm. """
        start_computing_time = time.time()
        self.HM = [self.problem.evaluate(self.problem.create_solution()) for _ in range(self.HMS)]
        worst_harmony_idx = self.get_worst_harmony_idx()
        terminate = False
        while True:
            if self.max_nfes < self.problem.nfes:
                terminate = True
                break
            new_harmony = Solution(self.problem.number_of_variables)
            for iv in range(self.problem.number_of_variables):
                if random.random() < self.HMCR:
                    pitch = self.HM[int(random.random()*self.HMS)].variables[iv]
                    if random.random() < self.PAR:
                        pitch = pitch + (2*random.random()-1)*self.bw
                        if pitch > self.problem.upper_bound[iv]:
                            pitch = self.problem.upper_bound[iv]
                        elif pitch < self.problem.lower_bound[iv]:
                            pitch = self.problem.lower_bound[iv]
                    new_harmony.variables[iv] = pitch
                else:
                    new_harmony.variables[iv] = random.uniform(self.problem.lower_bound[iv]*1.0, self.problem.upper_bound[iv]*1.0)
            self.problem.evaluate(new_harmony)
            if new_harmony.objective < self.HM[worst_harmony_idx].objective:
                self.HM[worst_harmony_idx] = new_harmony
                worst_harmony_idx = self.get_worst_harmony_idx()

        self.best_solution = self.HM[0]
        for harmony in self.HM:
            if harmony.objective < self.best_solution.objective:
                self.best_solution = harmony

        self.total_computing_time = time.time() - start_computing_time

    def get_result(self):
        return self.best_solution

    def get_name(self) -> str:
        return 'Harmony Search Optimizer'
