

class StringBuilder(object):

    def __init__(self, strr=''):
        self.str_list = [s for s in strr]

    def __getitem__(self, item):
        return ''.join(self.str_list[item])

    def __setitem__(self, key, value):
        self.str_list[key] = value

    def __repr__(self):
        return ''.join(self.str_list)

    def __len__(self):
        return len(self.str_list)

    def __iter__(self):
        for s in self.str_list:
            yield s

    def __add__(self, other):
        for s in other:
            self.str_list.append(s)
        return self

    def append(self, other):
        return self.__add__(other)

    def __str__(self):
        return self.__repr__()

    def __delitem__(self, key):
        self.str_list.pop(key)

    def remove(self, key):
        self.__delitem__(key)

    def to_string(self):
        return self.__str__()
