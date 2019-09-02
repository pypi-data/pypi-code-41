"""Module to take an existing r_map and replace all instances of ArrayedNode
with its children. Also fix addresses of AddressedNodes to safe the tree lookup
penalty imposed within their address properties. This involves manipulating the
tree in memory and providing and overridden AddressedNode which can be used when
deserializing the tree. The idea is to create a simplified tree with only a root
node with registermaps as childdren
"""
from .AddressedNode import AddressedNode
from .RegisterMap import RegisterMap
from .Register import Register
from .ArrayedNode import ArrayedNode

class FixedAddressedNode(AddressedNode):
    @property
    def address(self):
        return self.local_address

class FixedRegisterMap(FixedAddressedNode, RegisterMap):
    pass

class FixedRegister(FixedAddressedNode, Register):
    pass

def convert_to_fixed_node(item, recurse=True):
    """Warning this is a hacky solution but as we're merely overriding the
    address descriptor, this should work fine
    """

    if isinstance(item, RegisterMap): #order important here
        item.__class__ = FixedRegisterMap
    elif isinstance(item, Register):
        item.__class__ = FixedRegister
    elif isinstance(item, AddressedNode):
        item.__class__ = FixedAddressedNode
    else: #must be done
        return

    if hasattr(item, 'parent') and isinstance(item.parent, AddressedNode):
        item.local_address += item.parent.local_address

    if recurse:
        for child in item:
            convert_to_fixed_node(child, recurse=True)

def elaborate_nodes(item, recurse=True):
    for c in list(item):
        if isinstance(c, ArrayedNode):
            c.parent = None
            for instance in list(c):
                #we want standalone copies
                instance._ref = None
                item._add(instance)
                if recurse:
                    elaborate_nodes(instance, recurse=True)
        elif recurse:
            elaborate_nodes(c, recurse=True)



