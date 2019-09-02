"""
    A dict that allows for object-like property access syntax.
"""


class DotDict(dict):
    """ because square brackets are too many characters? """

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)
