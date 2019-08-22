from PIL.Image import Image

from abc import ABC, abstractclassmethod

from typing import Tuple

class MutationProcessor(ABC):
    @abstractclassmethod
    def mutate(self, image : Image) -> Image:
        pass

class ResizeMutation(MutationProcessor):
    def __init__(self, size : Tuple[int, int]):
        self.__size : Tuple[int, int] = size

    def mutate(self, image : Image) -> Image:
        return image.resize(self.__size).copy()

if __name__ == "__main__":
    s = ResizeMutation((20,20))