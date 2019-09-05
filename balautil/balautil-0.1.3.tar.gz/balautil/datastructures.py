class bidict():
    """
    Example Usage: bitdict(  <some dict> )
    test = bidict({"a": "apple", "b": "bananna"})
    test
    Normal: {'a': 'apple', 'b': 'bananna'}
    Reverse: {'apple': 'a', 'bananna': 'b'}
    test["a"]
    'apple'
    test["apple"]
    'a'
    test["c"] = "cat"
    test
    Normal: {'a': 'apple', 'b': 'bananna', 'c': 'cat'}
    Reverse: {'apple': 'a', 'bananna': 'b', 'cat': 'c'}
    test.inverse["apple"]
    'a'
    test.update({"d": "dog"}, e="elephant")
    {'a': 'apple', 'b': 'bananna', 'c': 'cat', 'e': 'elephant', 'd': 'dog'}
    {'apple': 'a', 'bananna': 'b', 'cat': 'c', 'elephant': 'e', 'dog': 'd'}{'a': 'apple', 'b': 'bananna', 'c': 'cat', 'e': 'elephant', 'd': 'dog'}
    {'apple': 'a', 'bananna': 'b', 'cat': 'c', 'elephant': 'e', 'dog': 'd'}
    test.get('apple', reverse=True)
    'a'
    test.get('a')
    'apple'
    """
    
    def __init__(self, dict_to_start={}):
        self.k_to_v = dict(dict_to_start)
        self.v_to_k = self._reverse(dict_to_start)
    
    def __getitem__(self, k ):
        if k in self.k_to_v: return self.k_to_v[k]
        else:
            if k in self.v_to_k: return self.v_to_k[k]
            else: raise KeyError(f"Key {k} :  Not found in both direction")
            
    def __setitem__(self, k,v):
        self.k_to_v[k] = v
        self.v_to_k[v] = k
    
    def _reverse(self, o_dict):
        return {v:k for k,v in o_dict.items()}
    
    @property
    def inverse(self): return self.v_to_k
    
    def update(self, new_dct, **kwargs):
        kwargs.update(new_dct)
        self.k_to_v.update(kwargs)
        self.v_to_k.update(self._reverse(kwargs))
    
    def clear(self):
        self.k_to_v.clear()
        self.v_to_k.clear()
    
    def copy(self, reverse=False):
        if reverse: return self.v_to_k.copy()
        else: return self.k_to_v.copy()
        
    def get(self, k, default=None, reverse=False):
        if reverse:  return self.v_to_k.get(k, default)
        else:        return self.k_to_v.get(k,default)
    
    def __repr__(self):
        return "Normal: " + self.k_to_v.__repr__() + "\nReverse: " + self.v_to_k.__repr__()