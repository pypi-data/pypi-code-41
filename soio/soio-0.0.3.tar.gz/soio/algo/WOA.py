'''
Whale Optimization Algorithm
@author: zzw
@reference: Mirjalili, S., & Lewis, A. (2016).
                    The Whale Optimization Algorithm.
                    Advances in Engineering Software, 95:51-67.
                    doi:https://doi.org/10.1016/j.advengsoft.2016.01.008

@log: 2019.5.14, creation
'''
from soio.core.algorithm import Algorithm
from soio.core.solution import Solution
from soio.core.problem import FloatProblem
import time
import numpy as np
import random
import math

class WhaleOptimizer(Algorithm):

    def __init__(self,
                 problem: FloatProblem,
                 swarm_size: int,
                 max_nfes: int):

        self.problem = problem
        self.swarm_size = swarm_size
        self.max_iterations = int(max_nfes/swarm_size)

        self.best_solution = Solution(self.problem.number_of_variables)
        self.best_solution.objective = float("inf")

    def create_initial_swarm(self) -> np.ndarray:
        """ Creates the initial list of solutions of a metaheuristic. """
        return [self.problem.create_solution() for _ in range(self.swarm_size)]

    def evaluate(self, swarm):
        """ Evaluates the swarm. """
        for i in range(self.swarm_size):
            swarm[i] = self.problem.evaluate(swarm[i])
            if swarm[i].objective < self.best_solution.objective:
                self.best_solution = swarm[i]

        return swarm

    def run(self):
        """ Execute the algorithm. """
        start_computing_time = time.time()

        self.swarm = self.create_initial_swarm()
        self.swarm = self.evaluate(self.swarm)
        self.records = []

        for iter in range(self.max_iterations):
            a = 2 - iter * ((2) / self.max_iterations)  # a decreases linearly fro 2 to 0
            a2 = -1 + iter * ((-1) / self.max_iterations) #  a2 linearly decreases from -1 to -2

            for i in range(self.swarm_size):
                r1 = random.random()
                r2 = random.random()
                A = 2 * a * r1 - a
                C = 2 * r2
                b = 1
                l = (a2 - 1) * random.random() + 1

                p = random.random()
                new_whale = Solution(self.problem.number_of_variables)
                for j in range(0, self.problem.number_of_variables):

                    if p < 0.5:
                        if abs(A) >= 1:
                            rand_leader_index = random.randint(0, self.swarm_size-1)
                            X_rand = self.swarm[rand_leader_index].variables
                            D_X_rand = abs(C * X_rand[j] - self.swarm[i].variables[j])
                            new_whale.variables[j] = X_rand[j] - A * D_X_rand

                        elif abs(A) < 1:
                            D_Leader = abs(C * self.best_solution.variables[j] - self.swarm[i].variables[j])
                            new_whale.variables[j] = self.best_solution.variables[j] - A * D_Leader

                    elif p >= 0.5:
                        distance2Leader = abs(self.best_solution.variables[j] - self.swarm[i].variables[j])
                        new_whale.variables[j] = distance2Leader * math.exp(b * l) * math.cos(l * 2 * math.pi) + self.best_solution.variables[j]

                new_whale.variables = np.clip(new_whale.variables, self.problem.lower_bound, self.problem.upper_bound).tolist()
                self.swarm[i]=new_whale


            self.evaluate(self.swarm)
            self.records.append(self.best_solution.objective)

        self.total_computing_time = time.time() - start_computing_time

    def get_result(self):
        return self.best_solution

    def get_name(self) -> str:
        return 'Whale Optimization Algorithm'

