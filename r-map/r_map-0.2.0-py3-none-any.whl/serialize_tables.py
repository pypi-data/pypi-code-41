"""Functions for translating a register map to/from primitive objects which can
then be easily serialized into formats such as JSON"""
from collections import deque
import r_map


def dump(node, objs:dict=None, _already_dumped:dict=None):
    """Return a dictionary representing this object.
    Dump is called recursively to transform each Node object into a
    dictionary. The dictionaries are stored in tables of dictionaries based on
    what kind of object is being represented

    """
    if _already_dumped is None:
        _already_dumped = {}
    if node.uuid in _already_dumped:
        dct = {'_ref' : node.uuid}
        if node._alias:
            dct['_alias'] = node._alias
        return dct
    dct = {n:getattr(node,n) for n in node._nb_attrs}
    dct['type'] = type(node).__name__
    ref = dct['_ref']
    if ref is not None:
        dct['_ref'] = ref.uuid
        #only save overridden values
        keys = node._nb_attrs - set(['_ref', '_alias'])
        for k in keys:
            if k in dct and hasattr(ref, k):
                dct_val = dct[k]
                ref_val = getattr(ref, k)
                if dct_val == ref_val:
                    dct.pop(k)
    elif isinstance(node, r_map.ArrayedNode):
        base_node = dct.pop('base_node')
        if base_node:
            dct['children'] = [dump(base_node, _already_dumped)]
    elif len(node):
        dct['children'] = [dump(c, _already_dumped) for c in node]
    _already_dumped[node.uuid] = node

    #no need to add nulls
    return {k:v for k,v in dct.items() if v is not None}





