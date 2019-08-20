'''
Whale Optimization Algorithm with cellular topological structure
@author: zzw
@reference: WOA & CGWO

@ log: 2019.7.25, create
'''
from soio.core.algorithm import Algorithm
from soio.core.problem import FloatProblem
from soio.core.solution import Solution
import random
import time
import numpy as np
import math

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


class CellularWhaleOptimizer(Algorithm):
    def __init__(self,
                 problem: FloatProblem,
                 max_nfes: int,
                 grid_shape = [20,20],
                 neighbor_structure = CA_C21,
                 ):

        self.problem = problem
        self.swarm_size = grid_shape[0]*grid_shape[1]
        self.max_iterations = int(max_nfes/(grid_shape[0]*grid_shape[1]))

        self.neighbor_structure = neighbor_structure
        self.grid_catalog = np.random.permutation(self.swarm_size).reshape(grid_shape)

        self.whales_coords = [None]*self.swarm_size
        for i in range(grid_shape[0]):
            for j in range(grid_shape[1]):
                self.whales_coords[self.grid_catalog[i][j]] = [i,j]

        self.best_solution = Solution(self.problem.number_of_variables)
        self.best_solution.objective = float("inf")


    def create_initial_swarm(self) -> np.ndarray:
        """ Creates the initial list of solutions of a metaheuristic. """
        return [self.problem.create_solution() for _ in range(self.swarm_size)]

    def run(self):
        """ Execute the algorithm. """
        start_computing_time = time.time()

        self.swarm = self.create_initial_swarm()
        for i in range(self.swarm_size):
            self.swarm[i] = self.problem.evaluate(self.swarm[i])
            if self.swarm[i].objective < self.best_solution.objective:
                self.best_solution = self.swarm[i]

        self.records = []

        for iter in range(self.max_iterations):
            a = 2 - iter * ((2) / self.max_iterations)  # a decreases linearly fro 2 to 0
            a2 = -1 + iter * ((-1) / self.max_iterations)  # a2 linearly decreases from -1 to -2

            for i in range(self.swarm_size):
                coord = self.whales_coords[i]
                neighbors = find_neighborhood(self.neighbor_structure, self.grid_catalog, coord)
                leader = self.select_best_neigbor(neighbors)

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
                            # rand_leader_index = random.randint(0, self.swarm_size-1)
                            rand_leader_index = random.choice(neighbors)
                            X_rand = self.swarm[rand_leader_index].variables
                            D_X_rand = abs(C * X_rand[j] - self.swarm[i].variables[j])
                            new_whale.variables[j] = X_rand[j] - A * D_X_rand

                        elif abs(A) < 1:
                            D_Leader = abs(C * leader.variables[j] - self.swarm[i].variables[j])
                            new_whale.variables[j] = leader.variables[j] - A * D_Leader

                    elif p >= 0.5:
                        distance2Leader = abs(leader.variables[j] - self.swarm[i].variables[j])
                        new_whale.variables[j] = distance2Leader * math.exp(b * l) * math.cos(l * 2 * math.pi) + leader.variables[j]

                new_whale.variables = np.clip(new_whale.variables, self.problem.lower_bound,
                                                  self.problem.upper_bound).tolist()
                new_whale = self.problem.evaluate(new_whale)
                # greedy
                if new_whale.objective < self.swarm[i].objective:
                    self.swarm[i] = new_whale
                    if new_whale.objective < self.best_solution.objective:
                        self.best_solution = new_whale

            self.records.append(self.best_solution.objective)

        self.total_computing_time = time.time() - start_computing_time

    def select_best_neigbor(self, neighbors):
        leader = Solution(self.problem.number_of_variables)
        leader.objective = float("inf")
        for i in neighbors:
            if self.swarm[i].objective < leader.objective:
                leader = self.swarm[i]

        return leader



    def get_result(self):
        return self.best_solution

    def get_name(self) -> str:
        return 'Cellular Whale Optimization Algorithm'
