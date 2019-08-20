'''
Test Functions
'''
import numpy as np
from soio.core.solution import Solution
from soio.core.problem import FloatProblem

class F1(FloatProblem):
    def __init__(self):
        self.number_of_variables = 30
        self.lower_bound = self.number_of_variables * [-100.0]
        self.upper_bound = self.number_of_variables * [100.0]
        self.nfes=0

    def get_name(self) -> str:
        return 'F1'

    def evaluate(self, solution: Solution):
        solution.objective = np.sum(np.array(solution.variables) ** 2)
        self.nfes += 1
        return solution