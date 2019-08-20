'''
Shuffled Cellluar Evolutionary Grey Wolf Optimizer
@author: zzw
@log: 2019.6.4, create
'''
from soio.core.algorithm import Algorithm
from soio.core.solution import Solution
from soio.core.problem import PermutationProblem
from soio.core.operator import Operator
import time
import numpy as np
import random

'''
Cellular Automata (2D)
'''
CA_L5 = [[0,-1], [0,1], [-1,0], [1,0]]
CA_L9 = [[0,-2], [0,-1], [0,1], [0,2], [-2,0], [-1,0], [2,0], [1,0]]
CA_C9 = [[-1,-1], [0,-1], [1,-1], [-1,0], [1,0], [-1,1], [0,1], [1,1]]
CA_C13 = [[0,-2], [-1,-1], [0,-1], [1,-1], [-2,0], [-1,0], [1,0], [2,0],
          [-1,1], [0,1], [1,1], [0, 2]]
CA_C21 = [[-1,-2], [0,-2], [1,-2],
          [-2,-1], [-1,-1], [0,-1], [1,-1], [2,-1],
          [-2,0], [-1,0], [1,0], [2,0],
          [-2,1], [-1,1], [0,1], [1,1], [2,1],
          [-1,2], [0,2], [1,2]]
CA_C25 = [[-2,-2], [-1,-2], [0,-2], [1,-2], [2,-2],
          [-2,-1], [-1,-1], [0,-1], [1,-1], [2,-1],
          [-2,0], [-1,0], [1,0], [2,0],
          [-2,1], [-1,1], [0,1], [1,1], [2,1],
          [-2,2], [-1,2], [0,2], [1,2], [2,2]]

def find_neighborhood(neighbor_structure, grid_catalog, coord):
    '''
    :param neighbor_structure:  2D list, Cellular Automata
    :param grid_catalog: 2D ndarray, wolf index in each celluar grid
    :param coord:  [x,y]
    :return:  neighborhood wolves indexes
    '''
    l,w = grid_catalog.shape
    neighbors = []
    for nc in neighbor_structure:
        nx = coord[0] + nc[0]
        ny = coord[1] + nc[1]

        if nx >= l:
            nx -= l
        elif nx < 0:
            nx += l

        if ny >= w:
            ny -= w
        elif ny < 0:
            ny += w

        neighbors.append(grid_catalog[nx,ny])
    return neighbors


class CellularGreyWolfOptimizer(Algorithm):
    def __init__(self,
                 problem: PermutationProblem,
                 mutation: Operator,
                 crossover: Operator,
                 max_nfes: int,
                 grid_shape = [20,20],
                 neighbor_structure = CA_C21,
                 ):

        self.problem = problem
        self.swarm_size = grid_shape[0]*grid_shape[1]
        self.max_nfes = max_nfes

        self.mutation_operator = mutation
        self.crossover_operator = crossover

        self.neighbor_structure = neighbor_structure
        self.grid_catalog = np.random.permutation(self.swarm_size).reshape(grid_shape)

        self.wolves_coords = [None]*self.swarm_size
        for i in range(grid_shape[0]):
            for j in range(grid_shape[1]):
                self.wolves_coords[self.grid_catalog[i][j]] = [i,j]

        self.best_solution = Solution(self.problem.number_of_variables)
        self.best_solution.objective = float("inf")

        self.grid_shape = grid_shape


    def create_initial_swarm(self) -> np.ndarray:
        """ Creates the initial list of solutions of a metaheuristic. """
        swarm = [self.problem.create_solution() for _ in range(self.swarm_size)]
        return swarm


    def shuffle_swarm(self):
        # shuffle
        self.grid_catalog = np.random.permutation(self.swarm_size).reshape(self.grid_shape)

        self.wolves_coords = [None] * self.swarm_size
        for i in range(self.grid_shape[0]):
            for j in range(self.grid_shape[1]):
                self.wolves_coords[self.grid_catalog[i][j]] = [i, j]

    def run(self):
        """ Execute the algorithm. """
        start_computing_time = time.time()

        self.swarm = self.create_initial_swarm()
        best_i = None
        for i in range(self.swarm_size):
            self.swarm[i] = self.problem.evaluate(self.swarm[i])
            if self.swarm[i].objective < self.best_solution.objective:
                self.best_solution = self.swarm[i]

        self.records = []
        terminate = False
        while True:
            if terminate:
                break

            update = False

            for i in range(self.swarm_size):
                if self.max_nfes < self.problem.nfes:
                    terminate = True
                    break
                wolf = self.swarm[i]
                new_wolf = None
                coord = self.wolves_coords[i]
                neighbors = find_neighborhood(self.neighbor_structure, self.grid_catalog, coord)
                alpha_wolf, beta_wolf, delta_wolf  = self.select_best_three_neigbors(neighbors)
                # social hierarchy
                new_wolf = None
                if wolf.objective == self.best_solution.objective:
                    new_wolf = self.mutation_operator.execute(wolf)
                elif wolf.objective < alpha_wolf.objective:
                    new_wolf = self.crossover_operator.execute([self.best_solution, wolf])
                elif wolf.objective < beta_wolf.objective:
                    new_wolf = self.crossover_operator.execute([alpha_wolf, wolf])
                elif wolf.objective < delta_wolf.objective:
                    if random.random() < 0.5:
                        new_wolf = self.crossover_operator.execute([alpha_wolf, wolf])
                    else:
                        new_wolf = self.crossover_operator.execute([beta_wolf, wolf])
                else:
                    r = random.random()
                    if r < 0.33:
                        new_wolf = self.crossover_operator.execute([alpha_wolf, wolf])
                    elif r < 0.66:
                        new_wolf = self.crossover_operator.execute([beta_wolf, wolf])
                    else:
                        new_wolf = self.crossover_operator.execute([delta_wolf, wolf])

                    new_wolf = self.mutation_operator.execute(new_wolf)

                    if new_wolf.objective == None:
                        self.problem.evaluate(new_wolf)
                    else:
                        self.problem.nfes += 1
                    # greedy
                    if new_wolf.objective < self.swarm[i].objective:
                        self.swarm[i] = new_wolf

                if new_wolf.objective < self.best_solution.objective:
                    self.best_solution = new_wolf
                    update = True

            if not update:
                self.shuffle_swarm()

            self.records.append(self.best_solution.objective)

        self.total_computing_time = time.time() - start_computing_time

    def select_best_three_neigbors(self, neighbors):
        alpha_wolf = Solution(self.problem.number_of_variables)
        alpha_wolf.objective = float("inf")
        beta_wolf = Solution(self.problem.number_of_variables)
        beta_wolf.objective = float("inf")
        delta_wolf = Solution(self.problem.number_of_variables)
        delta_wolf.objective = float("inf")
        for i in neighbors:
            if self.swarm[i].objective < alpha_wolf.objective:
                delta_wolf = beta_wolf
                beta_wolf = alpha_wolf
                alpha_wolf = self.swarm[i]

            elif self.swarm[i].objective < beta_wolf.objective:
                delta_wolf = beta_wolf
                beta_wolf = self.swarm[i]

            elif self.swarm[i].objective < delta_wolf.objective:
                delta_wolf = self.swarm[i]

        return alpha_wolf, beta_wolf, delta_wolf



    def get_result(self):
        return self.best_solution

    def get_name(self) -> str:
        return 'Shuffled Cellular Evolutionary Grey Wolf Optimizer'
