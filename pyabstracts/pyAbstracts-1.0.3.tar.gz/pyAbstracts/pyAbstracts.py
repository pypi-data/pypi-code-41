## http://stackoverflow.com/questions/3487434/overriding-append-method-after-inheriting-from-a-python-list

import collections

class TypedList(collections.MutableSequence):
    def __init__(self, oktypes, *args):
        # set the types/classes that this object is allowed to contain
        self._oktypes = oktypes
        # define a "private" untyped list to contain the elements of the typed list
        self._list = list()
        # add the $args as elements of the TypedList
        if len(args) > 0:
            self.extend(args[0])

    def __onSetItem__(self, i, v):
        pass

    def __onGetItem__(self, i, v):
        pass

    def __onDelItem__(self, i, v):
        pass

    # 
    def check(self, v):
        if not isinstance(v, self._oktypes):
            raise TypeError(['can only contain variables of type: ',self._oktypes])
        return v

    def __len__(self): 
        return len(self._list)

    # modified this method so that if a slice is called on typed list it will return 
    # an object of the same type instead of an ordinary list
    def __getitem__(self, i): 
        val = self._list[i]
        if isinstance(i, slice):
            cls = type(self)
            cls_instance = cls.__new__(cls)
            cls_instance.__init__(val)
            val = cls_instance

        self.__onGetItem__(i, val)
        return val

    def __delitem__(self, i): 
        self.__onDelItem__(i, self._list[i])
        del self._list[i]

    def __setitem__(self, i, v):
        v = self.check(v)
        self.__onSetItem__(i,v)
        self._list[i] = v

    # method to add a new member to the list (at a specified index), 
    # must first check/convert member for an allowed type
    # will not overwrite the member that already exists at that index, will extend list
    # called by append and extend
    def insert(self, i, v):
        v = self.check(v)
        self.__onSetItem__(i,v)
        self._list.insert(i, v)

    # is meant to return something that is human readable
    # is called when calling "print(obj)"
    def __str__(self):
        return str(self._list)
    
    # is supposed to return a string that when given as an argument to "eval" will return an identical object
    # is called when calling "obj" in the terminal
    def __repr__(self):
        return str(self._list)
        
    def sort(self,reverse=False):
        self._list = sorted(self._list,reverse=reverse)
        
    def __iter__(self):
        return self._list.__iter__()
    

## http://stackoverflow.com/questions/1061283/lt-instead-of-cmp

# self.__gt__ causes problems when other and self are different types:
# other<self
# python does not have a __lt__ function for other which can accept an argument of type self
# so instead python assumes that as the relational operators for self have been overloaded
# they will be better suited to cope with occurance. Python trys to be clever by noticing that:
#
# other<self == ( ~self>other ^ ~self==other ) == ~(self>other V self==other)
# where:
# ~: not
# ^: and
# V: or
#
# however this just causes self.__gt__ to be called again and will cause a recursion loop
#
# SOLUTION
# the only way around this problem is to define all the comparision operators properly
# in every class

# see also reflected operators (magic methods) they exist for numeric operations
# the set of comparision operators make up their own reflected operations
# hence why they should all be defined.

class ComparableMixin:
    # all methods defined in terms of less than "<"
    def __eq__(self, other):
        return not self<other and not other<self
    def __ne__(self, other):
        return self<other or other<self
    def __gt__(self, other):
        return other<self 
    def __ge__(self, other):
        return not self<other
    # inherit from class and override the __le__ (less than) method to get 
    # the functionality of all the other methods
    def __le__(self, other):
        return not other<self

# http://code.activestate.com/recipes/576694/
class OrderedSet(collections.MutableSet):

    def __init__(self, iterable=None):
        self.end = end = [] 
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:        
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)