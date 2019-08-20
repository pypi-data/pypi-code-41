'''
Grey wolf optimizer with cellular topological structure
@author: zzw
@reference: Lu, Chao, Liang Gao, and Jin Yi. 2018.
                    Grey wolf optimizer with cellular topological structure.
                    Expert Systems with Applications 107:89-114.
                    doi: https://doi.org/10.1016/j.eswa.2018.04.012.

@log: 2019.5.12, create
'''
from soio.core.algorithm import Algorithm
from soio.core.problem import FloatProblem
from soio.core.solution import Solution
import time
import numpy as np

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
                 problem: FloatProblem,
                 max_nfes: int,
                 grid_shape = [20,20],
                 neighbor_structure = CA_C21,
                 ):

        self.problem = problem
        self.swarm_size = grid_shape[0]*grid_shape[1]
        self.max_nfes = max_nfes

        self.max_iterations = int(self.max_nfes/(grid_shape[0]*grid_shape[1]))

        self.neighbor_structure = neighbor_structure
        self.grid_catalog = np.random.permutation(self.swarm_size).reshape(grid_shape)

        self.wolves_coords = [None]*self.swarm_size
        for i in range(grid_shape[0]):
            for j in range(grid_shape[1]):
                self.wolves_coords[self.grid_catalog[i][j]] = [i,j]

        self.best_solution = Solution(self.problem.number_of_variables)
        self.best_solution.objective = float("inf")


    def create_initial_swarm(self) :
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

            for i in range(self.swarm_size):
                coord = self.wolves_coords[i]
                neighbors = find_neighborhood(self.neighbor_structure, self.grid_catalog, coord)
                alpha_wolf, beta_wolf, delta_wolf  = self.select_best_three_neigbors(neighbors)

                r1 = np.random.random((3, self.problem.number_of_variables))
                r2 = np.random.random((3, self.problem.number_of_variables))

                A1 = 2 * a * r1[0] - a
                C1 = 2 * r2[0]
                D_alpha = np.abs(C1 * alpha_wolf.variables - self.swarm[i].variables)
                X1 = alpha_wolf.variables - A1 * D_alpha

                A2 = 2 * a * r1[1] - a
                C2 = 2 * r2[1]
                D_beta = np.abs(C2 * beta_wolf.variables - self.swarm[i].variables)
                X2 = beta_wolf.variables - A2 * D_beta

                A3 = 2 * a * r1[2] - a
                C3 = 2 * r2[2]
                D_delta = np.abs(C3 * delta_wolf.variables - self.swarm[i].variables)
                X3 = delta_wolf.variables - A3 * D_delta

                new_pos = (X1 + X2 + X3) / 3
                new_pos= np.clip(new_pos, self.problem.lower_bound, self.problem.upper_bound)
                new_wolf = Solution(self.problem.number_of_variables)
                new_wolf.variables = new_pos
                new_wolf = self.problem.evaluate(new_wolf)

                # greedy
                if new_wolf.objective < self.swarm[i].objective:
                    self.swarm[i] = new_wolf
                    if new_wolf.objective < self.best_solution.objective:
                        self.best_solution = new_wolf

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
        return 'Cellular Grey Wolf Optimizer'
