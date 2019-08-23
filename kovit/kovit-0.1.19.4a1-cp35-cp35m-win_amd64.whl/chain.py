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
from collections import defaultdict

try:
    import kovit.json as _kovit_json
except ImportError:
    import kovit.pjson as _kovit_json

from kovit.bag import ProbabilityBag


class _NoItem:
    pass


def _tuplefy(items):
    return ((i,) if not isinstance(i, tuple) else i for i in items)


class Chain:
    """
    Markov Chain data structure.
    """

    def __init__(self):
        self._c = {}

    def __contains__(self, start):
        """
        Check if the chain contains a particular start item.

        :param start: start item
        :return: bool
        """
        return start in self._c

    def __getitem__(self, start):
        """
        Get the trailing :py:class:`kovit.ProbabilityBag` for a start item.

        :param start: start item
        :return: :py:class:`kovit.ProbabilityBag`
        """
        return self._c.__getitem__(start)

    def __setitem__(self, start, next_items):
        """
        Set the trailing items for a start item explicit, overwriting what is there.

        .. code-block:: python

            chain['startword'] = ['happens-once', 'happens-twice', 'happens-twice']

        :param start: start item
        :param next_items: sequence of trailing items, duplicates contribute to frequency
        """
        self._c.__setitem__(start, ProbabilityBag(_tuplefy(next_items)))

    def __delitem__(self, start):
        """
        Delete a start item and its trailing :py:class:`kovit.ProbabilityBag` from the chain.

        :param start: start item
        """
        self._c.__delitem__(start)

    def __len__(self):
        """
        Return the number of start items in the chain.

        :return: int
        """
        return len(self._c)

    def get_bag(self, start, default=None):
        """
        Get the probability bag representing trailing sequence probabilities for a certain start item.

        :param start: start item
        :param default: Default value if start item does not exist in the chain
        :return: :py:class:`kovit.ProbabilityBag` or **default**
        """
        return self._c.get(start, default)

    def set_bag(self, start, bag):
        """
        Set the probability bag representing trailing sequence probabilities for a certain start item.

        :param start: start item
        :param bag: :py:class:`kovit.ProbabilityBag`
        """
        if not isinstance(bag, ProbabilityBag):
            raise ValueError("bag must be of type ProbabilityBag")

        self._c[start] = bag

    def __eq__(self, other):
        """
        Compair this chain for equality with another chain.

        :param other: :py:class:`kovit.Chain`
        :return: bool
        """
        if not isinstance(other, Chain):
            raise ValueError('Cannot compare Chain to "{}"'.format(type(other).__name__))

        if len(self) != len(other):
            return False

        for start, bag in self.items():
            o_bag = other.get_bag(start, default=None)
            if o_bag is None:
                return False
            if o_bag != bag:
                return False
        return True

    def __ne__(self, other):
        """
        Compare this chain for inequality with another chain.

        :param other: :py:class:`kovit.Chain`
        :return: bool
        """
        return not self.__eq__(other)

    def build_frequency_dict(self):
        """
        Build a frequency dictionary from items that recur in multiple areas of the chain structure.

        :return: dict
        """

        d = defaultdict(int)
        for start, bag in self._c.items():
            d[start] += 1
            for items, cnt in bag.choices():
                for item in items:
                    d[item] += 1
        return d

    def add_to_bag(self, start, next_items, count=1):
        """
        Cumulatively add a sequential run of items that may follow a starting word.

        The items are added into a :py:class:`kovit.ProbabilityBag` if one exists
        for the start item, otherwise a bag is created and then they are added.


        .. code-block:: python

            import kovit
            from kovit.iters import iter_window, iter_runs

            chain = kovit.Chain()

            words = [...]

            for start, next_items in iter_window(words, 3):
                chain.add_to_bag(start, next_items)

            for start, next_items in iter_runs(words, 3):
                chain.add_to_bag(start, next_items)

        :param start: Start item
        :param next_items: An iterable run of items that may follow the start item in order
        :param count: Number of occurrences to add
        """
        next_items = tuple(next_items)

        entry = self.get_bag(start, _NoItem)

        if entry is _NoItem:
            new_bag = ProbabilityBag()
            new_bag.add(next_items, count=count)
            self.set_bag(start, new_bag)
        else:
            entry.add(next_items, count=count)

    def starts(self):
        """
        Iterate over start items in the chain.

        :return: iterator
        """
        return self._c.keys()

    def items(self):
        """
        Iterate over (start item, :py:class:`kovit.ProbabilityBag`) tuple pairs in the chain.

        :return: iterator
        """
        return self._c.items()

    def is_dead_end(self, start):
        """Check if a start item is a dead end in the chain, IE. Has no possible trailing items.

        (Also returns **True** if the start item does not exist)

        :param start: The start item
        :return: bool
        """
        b = self.get_bag(start, _NoItem)

        if b is _NoItem:
            return True

        if b.unique_count == 1:
            return len(next(b.values(), tuple())) == 0
        
        return False

    def random_start(self, dead_end_ok=True):
        """
        Return a random start item from the chain.

        :param dead_end_ok: Should a start with no possible trailing items at all be allowed as the return value?
        :return: start item
        """
        if dead_end_ok:
            return random.choice(tuple(self.starts()))

        return random.choice(tuple(x for x in self.starts() if not self.is_dead_end(x)))

    def walk(self, max_items=0, start=None, repeat=False, start_chooser=None, next_chooser=None):
        """
        Preform a random walk of the Markov chain, returning items based on probability
        of occurrence after the last visited state.

        :param max_items: Max items to return. 0 indicates the walk should continue until \
        the chain dead ends at a start item with no trailing items. If there is a loop in the chain \
        passing 0 will generate an infinite sequence until you break out of it (while using a for loop for iteration)

        :param start: Pick a specific start item to begin the walk from, \
        instead of using :py:func:`kovit.Chain.random_start`

        :param repeat: Whether or not to repeat if the walk dead ends, passing \
        **True** will yield an infinite sequence if your chain has at least one start with a trailing item.

        :param start_chooser: Function callback for choosing the first start when **start** is **None**, and \
        starts that occur during a walk repeat. The default function used is :py:func:`kovit.Chain.random_start`

        :param next_chooser: Function callback for choosing the next start item from a \
        :py:class:`kovit.ProbabilityBag`. This function is passed a :py:class:`kovit.ProbabilityBag`, \
        and should return an item from the bag. The default implementation delegates to \
        :py:func:`kovit.ProbabilityBag.choose`.

        :return: iterator
        """

        if start_chooser is None:
            start_chooser = self.random_start

        if next_chooser is None:
            def next_chooser(bag):
                return bag.choose()

        if start is None:
            start = (start_chooser(),)
        else:
            start = (start,)

        cnt = 0

        while True:
            assert type(start) is tuple

            for start_next in start:
                if max_items == 0 or cnt < max_items:
                    yield start_next
                    cnt += 1
                else:
                    return

            if len(start):
                while True:
                    # start_next will be set to the last item
                    # iterated to above if any iteration happened
                    bag = self.get_bag(start_next, default=None)
                    if bag is not None:
                        break
                    if not repeat:
                        return
                    start_next = start_chooser()

                start = next_chooser(bag)

                if start is None:
                    if repeat:
                        start = (start_chooser(),)
                    else:
                        break

            elif repeat:
                start = (start_chooser(),)
            else:
                return

    def __str__(self):
        return str(self._c)

    def __repr__(self):
        return self.__str__()

    def dump_json(self, file, frequency_compress=True, large_file=False):
        """
        Dump the chain as JSON to a file.

        :param file: file object

        :param frequency_compress: Whether or not to use dictionary compression for items in the chain.
                                   Items will be given a code based on their frequency and then be referenced
                                   by it in the chain instead of duplicated, this works well for text.

        :param large_file: Whether or not to optimize the file write to use less memory, if **True** the chain
                           will be written progressively to the file instead of dumped all at once, which is
                           much slower.
        """
        if large_file:
            _kovit_json.dump_json_big(self, file, frequency_compress=frequency_compress)
        else:
            _kovit_json.dump_json_small(self, file, frequency_compress=frequency_compress)

    def load_json(self, file, merge=False, large_file=False):
        """
        Read the chain in from a JSON file.

        The file should be opened in read binary mode 'rb' for YAJL compatibility.

        :param file: file object

        :param merge: Whether or not to merge the chain data with the existing chain.

        :param large_file: Whether or not to optimize the file load to use less memory, if **True** the chain
                           will be read and built progressively from the file instead of all at once, which is
                           much slower.
        """
        if large_file:
            _kovit_json.load_json_big(self, file, merge=merge)
        else:
            _kovit_json.load_json_small(self, file, merge=merge)

    def clear(self):
        """
        Clear the chain of all items.
        """
        self._c.clear()
