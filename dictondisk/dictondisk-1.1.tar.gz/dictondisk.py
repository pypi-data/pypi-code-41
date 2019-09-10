from copy import copy
import tempfile
import pickle
import os

__title__ = "dictondisk"
__description__ = "Implementation of a dictionary in a temporary directory"
__version__ = "1.1"

__url__ = "https://github.com/MKuranowski/dictondisk"
__author__ = "Mikołaj Kuranowski"
__email__ = "mkuranowski@gmail.com"

__copyright__ = "© Copyright 2019 Mikołaj Kuranowski"
__license__ = "MIT"

class DictOnDiskView:
    """A very basic implementation of the dict-view stuff"""

    def __init__(self, parent, intrest):
        assert intrest in {"keys", "values", "items"}

        self.parent = parent
        self.intrest = intrest

    def __repr__(self):
        return "<DictOnDiskView object of {!r} of {!r}>".format(self.intrest, self.parent.folder.name)

    def __len__(self):
        """
        An exact amount of items inside the parent DictOnDisk.
        Will count duplicate values, if they are under different keys.

        If you do not need the exact number, use the parents DictOnDisk.approx_len() method.
        """
        return len(self.parent)

    def __contains__(self, i):
        """
        Check if a given item is inside the DictOnDiskView.
        """
        # Keys & Items view check if the key is in the parent by parent.__contains__,
        # But for values the view has to implement its own check
        if self.intrest == "keys":
            return (i in self.parent)

        elif self.intrest == "items":
            return (i[0] in self.parent)

        elif self.intrest == "values":
            # iterate over each .pkl file
            for file in os.scandir(self.parent.folder.name):

                # ignore non-files
                if not file.is_file():
                    continue

                # ignore non-pickled files
                if not file.name.endswith(".pkl"):
                    continue

                # read the obj
                with open(file.path, "rb") as f:
                    obj = pickle.load(f)

                # check if the value is in the obj
                for other_i in obj.values():

                    if other_i == i:
                        return True

            return False

    def __iter__(self):
        """
        Iterates over requested stuff from the parent DictOnDisk
        """
        # iterate over each .pkl file
        for file in os.scandir(self.parent.folder.name):

            # ignore non-files
            if not file.is_file():
                continue

            # ignore non-pickled files
            if not file.name.endswith(".pkl"):
                continue

            # read the obj
            with open(file.path, "rb") as f:
                obj = pickle.load(f)

            # check if the value is in the obj
            for item_k, item_v in obj.items():

                if self.intrest == "keys":
                    yield item_k

                elif self.intrest == "values":
                    yield item_v

                elif self.intrest == "items":
                    yield (item_k, item_v)

