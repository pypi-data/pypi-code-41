from collections.abc import MutableMapping


class HashableDict(MutableMapping):
    """Hashable dict.

    This mapping object behaves like the built-in :class:`dict`, but supports hashing.
    """

    def __init__(self, *args, **kwargs):
        self._storage = dict(*args, **kwargs)

    def __delitem__(self, key):
        del self._storage[key]

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __getitem__(self, key):
        return self._storage[key]

    def __hash__(self):
        return hash(self.__key())

    def __iter__(self):
        return iter(self._storage)

    def __key(self):
        return tuple((k, self._storage[k]) for k in sorted(self._storage))

    def __len__(self):
        return len(self._storage)

    def __setitem__(self, key, value):
        self._storage[key] = value
