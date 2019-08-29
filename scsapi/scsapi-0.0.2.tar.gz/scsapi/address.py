# Created by MysteryBlokHed in 2019.
class Address(object):
    def __init__(self):
        self._dict = {}
    
    def __getitem__(self, key):
        try:
            return self._dict[key]
        except KeyError:
            return