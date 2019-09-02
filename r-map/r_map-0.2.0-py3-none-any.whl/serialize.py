"""Functions for translating a register map to/from primitive objects which can
then be easily serialized into formats such as JSON"""
from collections import deque
import r_map


def load(dct, parent=None, already_loaded=None, todo=None):
    """Create an r_map from a dictionary of primitive objects"""
    if already_loaded is None:
        already_loaded = {}
    if todo is None:
        todo = deque()

    obj = _load(dct, parent=parent, already_loaded=already_loaded, todo=todo)
    #now finish loading by taking another pass
    while True:
        before_length = len(todo)
        if before_length == 0:
            break
        dct, parent = todo.popleft()
        _load(dct, parent=parent, already_loaded=already_loaded, todo=todo)
        after_length = len(todo)
        if after_length != before_length - 1:
            raise RuntimeError(f"Could not deserialize dictionary: {dct}"
                               f" with parent: {parent}")
    return obj

def _load(dct, parent, already_loaded, todo):
    obj = None
    if isinstance(dct, dict):
        #decode dict logic here
        type_name = dct.get('type')
        T = getattr(r_map, type_name) if type_name else None
        ref_uuid = dct.get('_ref')
        uuid = dct.get('uuid')
        if ref_uuid:
            ref_obj = already_loaded.get(ref_uuid)
            if not ref_obj and 'children' in dct:
                children = dct.get('children')
                ref_obj = _load(children[0],
                                parent=None,
                                already_loaded=already_loaded,
                                todo=todo)
            if ref_obj:
                vals = {k:v for k,v in dct.items() if k in ref_obj._nb_attrs
                                                   and v is not None}
                obj = ref_obj._copy(parent=parent,
                                    alias=vals.pop('_alias', False),
                                    **vals)
            else:
                todo.append((dct, parent))
                return
        elif uuid in already_loaded:
            obj = already_loaded[uuid]
        elif T:
            vals = {k:v for k,v in dct.items() if k in T._nb_attrs
                                               and v is not None}
            obj = T(parent=parent, **vals)
            children = dct.get('children')
            if children:
                if isinstance(obj, r_map.ArrayedNode):
                    if len(children) > 1:
                        raise RuntimeError("An ArrayedNode shouldn't have more "
                                           "than 1 child.")
                    #Children of ArrayedNode are dynamically generated only.
                    #Marking base_node as child during serialization to leverage
                    #existing infrastucture
                    child = _load(children[0],
                                  parent=None,
                                  already_loaded=already_loaded,
                                  todo=todo)
                    obj.base_node = child
                else:
                    for child_dct in children:
                        _load(child_dct,
                              parent=obj,
                              already_loaded=already_loaded,
                              todo=todo)
        else:
            raise ValueError(f"Could not load data: {dct}")
        already_loaded[obj.uuid] = obj
    else:
        raise ValueError(f"Expected dictionary type argument. Got {type(dct)}")
    return obj

def dump(node, _already_dumped:dict=None):
    """Return a dictionary representing this object
    dump is called recursively to transform each Node object into a
    dictionary
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
    if isinstance(node, r_map.ArrayedNode):
        dct['name'] = node._full_name
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
        #this ensures that when a node in the tree is serialized all of its
        #dependencies are serialized as well
        if ref.uuid not in _already_dumped:
            dct['children'] = [dump(ref, _already_dumped)]
    elif isinstance(node, r_map.ArrayedNode):
        base_node = dct.pop('base_node')
        if base_node:
            dct['children'] = [dump(base_node, _already_dumped)]
    elif len(node):
        dct['children'] = [dump(c, _already_dumped) for c in node]
    _already_dumped[node.uuid] = node

    #no need to add nulls
    return {k:v for k,v in dct.items() if v is not None}





