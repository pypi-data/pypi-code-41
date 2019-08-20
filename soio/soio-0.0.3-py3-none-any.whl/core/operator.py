from abc import  abstractmethod
from soio.core.solution import Solution

class Operator:
    """ Class representing operator """

    @abstractmethod
    def execute(self, Solution) ->Solution:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass