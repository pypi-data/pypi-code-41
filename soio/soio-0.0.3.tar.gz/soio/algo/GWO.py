'''
Grey WOlf OptimizationAlgorithm
@author: zzw
@reference: Mirjalili, S., S. M. Mirjalili, and A. Lewis. 2014.
                    Grey Wolf Optimizer."
                    Advances in Engineering Software 69:46-61
                    doi: 10.1016/j.advengsoft.2013.12.007.

@log: 2019.5.12, create
'''
from soio.core.algorithm import Algorithm
from soio.core.solution import Solution
from soio.core.problem import FloatProblem
import time
import numpy as np
import copy

class GreyWolfOptimizer(Algorithm):

    def __init__(self,
                 problem: FloatProblem,
                 swarm_size: int,
                 max_nfes: int):

        self.problem = problem
        self.swarm_size = swarm_size
        self.max_iterations = int(max_nfes/swarm_size)

        self.alpha_wolf = Solution(self.problem.number_of_variables)
        self.alpha_wolf.objective = float("inf")
        self.beta_wolf = Solution(self.problem.number_of_variables)
        self.beta_wolf.objective = float("inf")
        self.delta_wolf = Solution(self.problem.number_of_variables)
        self.delta_wolf.objective = float("inf")

    def create_initial_swarm(self):
        """ Creates the initial list of solutions of a metaheuristic. """
        return [self.problem.create_solution() for _ in range(self.swarm_size)]

    def evaluate(self, swarm):
        """ Evaluates the swarm. """
        for i in range(self.swarm_size):
            swarm[i] = self.problem.evaluate(swarm[i])
            if swarm[i].objective < self.alpha_wolf.objective:
                self.delta_wolf = self.beta_wolf
                self.beta_wolf = self.alpha_wolf
                self.alpha_wolf = swarm[i]

            elif swarm[i].objective < self.beta_wolf.objective:
                self.delta_wolf = self.beta_wolf
                self.beta_wolf =  copy.copy(swarm[i])

            elif swarm[i].objective < self.delta_wolf.objective:
                self.delta_wolf =  copy.copy(swarm[i])
        return swarm

    def run(self):
        """ Execute the algorithm. """
        start_computing_time = time.time()

        self.swarm = self.create_initial_swarm()
        self.evaluate(self.swarm)
        self.records = []

        for iter in range(self.max_iterations):
            a = 2 - iter * 2 / self.max_iterations  # a decreases linearly fro 2 to 0
            r1 = np.random.random((3, self.swarm_size, self.problem.number_of_variables))
            r2 = np.random.random((3, self.swarm_size, self.problem.number_of_variables))
            A1 = 2 * a * r1[0] - a
            C1 = 2 * r2[0]
            A2 = 2 * a * r1[1] - a
            C2 = 2 * r2[1]
            A3 = 2 * a * r1[2] - a
            C3 = 2 * r2[2]

            for i in range(self.swarm_size):
                wolf = self.swarm[i]
                D_alpha = np.abs(C1[i] * self.alpha_wolf.variables - wolf.variables)
                X1 = self.alpha_wolf.variables - A1[i] * D_alpha

                D_beta = np.abs(C2[i] * self.beta_wolf.variables - wolf.variables)
                X2 = self.beta_wolf.variables - A2[i] * D_beta

                D_delta = np.abs(C3[i] * self.delta_wolf.variables - wolf.variables)
                X3 = self.delta_wolf.variables - A3[i] * D_delta

                new_pos = (X1 + X2 + X3) / 3
                new_pos = np.clip(new_pos, self.problem.lower_bound, self.problem.upper_bound)

                new_wolf = Solution(self.problem.number_of_variables)
                new_wolf.variables = list(new_pos)
                self.swarm[i] = new_wolf

            self.swarm = self.evaluate(self.swarm)
            self.records.append(self.alpha_wolf.objective)

        self.total_computing_time = time.time() - start_computing_time

    def get_result(self):
        return self.alpha_wolf

    def get_name(self) -> str:
        return 'Grey Wolf Optimizer'










