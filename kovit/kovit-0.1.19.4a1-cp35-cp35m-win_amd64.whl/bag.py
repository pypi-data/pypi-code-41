# Copyright (c) 2018, Teriks
# All rights reserved.
#
# kovit is distributed under the following BSD 3-Clause License
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import random
from collections import namedtuple
from functools import reduce

__all__ = ['BagItem', 'ProbabilityBag']

BagItem = namedtuple('BagItem', ['value', 'count'])


class _NoItem:
    pass


class ProbabilityBag:
    """
    Represents a bag of items which have varying quantities.
    """

    @staticmethod
    def from_flat_choices(iterable):
        """
        Construct a bag from a flat iterable of values followed by their count/quantity.

        .. code-block:: python

            ProbabilityBag.from_flat_choices(["two-of-me", 2, "five-of-me", 5, "one-of-me", 1])

        Items that appear more than once will have their count accumulated.

        :param iterable: items followed by their count/quantity
        :return: :py:class:`kovit.ProbabilityBag`
        """

        r = ProbabilityBag()
        i = iter(iterable)

        for value, count in zip(i, i):
            existing = r._items.get(value, _NoItem)

            if existing is _NoItem:
                r._items[value] = BagItem(value, count)
            else:
                r._items[value] = BagItem(value, count + existing.count)

            r._count += count

    def __init__(self, items=None):
        """
        Construct a bag.

        Optionally from a sequence of items.

        A frequency dictionary is built from any given items.


        :param items:
        """
        self._items = {}
        self._count = 0
        if items:
            for i in items:
                self.add(i)

    def __len__(self):
        """
        :return: :py:func:`kovit.ProbabilityBag.count`
        """

        return self._count

    def get(self, item, default=None):
        """
        Get an items container by reference.

        :return: :py:class:`kovit.BagItem`
        """
        return self._items.get(item, default)

    def merge(self, other):
        """
        Merge in the items from another bag.

        :param other: :py:class:`kovit.ProbabilityBag`
        """
        for value, count in other.choices():
            self.add(value, count)

    def add(self, item, count=1):
        """
        Add an item to the bag with an optional quantity.

        If the item already exists in the bag, its count will be incremented by **count**.

        :param item: The item to add
        :param count: int
        """

        i = self.get(item, default=_NoItem)

        if i is _NoItem:
            self._items[item] = BagItem(item, count)
        else:
            self._items[item] = BagItem(item, i.count + count)

        self._count += count

    @property
    def count(self):
        """
        Return the number of items that have been added to this bag.

        This is the sum total of all item occurrences.

        :return: int
        """
        return self._count

    @property
    def unique_count(self):
        """
        Return the number of unique items that have been added to this bag.

        Items that appear more than once only count as 1.

        :return: int
        """
        return len(self._items)

    def choices_weights(self):
        """
        Iterate over tuples of items and their probability weight in the bag.

        :return: iterator over tuples (item_value, weight)
        """
        for i in self._items.values():
            yield (i.value, i.count / len(self))

    def choices_weights_flat(self):
        """
        Iterate over items followed by their probability weight in the bag.

        :return: iterator over sequence [item_value, weight, item_value, weight ...]
        """

        for i in self._items.values():
            yield i.value
            yield i.count / len(self)

    def choices(self):
        """
        Iterate over tuples of items and their frequency count in the bag.

        :return: iterator over tuples (item_value, count)
        """
        for i in self._items.values():
            yield (i.value, i.count)

    def choices_flat(self):
        """
        Iterate over items followed by their frequency count in the bag.

        :return: iterator over tuples [item_value, count, item_value, count ...]
        """
        for i in self._items.values():
            yield i.value
            yield i.count

    def values(self):
        """
        Iterate over :py:class:`kovit.BagItem` nodes in the bag.

        :return: iterator over :py:class:`kovit.BagItem` objects
        """
        return (v.value for v in self._items.values())

    def __eq__(self, other):
        """
        Compare for equality with another :py:class:`kovit.ProbabilityBag`

        :param other: :py:class:`kovit.ProbabilityBag`
        :return: bool
        """

        if not isinstance(other, ProbabilityBag):
            raise ValueError('Cannot compare ProbabilityBag to "{}"'.format(type(other).__name__))

        if self.unique_count != other.unique_count or self.count != other.count:
            return False

        for value, count in self.choices():
            o_item = other.get(value, None)
            if o_item is None or o_item.count != count:
                return False

        return True

    def __ne__(self, other):
        """
        Compare for inequality with another :py:class:`kovit.ProbabilityBag`

        :param other: :py:class:`kovit.ProbabilityBag`
        :return: bool
        """

        return not self.__eq__(other)

    def choose(self, item_filter=None):
        """
        Choose a random bag item based on probability/item frequency

        :param item_filter: Can be used to filter out certain :py:class:`kovit.BagItem`'s from selection.
                            It should be a callable that takes a :py:class:`kovit.BagItem` and returns **True**
                            if the item is an allowed choice and **False** if not.

        :return: raw **BagItem.value**
        """

        if item_filter:
            items = list(filter(item_filter, self._items.values()))
            count = reduce(lambda x, y: x + y.count, items, 0)
        else:
            items = self._items.values()
            count = self._count

        r = random.uniform(0, count)
        up_to = 0
        for item in items:
            if up_to + item.count >= r:
                return item.value
            up_to += item.count

    def __str__(self):
        return str(self._items)

    def __repr__(self):
        return self.__str__()
