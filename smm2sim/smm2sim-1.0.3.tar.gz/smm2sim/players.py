from pandas import DataFrame
from itertools import compress
from collections import OrderedDict

class Player(object):
    def __init__(self, name, div=None, pwr=None, seed=None):
        self.name = name
        self.division = div
        self.pwr = pwr
        self.seed = seed

class Players(object):
    def __init__(self, values, indexed=False):
        if type(values) is DataFrame:
            playerdict = values.to_dict('records')
            self.values = [Player(name=x['Player'], div=x['Division'], 
                                  pwr=x['PWR'], seed=x['Seed']) for x in playerdict]
        else:
            self.values = values
        self.indexed = indexed

    def index(self, name=False, div=False, seed=False):
        attrs = ['name','division','seed']
        bools = [name, div, seed]
        indices = list(compress(attrs, bools))
        multi_index = len(indices) != 1
        val_dict = {}
        for player in self.values:
            if multi_index:
                key = tuple([getattr(player, x) for x in indices])
            else:
                key = getattr(player, indices[0])
            if key in val_dict:
                val_dict[key] = val_dict[key] + [player]
            else:
                val_dict[key] = [player]
        self.values = OrderedDict(sorted(val_dict.items(), key=lambda x: x[0]))
        self.indexed = True
        return self

    def copy(self, reset_index=True):
        if not reset_index:
            return Players(self.values, indexed=self.indexed)
        elif self.indexed:
            return Players([x for y in [x for i, x in self.items()] for x in y])
        else:
            return Players(self.values)            

    def len(self):
        return len(self.values)

    def items(self):
        return self.values.items()

    def keys(self):
        if self.indexed:
            return list(self.values)
