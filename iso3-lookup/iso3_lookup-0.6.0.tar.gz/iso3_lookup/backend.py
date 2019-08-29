import requests
from fuzzywuzzy import fuzz
import pickle
import os

PATH = os.path.join(os.path.split(__file__)[0], 'data', 'stored.pickle')


class Lookup:
    def __new__(cls):
        internet = cls.internet_on()
        setup = object.__new__(cls)

        if internet:
            setup.data = cls.get_recent_data()
        else:
            setup.data = cls.get_stored_data()

        return setup

    @staticmethod
    def get_recent_data(
        url="https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/slim-3/slim-3.json"
    ):
        data = requests.get(url).json()
        with open(PATH, 'wb') as f:
            pickle.dump(data, f)
        return data

    @staticmethod
    def get_stored_data():
        with open(PATH, 'rb') as f:
            data = pickle.loads(f)
        return data

    @staticmethod
    def internet_on():
        try:
            requests.get('http://216.58.192.142', timeout=1)
            return True
        except Exception:
            return False

    @staticmethod
    def conf_exists(l, var, value):
        if len(l) > 0:
            return l[0][var]
        raise ValueError(value + " does not exist in lookup data.")

    @staticmethod
    def get_fuzz(v, country, var):
        v["ratio"] = fuzz.partial_ratio(v[var].lower(), country.lower())
        return v

    @staticmethod
    def get_max(data):
        return max([v["ratio"] for v in data])

    @staticmethod
    def filter_data(data, cutoff=50):
        return [v for v in data if v["ratio"] > cutoff]

    def max_data(self, data):
        return self.get_max(data), self.filter_data(data)
