"""Utilities for managing the pyrameter experience.

Classes
-------
CountedBase
    Base class for classes that should be counted/given a unique id.
"""

import itertools


class CountedBase(object):
    """Base class for classes that should be counted/given a unique id.

    Attributes
    ----------
    counter : itertools.count
        Counter tranking the number of class instances created.
    """

    counter = itertools.count(0)

    def __init__(self):
        self.id = next(self.__class__.counter)
