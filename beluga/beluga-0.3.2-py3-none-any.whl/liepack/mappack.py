class Any(object):
    def __new__(cls):
        obj = super(Any, cls).__new__(cls)
        return obj


class Morphism(object):
    inputs = 0
    outputs = 0
    domain = ()
    range = ()
    def __new__(cls, *args, **kwargs):
        obj = super(Morphism, cls).__new__(cls)
        obj._args = cls.inputs*[None]
        obj = cls.__call__(obj, *args, **kwargs)
        return obj

    def __call__(self, *args, **kwargs):
        l = 0
        for k in range(self.inputs):
            if self._args[k] is None and l < len(args):
                self._args[k] = args[l]
                l += 1

        # Check inputs and determine if we can actually compute the morphism
        num_args = 0
        for k in range(self.inputs):
            if (isinstance(self._args[k], self.domain[k])) or (self.domain[k] == object):
                num_args += 1

        if num_args == self.inputs:
            return self.map(*self._args)
        else:
            return self

    def __repr__(self):
        return " x ".join([str(_) for _ in self.domain]) + ' -> ' + " x ".join([str(_) for _ in self.range])

    @staticmethod
    def map(*args):
        raise NotImplementedError('Morphism class is a generic superclass that cannot be called.')


class Identity(Morphism):
    inputs = 1
    outputs = 1
    domain = (object,)
    range = (object,)

    @staticmethod
    def map(M):
        return M