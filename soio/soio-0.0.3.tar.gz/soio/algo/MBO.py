'''
Migrating Birds Optimization (MBO)
@author: zzw
@reference:
@log: 2019.6.8, create
'''
from soio.core.algorithm import Algorithm
from soio.core.problem import PermutationProblem
from soio.core.operator import Operator
import time


class MigratingBirdsOptimizer(Algorithm):
    def __init__(self,
                 problem: PermutationProblem,
                 neighbor_generator: Operator,
                 max_nfes: int,
                 swarm_size: int,
                 neighbors_size: int,
                 shared_neigbors: int,
                 num_tours: int):
        '''
        :param problem:
        :param neighbor_generator:
        :param max_nfes:
        :param swarm_size:  the number of individuals in the swarm (α), odd
        :param neighbors_size:  the number of neigbors to be considered (β), β >= (2χ+1)
        :param shared_neigbors: he number of neighbors to be shared with the following company (χ)
        :param num_tours: the number of tours (w)

        Step1. Initialization:
        At first,  α solutions are generated randomly, in which one solution is selected as the leader
        and others are divided equally to form the left line and the right line of the V-shape respectively.

        Step2. Leader improvement:
        β solutions are generated around the leader.
        If the best neighbor brings an improvement, then the leader is replaced; otherwise, the leader keeps unchanged.
        Then, the unused neighbors are sorted in ascending order according to their objective values
        and the best 2 χ are selected and divided equally to form the left and the right sharing neighbor set respectively

        Step3. Follower improvement:
        The improvement process is conducted along the lines toward the tails.
        For a solution (such as X) in the left (right) line, β − χ neighbors are created randomly.
        Then these β − χ solutions and χ solutions in the left (right) sharing neighbor set are seen as neighborhood of X and evaluated together.
        If the best neighbor has a better fitness than X, then X is replaced.
        Subsequently, the best χ unused neighbors are utilized to rebuild the left (right) sharing neighbor set.
        The procedure above is repeated until all solutions in the left and right list have been considered.
        '''

        self.problem = problem
        self.neighbor_generator = neighbor_generator
        self.max_nfes = max_nfes
        self.swarm_size = swarm_size
        self.max_nfes = max_nfes
        self.neighbors_size = neighbors_size
        self.shared_neigbors = shared_neigbors
        self.num_tours = num_tours

        self.best_solution = None

        self.leader = None
        self.left_followers = None
        self.right_followers = None
        self.num_followers= int((self.swarm_size - 1) / 2)


    def run(self):
        start_computing_time = time.time()

        self.leader = self.problem.evaluate(self.problem.create_solution())
        self.left_followers = [self.problem.evaluate(self.problem.create_solution()) for _ in range(self.num_followers)]
        self.right_followers = [self.problem.evaluate(self.problem.create_solution()) for _ in range(self.num_followers)]

        terminate = False
        LR = False
        while True:
            if terminate:
                break
            for tour in range(self.num_tours):
                right_shared_list = None
                left_shared_list = None

                if self.max_nfes < self.problem.nfes:
                    terminate = True
                    break

                # improve the leader
                leader_neigbors = [self.problem.evaluate(self.neighbor_generator.execute(self.leader)) for _ in range(self.neighbors_size)]
                leader_neigbors.sort(key=lambda x: x.objective)
                if leader_neigbors[0].objective< self.leader.objective:
                    self.leader = leader_neigbors[0]
                    if LR:
                        right_shared_list = leader_neigbors[1:self.shared_neigbors+1]
                        left_shared_list = leader_neigbors[self.shared_neigbors+1: 2*self.shared_neigbors+1]
                    else:
                        left_shared_list = leader_neigbors[1:self.shared_neigbors + 1]
                        right_shared_list = leader_neigbors[self.shared_neigbors + 1: 2 * self.shared_neigbors + 1]
                else:
                    if LR:
                        right_shared_list = leader_neigbors[0:self.shared_neigbors]
                        left_shared_list = leader_neigbors[self.shared_neigbors: 2*self.shared_neigbors]
                    else:
                        left_shared_list = leader_neigbors[0:self.shared_neigbors]
                        right_shared_list = leader_neigbors[self.shared_neigbors: 2 * self.shared_neigbors]

                #improve the followers
                for idx in range(self.num_followers):
                    if self.max_nfes < self.problem.nfes:
                        terminate = True
                        break

                    left_neigbors = [self.problem.evaluate(self.neighbor_generator.execute(self.left_followers[idx]))
                                     for _ in range(self.neighbors_size-self.shared_neigbors)] \
                                    + left_shared_list
                    left_neigbors.sort(key=lambda x: x.objective)
                    if left_neigbors[0].objective < self.left_followers[idx].objective:
                        self.left_followers[idx] = left_neigbors[0]
                        left_shared_list = left_neigbors[1:self.shared_neigbors+1]
                    else:
                        left_shared_list = left_neigbors[0:self.shared_neigbors]

                    if self.max_nfes < self.problem.nfes:
                        terminate = True
                        break

                    right_neigbors = [self.problem.evaluate(self.neighbor_generator.execute(self.right_followers[idx]))
                                     for _ in range(self.neighbors_size - self.shared_neigbors)] \
                                    + right_shared_list
                    right_neigbors.sort(key=lambda x: x.objective)
                    if right_neigbors[0].objective < self.right_followers[idx].objective:
                        self.right_followers[idx] = right_neigbors[0]
                        right_shared_list = right_neigbors[1:self.shared_neigbors + 1]
                    else:
                        right_shared_list = right_neigbors[0:self.shared_neigbors]

            # Select a new leader
            if LR:
                self.right_followers.append(self.leader)
                self.leader = self.right_followers[0]
                self.right_follower= self.right_followers[1:]
            else:
                self.left_followers.append(self.leader)
                self.leader = self.left_followers[0]
                self.left_follower = self.left_followers[1:]

            LR = not LR

        self.best_solution = self.leader
        for solution in self.left_followers:
            if solution.objective < self.best_solution.objective:
                self.best_solution = solution
        for solution in self.right_followers:
            if solution.objective < self.best_solution.objective:
                self.best_solution = solution
        self.total_computing_time = time.time() - start_computing_time

    def get_result(self):
        return self.best_solution

    def get_name(self) -> str:
        return 'Migrating Birds Optimizer '






