# Copyright 2018, 2019 Felix Krull
# Licensed under the MIT license, see LICENSE for details.


def equals(cls):
    def eq(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__
    cls.__eq__ = eq
    return cls


def repr(cls):
    def repr(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            ', '.join('%s=%r' % (k, v) for (k, v) in self.__dict__.items()),
        )
    cls.__repr__ = repr
    return cls
