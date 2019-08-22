from PIL.Image import Image

from abc import ABC, abstractclassmethod
from typing import Tuple, Optional

from random import randint

class PastingRule(ABC):
    @abstractclassmethod
    def rule(self) -> Tuple[int, int]:
        pass

class DefaultPastingRule(PastingRule):
    def rule(self) -> Tuple[int, int]:
        return (0, 0)

class LeftCornerPastingRule(PastingRule):
    def __init__(self, left_corner = Tuple[int, int]):
        self.__rule = left_corner
    
    def rule(self) -> Tuple[int, int, int, int]:
        return self.__rule

class RandomPastingRule(PastingRule):
    def __init__(self, limit : Optional[int] = 20):
        self.__limit = limit

    def rule(self) -> Tuple[int, int, int, int]:
        return (randint(0, self.__limit), randint(0,self.__limit))
    
if __name__ == "__main__":
    lrule : PastingRule = LeftCornerPastingRule((10, 10))
    print(lrule.rule())