from typing import Any, List


class AbstractModel:
    def train(self, x: List[List[Any]], y: List[List[Any]]):
        pass

    def score(self, x: List[List[Any]], y: List[List[Any]]):
        pass

    def predict(self, x: List[List[Any]]):
        pass
