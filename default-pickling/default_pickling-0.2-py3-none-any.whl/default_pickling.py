import copy

__all__ = ['KwargsNew', 'DefaultPickling']


class KwargsNew:

    def __init__(self, cls_):
        self.cls_ = cls_

    def __call__(self, cls_, new_kwargs, *new_args):
        """
        Override this method to use a different new.
        """
        retval = cls_.__new__(cls_, *new_args, **new_kwargs)
        retval.__init__(*new_args, **new_kwargs)
        return retval


class DefaultPickling:

    """
    Define default getstate and setstate for use in coöperative inheritance.
    """

    kwargs_new_cls = KwargsNew

    # New methods -------------------------------------------------------------
    def pickled(self):
        return []

    def constructor_args(self):
        return []

    def constructor_kwargs(self):
        return []

    # Magic methods -----------------------------------------------------------
    def __getstate__(self, **kwargs):
        state = {}

        # Create entries for explicitly pickled attributes.
        for attr_name in self.pickled():
            state[attr_name] = getattr(self, attr_name)

        return state

    def __setstate__(self, state):
        try:
            for k, v in state.items():
                setattr(self, k, v)
        except AttributeError:
            raise AttributeError(f"Can't set {k}")

    def __getnewargs_ex__(self):
        args = [getattr(self, attr_name)
                for attr_name in self.constructor_args()]
        kwargs = {attr_name: getattr(self, attr_name)
                  for attr_name in self.constructor_kwargs()}
        return (args, kwargs)

    def __reduce__(self, **kwargs):
        """
        Reimplement __reduce__ so that
        * it supports keyword arguments to new:
          * it calls __getnewargs_ex__ regardless of the Python version, and
          * it will pass the keyword arguments to object.__new__ using
            an overridable kwargs_new static method.
        * it passes keyword arguments to getstate.
        """

        new_args, new_kwargs = self.__getnewargs_ex__()
        state = self.__getstate__(**kwargs)

        return (type(self).kwargs_new_cls(type(self)),
                (type(self), new_kwargs,) + tuple(new_args),
                state)

    def __deepcopy__(self, memo):
        """
        Reimplement __deepcopy__ so that
        * it supports keyword arguments to reduce.
        """
        kwargs = memo.get('deepcopy kwargs', {})
        new, args, state = self.__reduce__(**kwargs)
        args_copy = copy.deepcopy(args, memo)
        if id(self) in memo:
            return memo[id(self)]
        memo[id(self)] = result = new(*args_copy)
        if state:
            state_copy = copy.deepcopy(state, memo)
            result.__setstate__(state_copy)
        return result
