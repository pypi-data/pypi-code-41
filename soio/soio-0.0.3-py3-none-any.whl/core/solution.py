class Solution:
    """ Class representing solutions """

    def __init__(self, number_of_variables: int):
        self.number_of_variables = number_of_variables
        self.objective = None
        self.variables = [[] for _ in range(self.number_of_variables)]

    def __eq__(self, solution) -> bool:
        if isinstance(solution, self.__class__):
            return self.variables == solution.variables
        return False

    def __str__(self) -> str:
        return 'Solution(objective={},variables={})'.format(self.objective, self.variables)

    def __copy__(self):
        new_solution = Solution(self.number_of_variables)
        new_solution.objective = self.objective
        new_solution.variables = self.variables[:]
        return new_solution