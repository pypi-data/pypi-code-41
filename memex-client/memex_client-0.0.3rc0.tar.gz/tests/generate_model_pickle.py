from memex_client.abstract_model import AbstractModel
from memex_client.scientist import package
from requests import get


class Temp:
    def __init__(self):
        self.wow_number = 7

    def set_wow_number(self, new_numb):
        self.wow_number = new_numb

    def get_wow_number(self):
        return self.wow_number


class DecisionTreeTrained(AbstractModel):
    def __init__(self):
        self.specialNumber = 0
        self.temp = Temp()

    def train(self, data=None):
        get("https://www.google.com")
        if data is not None:
            self.specialNumber += 1
        self.temp.set_wow_number(self.specialNumber)

    def predict(self, data=None):
        return [self.specialNumber]

    def score(self, data=None):
        return [1]


if __name__ == "__main__":
    d = DecisionTreeTrained()
    for i in range(10):
        d.train(1)
    print(package(d, write_to_file=False))
