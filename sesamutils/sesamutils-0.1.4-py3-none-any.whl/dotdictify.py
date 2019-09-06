
class Dotdictify(dict):
    """
    Turn dictionary into an object that allows access to nested keys via dot notation
    from http://stackoverflow.com/questions/3797957/python-easily-access-deeply-nested-dict-get-and-set
    """
    def __init__(self, value=None):
        if value is None:
            pass
        elif isinstance(value, dict):
            for key in value:
                self.__setitem__(key, value[key])
        else:
            raise TypeError("Expected type dict.")

    def __setitem__(self, key, value):
        if key is not None and '.' in key:
            my_key, rest_of_key = key.split('.', 1)
            target = self.setdefault(my_key, Dotdictify())
            if not isinstance(target, Dotdictify):
                raise KeyError(f"Cannot set '{rest_of_key}' in '{my_key}' ({repr(target)}).")
            target[rest_of_key] = value
        else:
            if isinstance(value, dict) and not isinstance(value, Dotdictify):
                value = Dotdictify(value)
            dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        if key is None or '.' not in key:
            return dict.__getitem__(self, key)
        my_key, rest_of_key = key.split('.', 1)
        target = dict.__getitem__(self, my_key)
        if not isinstance(target, Dotdictify):
            raise KeyError(f"Cannot get '{rest_of_key}' in '{my_key}' ({repr(target)}).")
        return target[rest_of_key]

    def __contains__(self, key):
        if key is None or '.' not in key:
            return dict.__contains__(self, key)
        my_key, rest_of_key = key.split('.', 1)
        if not dict.__contains__(self, my_key):
            return False
        target = dict.__getitem__(self, my_key)
        if not isinstance(target, Dotdictify):
            return False
        return rest_of_key in target

    def setdefault(self, key, default):
        if key not in self:
            self[key] = default
        return self[key]

    def get(self, k, d=None):
        if Dotdictify.__contains__(self, k):
            return Dotdictify.__getitem__(self, k)
        return d

    __setattr__ = __setitem__
    __getattr__ = __getitem__