class DictOnDisk:
    """An implementation of dict that stores stuff inside a temporary directory"""

    def __init__(self, data={}, **kwargs):
        """
        Create a dictionary held in a TemporaryDirectory.

        Params are the same as for the DictOnDisk.update method:
        First one can be a dict or any iterable of (key, value) pairs to insert into the _FileDict;
        Others have to be keyword arguments, that will also get inserted into the created _FileDict.
        """
        self.folder = tempfile.TemporaryDirectory()
        self.update(data, **kwargs)

    def __repr__(self):
        return "<DictOnDisk object at {!r}>".format(self.folder.name)

    def __del__(self):
        """Cleaunp the temporary folder on object removal"""
        try:
            self.folder.cleanup()
        except AttributeError:
            pass

    def _path(self, fname):
        """A shorthand function to join any filename to the tempfolder name"""
        return os.path.join(self.folder.name, fname)

    def __len__(self):
        """
        An exact amount of items inside this dictionary.
        Requires opening every pickled file to check how many items are inside each file.
        If you don't need the exact amount, use DictOnDisk.approx_len()
        """
        count = 0

        # iterate over each .pkl file
        for file in os.scandir(self.folder.name):

            # ignore non-files
            if not file.is_file():
                continue

            # ignore non-pickled files
            if not file.name.endswith(".pkl"):
                continue

            # read the obj
            with open(file.path, "rb") as f:
                obj = pickle.load(f)

            # bump the total count
            count += len(obj)

            # remove the obj
            del obj

        return count

    def __getitem__(self, k):
        """
        Fetch an item from the dictionary:
        Creates a hash for the key, finds the corresponding file,
        Unpickles it and searches for the exact key.
        """
        # Create a hash of the key
        khash = hash(k)
        fname = str(khash) + ".pkl"

        # raise KeyError if the file does not exist
        if not os.path.exists(self._path(fname)):
            raise KeyError(k)

        # read the items from the file
        # the pickled file contains a mapping of exact keys to values
        # this is to prevent hash collisions — one file can contain may keys
        with open(self._path(fname), "rb") as f:
            obj = pickle.load(f)

        if k in obj:
            return obj[k]

        else:
            raise KeyError(k)

    def __setitem__ (self, k, v):
        """
        Sets a value to a key.
        Creates a hash for the key, finds the corresponding file (creating it if it does not exist)
        And then pickles the key, value pair to the file.
        """
        # Create a hash of the key
        khash = hash(k)
        fname = str(khash) + ".pkl"

        # The file exists - load the pickled list in the file
        if os.path.exists(self._path(fname)):

            # read stuff from the pickled file
            with open(self._path(fname), "rb") as f:
                obj = pickle.load(f)

            # obj is a dict with exact keys for preventing hash collision
            obj[k] = v

            # and finally pickle the file
            with open(self._path(fname), "wb") as f:
                pickle.dump(obj, f)


        # The file does not exist - create it
        else:

            with open(self._path(fname), "wb") as f:
                pickle.dump({k: v}, f)

    def __delitem__(self, k):
        """
        Removes an item corresponding to the given key.
        Creates a hash for the key, finds the corresponding file (creating it if it does not exist),
        Unpickles the file, removes item corresponding to the given key,
        """
        # Create a hash of the key
        khash = hash(k)
        fname = str(khash) + ".pkl"

        # raise KeyError if the file does not exist
        if not os.path.exists(self._path(fname)):
            raise KeyError(k)

        # read the items from the file
        # the pickled file contains a mapping of exact keys to values
        # this is to prevent hash collisions — one file can contain may keys
        with open(self._path(fname), "rb") as f:
            obj = pickle.load(f)

        # raise KeyError if k is not in the unpickled obj
        if k not in obj:
            raise KeyError(k)

        # delete the thing
        del obj[k]

        # if obj still has other items, pickle it
        if len(obj) > 0:
            with open(self._path(fname), "wb") as f:
                pickle.dump(obj, f)

        # otherwise remove the file
        else:
            os.remove(self._path(fname))

    def __contains__(self, k):
        """
        Checks if given key is inside the DictOnDisk
        Creates a hash for the key, finds the corresponding file (immediately returning False if it does not exist),
        Unpickles the file, and checks if the exact key is inside the file.
        """
        # Create a hash of the key
        khash = hash(k)
        fname = str(khash) + ".pkl"

        # no file - no key in dict
        if not os.path.exists(self._path(fname)):
            return False

        # read the items from the file
        # the pickled file contains a mapping of exact keys to values
        # this is to prevent hash collisions — one file can contain may keys
        with open(self._path(fname), "rb") as f:
            obj = pickle.load(f)

        if k in obj:
            return True

        else:
            raise False

    def __iter__(self):
        """
        Iterate over every key inside dict, in an unspecified order.
        If you'll need to also fetch values for the corresponding values, always use FileDict.items()!
        """
        # iterate over each .pkl file
        for file in os.scandir(self.folder.name):

            # ignore non-files
            if not file.is_file():
                continue

            # ignore non-pickled files
            if not file.name.endswith(".pkl"):
                continue

            # read the obj
            with open(file.path, "rb") as f:
                obj = pickle.load(f)

            yield from obj

    def get(self, k, fallback=None):
        """
        Get a value corresponding for the given key from the dictionary,
        and if it does not exist returns `fallback` (defaults to None)
        """
        try:
            return self[k]

        except KeyError:
            return fallback

    def keys(self):
        """
        Returns a DictOnDiskView for keys of this DictOnDisk.

        Only 3 things can be done with a DictOnDiskView:
        1. Length of given DictOnDiskView (`len` method)
        2. Iterating over DictOnDiskView (`for _ in` operator or `iter` method)
        3. Checking if a thing is inside the DictOnDiskView (`in` operator)

        DictOnDiskView follows any changes made to the parent DictOnDisk.
        """
        return DictOnDiskView(self, "keys")

    def values(self):
        """
        Returns a DictOnDiskView for values of this DictOnDisk.

        Only 3 things can be done with a DictOnDiskView:
        1. Length of given DictOnDiskView (`len` method)
        2. Iterating over DictOnDiskView (`for _ in` operator or `iter` method)
        3. Checking if a thing is inside the DictOnDiskView (`in` operator)

        DictOnDiskView follows any changes made to the parent DictOnDisk.
        """

        return DictOnDiskView(self, "values")

    def items(self):
        """
        Returns a DictOnDiskView for items (key, value pairs) of this DictOnDisk.

        Only 3 things can be done with a DictOnDiskView:
        1. Length of given DictOnDiskView (`len` method)
        2. Iterating over DictOnDiskView (`for _ in` operator or `iter` method)
        3. Checking if a thing is inside the DictOnDiskView (`in` operator)

        DictOnDiskView follows any changes made to the parent DictOnDisk.
        """

        return DictOnDiskView(self, "items")

    def update(self, other, **kwargs):
        """
        Add items from other containers to the given DictOnDisk.
        If a key is already in the DictOnDisk, it will be overwriten.

        The first argument can be a dict-like thing (has to have the .items() method),
        Or any other iterable container of (key, value) pairs.

        Also supports updating from keyword arguments, which can overwrite items from the first argument.
        """

        # If other has an items() method, we assume it behaves like a dict:
        # So that it returns key, value pairs
        if hasattr(other, "items"):
            for k, v in other.items():
                self[k] = v

        # Otherwise, simply iterate over 'other' and assume every item in there
        # Represents a key, value pair
        else:
            for i in other:
                if len(i) != 2:
                    raise ValueError("{!r} does not represent a key, value pair".format(i))
                self[i[0]] = i[1]

        # At the end, add items from the keyword arguments
        for k, v in kwargs.items():
            self[k] = v

    def approx_len(self):
        """An approximation for the length: amount of files inside the temporary directory"""
        return len(os.listdir(self.folder.name))

    def copy(self):
        """Creates a shallow copy of this dictondisk"""

        new = self.__class__()

        for k, v in self.items():
            new[copy(k)] = copy(v)

        return new

    @classmethod
    def fromkeys(cls, iterable, value=None):
        new = cls()

        for i in iterable:
            new[i] = value

        return new

    def pop(self, key, *defaults):
        """
        Check if key exists in the dictondisk,
        If yes, remove it from dict and return its value; otherwise return default.
        If default was not provided, raise KeyError.
        """
        # Only 1 default can be passed
        if len(defaults) > 1:
            raise TypeError(
                "DictOnDisk.pop() expected at most 2 arguments, got {}".format(
                    1+len(defaults)
            ))

        # Create a hash of the key
        khash = hash(key)
        fname = str(khash) + ".pkl"

        # no file exist: key not in dictondisk
        if not os.path.exists(self._path(fname)):
            # return default, if provided, otherwise raise KeyError
            if len(defaults) == 1:
                return defaults[0]

            else:
                raise KeyError(key)

        # read the items from the file
        with open(self._path(fname), "rb") as f:
            obj = pickle.load(f)

        # if key is inside pickled file,
        # get the value and remove it from obj
        if key in obj:
            value = obj[key]
            del obj[key]

            # if obj still has other items, pickle it
            if len(obj) > 0:
                with open(self._path(fname), "wb") as f:
                    pickle.dump(obj, f)

            # otherwise remove the file
            else:
                os.remove(self._path(fname))

            return value

        else:
            # return default, if provided, otherwise raise KeyError
            if len(defaults) == 1:
                return defaults[0]

            else:
                raise KeyError(key)

    def popitem(self):
        """
        Remove and return an arbitrary (key, value) pair
        If dictondisk is empty, raises KeyError.
        """
        # Pick a random file
        fname = None
        with os.scandir(self.folder.name) as fpicker:

            for i in fpicker:
                # Only consider .pkl files
                if i.name.endswith(".pkl"):
                    fname = i.name
                    break

            else:
                raise KeyError("popitem(): dictondisk is empty")

        # read the items from the file
        with open(self._path(fname), "rb") as f:
            obj = pickle.load(f)

        # get an (key, value) from pickled dict
        key, value = obj.popitem()

        # if obj still has other items, pickle it
        if len(obj) > 0:
            with open(self._path(fname), "wb") as f:
                pickle.dump(obj, f)

        # otherwise remove the file
        else:
            os.remove(self._path(fname))

        return key, value
