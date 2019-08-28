from abc import ABC, abstractmethod


class Base(ABC):
 
    @abstractmethod
    def __init__(self, value):
        pass
    
    @abstractmethod
    def fit_predict(self, data):
        pass
