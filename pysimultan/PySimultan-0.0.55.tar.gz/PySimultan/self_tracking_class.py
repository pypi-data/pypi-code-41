import weakref


class SelfTrackingClass(object):
    """Use as base class for classes that can report their instances.

    Subclass.instances: get list of object instances.
    Subclass.max: get/set max number of instances; default is unlimited.
    """

    # set in Subclass to limit number of instances of Subclass
    max = None

    # key: class name as string, value: list of weakrefs to instances
    _classnames = {}

    # technique for "class properties" is adapted from:
    #   http://stackoverflow.com/a/7864317/3531387
    class ClassProperty(property):
        def __get__(self, cls, owner):
            return self.fget.__get__(None, owner)()

    @ClassProperty
    @classmethod
    def instances(cls):
        """Return tuple of instances for this class, or None if none."""
        try:
            return tuple(
              [instance() for instance in cls._classnames[cls.__name__]])
        except KeyError:
            return None

    def __new__(cls, **kwargs):
        """Create instance, if not over limit, and store ref to it."""
        if cls.__name__ not in cls._classnames:
            cls._classnames[cls.__name__] = []
        instance = object.__new__(cls)
        cls._classnames[cls.__name__].append(weakref.ref(instance))
        return instance

    def __del__(self):
        """Remove ref to dead instance from list of instances."""
        for instance in self.__class__._classnames[self.__class__.__name__]:
            if instance() is None:
                self.__class__._classnames[
                  self.__class__.__name__].remove(instance)
        if len(self.__class__._classnames[self.__class__.__name__]) == 0:
            del self.__class__._classnames[self.__class__.__name__]

    @classmethod
    def get_instances(cls):
        if cls.instances is None:
            return list()
        else:
            return list(cls.instances)  # Returns list of all current instances