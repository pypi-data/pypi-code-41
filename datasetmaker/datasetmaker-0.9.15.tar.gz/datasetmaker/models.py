from abc import ABC, abstractmethod


class Client(ABC):
    @abstractmethod
    def get(self, indicators, periods):
        pass

    @abstractmethod
    def save(self, path):
        pass


class DataBundle:
    def __init__(self):
        pass
