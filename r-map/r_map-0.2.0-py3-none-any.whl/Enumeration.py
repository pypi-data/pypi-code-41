from .Node import Node
from .ValueNodeMixins import UnsignedValueNodeMixin
from operator import __eq__, __lt__, __le__, __gt__, __ge__
from functools import wraps
import r_map

def comp_func(op):
    @wraps(op)
    def op_func(self, other):
        if isinstance(other, (Enumeration,  r_map.BitField)):
            return op(self.value, other.value)
        elif isinstance(other, int):
            return op(self.value, other)
        else:
            return NotImplemented
    return op_func

def comparisons(cls):
    for op in __eq__, __lt__, __le__, __gt__, __ge__:
        f = comp_func(op)
        setattr(cls, '__{}__'.format(op.__name__), f)
    return cls


@comparisons
class Enumeration(UnsignedValueNodeMixin, Node):
    "r_map Enumeration type"
    _nb_attrs = frozenset(['value',])

    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        self._value = value

    def __str__(self):
        return super().__str__() + ' value: {}'.format(self.value)

