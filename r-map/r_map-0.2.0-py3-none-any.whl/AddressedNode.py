from .Node import Node
from operator import attrgetter
class AddressedNode(Node):
    _nb_attrs = frozenset(['local_address'])
    def __init__(self, *, local_address, **kwargs):
        '''Args:
            local_address(int): local address is the address of the node without
            consideration of any offset that a parent node may impose'''
        super().__init__(local_address=local_address, **kwargs)

    def __str__(self):
        return super().__str__() + ' ({:#010x})'.format(self.address)

    @property
    def address(self):
        if self.parent and hasattr(self.parent, 'address'):
            return self.local_address + self.parent.address #allows for relative addressing
        else:
            return self.local_address

    def __iter__(self):
        children = list(Node.__iter__(self))
        if any(not hasattr(c, 'address') for c in children):
            return (s for s in children)
        else:
            return (s for s in sorted(children, key=attrgetter('address')))

