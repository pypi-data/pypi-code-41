from abc import  abstractmethod
from soio.core.solution import Solution
import random

class Algorithm:
    """ Class representing metaheuristic algorithms. """

    def __init__(self):
        self.number_of_variables: int = 0
        self.nfes: int = 0

    @abstractmethod
    def run(self):
        """ Execute the algorithm. """
        pass

    @abstractmethod
    def get_result(self) -> Solution:
        """ :return: Optimal solution. """
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass
