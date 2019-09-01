from farmfs.util import compose, identity

class _lens:
  def __init__(self, foo):
    self.__call__ = foo

  def _compose(self, foo):
    return _lens(compose(foo, self.__call__))

  def get(self, attrib):
    def getter(store):
      return store.get(attrib)
    return self._compose(getter)

  def set(self, value):
    def setter(store):
      s2 = dict(store)
      s2[attrib] = value
      return s2
    return self._compose(setter)

  def mod(self, attrib):
    def transform(f):
      def applicator(store):
        s1 = get(attrib)(store)
        s2 = f(s1)
        return set(attrib)(s2)(store)
      return applicator
    return self._compose(transform)

def get(attrib):
  return _lens(identity).get(attrib)

def set(attrib):
  return _lens(identity).set(attrib)

def mod(attrib):
  return _lens(identity).mod(attrib)
