'''
Biogeography-Based Optimization
@author: zzw
@reference: Simon, D. 2008.
                    Biogeography-Based Optimization.
                    IEEE Transactions on Evolutionary Computation 12 (6):702-13.
                    doi: https://doi.org/10.1109/TEVC.2008.919004.
                    http://embeddedlab.csuohio.edu/BBO/
@log: 2019.7.25, create, still need improve
'''
from soio.core.algorithm import Algorithm
from soio.core.problem import FloatProblem
from soio.core.solution import Solution
import time
import random

class BBO(Algorithm):
    def __init__(self,
        problem: FloatProblem,
        habitats_size: int,
        max_nfes: int,
    ):
        self.problem = problem
        self.habitats_size=habitats_size
        self.max_iterations = int(max_nfes/habitats_size)
        pass

    def run(self):
        """ Execute the algorithm. """
        self.records =[]
        start_computing_time = time.time()

        self.habitats = [self.problem.create_solution() for _ in range(self.habitats_size)]
        for habitat in self.habitats:
            self.problem.evaluate(habitat)
        self.habitats.sort(key=lambda x:x.objective)
        self.best_solution = self.habitats[0]
        assert self.habitats[0].objective < self.habitats[-1].objective

        self.immigrate_rates = []
        self.emigrate_rates = []
        for i in range(self.habitats_size):
            mu = (self.habitats_size+1-i)/(self.habitats_size+1)
            self.emigrate_rates.append(mu) #decreasing
            self.immigrate_rates.append(1-mu) #increasing
        self.mut_prob = 0.01
        self.keep=2

        for _  in range(self.max_iterations):
            # Migration
            new_habitats =[]
            new_habitats.append(self.habitats[0])
            for hi in range(1,self.habitats_size):
                new_habitat = Solution(self.problem.number_of_variables)
                for vi in range(self.problem.number_of_variables):
                    if random.random() < self.immigrate_rates[hi]:
                        # Roulette Wheel Selection
                        rhi = self.roulette_wheel_selection()
                        new_habitat.variables[vi] = self.habitats[rhi].variables[vi]
                    else:
                        new_habitat.variables[vi] = self.habitats[hi].variables[vi]
                new_habitats.append(new_habitat)

            # Mutation
            for hi in range(self.habitats_size):
                for vi in range(self.problem.number_of_variables):
                    if random.random() < self.mut_prob:
                        new_habitats[hi].variables[vi] = self.problem.lower_bound[vi] + \
                                               (self.problem.upper_bound[vi]-self.problem.lower_bound[vi])*random.random()

            for habitat in new_habitats:
                self.problem.evaluate(habitat)

            new_habitats.sort(key=lambda x:x.objective)
            new_habitats[self.habitats_size-self.keep:] = self.habitats[:self.keep]
            self.habitats = sorted(new_habitats, key=lambda x:x.objective)
            assert len(self.habitats)==self.habitats_size

            self.best_solution = self.habitats[0]
            self.records.append(self.best_solution.objective)



    def roulette_wheel_selection(self):
        r = random.random()*sum(self.emigrate_rates)
        s = self.emigrate_rates[0]
        si = 0
        while (r>s) and (si<(self.habitats_size-1)):
            si += 1
            s += self.emigrate_rates[si]
        return si



    def get_result(self):
        return self.best_solution

    def get_name(self) -> str:
        return 'Biogeography-Based Optimization'