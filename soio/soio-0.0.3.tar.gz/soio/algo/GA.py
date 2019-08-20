'''
Genetic Algorithm
@author: zzw

@log: 2019.5.9, create
'''
from soio.core.algorithm import Algorithm
from soio.core.problem import PermutationProblem
from soio.core.operator import Operator
import time

class GeneticAlgorithm(Algorithm):

    def __init__(self,
                 problem: PermutationProblem,
                 population_size: int,
                 offspring_size: int,
                 mutation: Operator,
                 crossover: Operator,
                 selection: Operator,
                 max_nfes: int):

        self.problem = problem
        self.population_size = population_size
        self.offspring_size = offspring_size
        self.max_iterations = int(max_nfes/population_size)

        self.mutation_operator = mutation
        self.crossover_operator = crossover
        self.selection_operator = selection

        self.best_solution = None


    def create_initial_population(self):
        return [self.problem.create_solution() for _ in range(self.population_size)]

    def evaluate(self, solution_list) ->None:
        for solution in solution_list:
            self.problem.evaluate(solution)
            if self.best_solution == None:
                self.best_solution = solution
            elif self.best_solution.objective > solution.objective:
                self.best_solution = solution

    def selection(self, population):
        mating_population = []
        for i in range(self.offspring_size):
            solution = self.selection_operator.execute(population)
            mating_population.append(solution)
        return mating_population

    def reproduction(self, mating_population):

        offspring_population = []
        for i in range(0, self.offspring_size, 2):
            parents = [mating_population[i], mating_population[i +1]]
            offspring = self.crossover_operator.execute(parents)

            for solution in offspring:
                self.mutation_operator.execute(solution)
                offspring_population.append(solution)

        return offspring_population

    def replacement(self, population, offspring_population):
        population.extend(offspring_population)
        population.sort(key=lambda s: s.objective)
        return population[:self.population_size]

    def run(self):
        """ Execute the algorithm. """
        start_computing_time = time.time()

        self.population = self.create_initial_population()
        self.evaluate(self.population)
        self.records = []

        for iter in range(self.max_iterations):
            mating_population = self.selection(self.population)
            offspring_population = self.reproduction(mating_population)
            self.evaluate(offspring_population)
            self.population = self.replacement(self.population, offspring_population)
            # or self.population = offspring_population
            self.records.append(self.best_solution.objective)

        self.total_computing_time = time.time() - start_computing_time

    def get_result(self):
        return self.best_solution

    def get_name(self) -> str:
        return 'Genetic algorithm'