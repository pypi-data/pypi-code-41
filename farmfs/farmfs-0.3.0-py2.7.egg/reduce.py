from functools import partial

# Example reducers

def add(x = 0, y = 0):
    return x + y

def mul(x = 1, y = 1):
    return x * y

# In haskell (b -> a -> b) -> b -> t a -> b
# In Python (b | b->a->b) -> t a -> b? -> b
def foldl(f, col, initial=None):
    if initial is None:
        agg = f()
    else:
        agg = initial
    for x in col:
        agg = f(agg, x)
    return agg

assert foldl(add, []) == 0
assert foldl(add, [], 1) == 1
assert foldl(add, [1,2,3]) == 6
assert foldl(add, [1,2,3], 4) == 10

def append(l=list(), x=None):
    assert isinstance(l, list)
    if x is not None:
        l.append(x)
    return l

assert foldl(append, []) == []
assert foldl(append, [], []) == []
assert foldl(append, [1,2,3,4]) == [1,2,3,4]
assert foldl(append, [3,4],[1,2]) == [1,2,3,4]

"""
# (b | b->a->b) -> (c | c->b->c) -> (c | c->a->c)
def transduce(first, second):
    def transduced(c, a):
        out_b = first(first(), a)
        out_c = second(second(), out_b)
        return out_c
"""

def reduceWith(reducer, seed, iterable):
    acc = seed
    for value in iterable:
        acc = reducer(acc, value)
    return acc

def compositionOf(acc, val):
    def composed(*largs):
        val(acc(*largs))

def compose(*fns):
    reduceWith(compositionOf(lambda x: x, fns))

#TODO test compositionOf
# ???
def compose2():
    pass

# (b | b->a->b) -> (b->c) -> ???
def transform(transformation, reducer):
    pass

# transformer
def transduce(transformer, reducer, seed, iterable):
    
