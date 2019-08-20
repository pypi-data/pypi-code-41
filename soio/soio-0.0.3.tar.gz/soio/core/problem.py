from abc import  abstractmethod
from soio.core.solution import Solution
import random

class Problem:
    """ Class representing problems. """

    def __init__(self):
        self.number_of_variables: int = 0
        self.nfes: int = 0

    @abstractmethod
    def create_solution(self) -> Solution:
        """ Creates a random solution to the problem.

        :return: Solution. """
        pass

    @abstractmethod
    def evaluate(self, solution: Solution) -> Solution:
        """ Evaluate a solution. For any new problem inheriting from :class:`Problem`, this method should be
        replaced. Note that this framework ASSUMES minimization, thus solutions must be evaluated in consequence.

        :return: Evaluated solution. """
        self.nfes += 1
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

class PermutationProblem(Problem):
    """ Class representing permutation problems. """

    def __init__(self):
        super(PermutationProblem, self).__init__()

    def create_solution(self) -> Solution:
        pass

class FloatProblem(Problem):

    def __init__(self):
        super(FloatProblem, self).__init__()
        self.lower_bound = []
        self.upper_bound = []

    def create_solution(self) -> Solution:
        new_solution = Solution(self.number_of_variables)
        new_solution.variables = [random.uniform(self.lower_bound[i]*1.0, self.upper_bound[i]*1.0) for i in range(self.number_of_variables)]

        return new_solution