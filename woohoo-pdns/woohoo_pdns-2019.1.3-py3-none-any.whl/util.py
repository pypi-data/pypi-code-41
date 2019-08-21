# -*- encoding: utf-8 -*-

import logging

from collections import namedtuple

record_data = namedtuple("pdns_entry_tokens", ["first_seen", "last_seen", "rrtype", "rrname", "hitcount", "rdata",
                                               "key"])
"""
A named tuple holding the values of a single entry in the pDNS database.

Note:
    first_seen and last_seen can be both, datetimes or timestamps (integers) but it must be consistent.
    The 'key' field can be left empty; it will then be auto-populated by the cache in a consistent way. If it is
    non-empty the passed in key is kept and it is the caller's responsibility to guarantee uniqueness of the key(s).
"""


class LoaderCache:
    """
    This class implements the cache used when loading entries into the database.

    Because pDNS databases have to ingest high volumes of data with high redundancy (never seen before entries are
    comparatively rare) it can be expected that caching substantially improves performance.

    The cache internally holds values in dictionaries with a key derived from the actual data. To add records to the
    cache the named tuple 'record_data' should be used.

    Note:
        When adding a record to the cache, four modes are available: cache_only, new, updated and auto. For a
        description of the modes, see the documentation of the "modes" named tuple.
    """
    modes = namedtuple("cache_modes", ["cache_only", "new", "updated", "auto"])
    """
    The mode is relevant when adding records to the cache that are not already present in the cache. 'cache_only' should
    only be used to (pre) populate the cache. This is mainly useful if the 'auto' mode should be used later on. 'auto'
    assumes that the cache already holds *all* relevant entries; therefore, when adding an entry it will be cached as
    'new' if it was not present in the cache before and as 'updated' if it already was in the cache.
    If the mode is set to 'new', the entry will be considered to be new (i.e. returned by :func:`get_new_entries`)
    whereas with the mode set to 'updated' it will be considered to already be known by the pDNS database (but not
    necessarily the cache, i.e. it will be returned by :func:`get_to_update`). 
    """
    MODES = modes(1, 2, 4, 8)

    def __init__(self):
        self._l = logging.getLogger(__name__)
        self.new_entries = {}
        self.updated_entries = {}
        self.cache_only_entries = {}

    def __contains__(self, item):
        """
        Checks if the cache contains the entry represented by the named tuple (or dict) passed in.

        Args:
            item (record_data): The record which should be checked for presence in the cache.

        Returns:
            True if the item is in the cache, false otherwise.
        """
        item = LoaderCache._dictionise(item)
        item_key = list(item.keys())[0]
        return (item_key in self.new_entries) or\
               (item_key in self.updated_entries) or\
               (item_key in self.cache_only_entries)

    def get_new_entries(self, for_bulk=False):
        """
        Return the list of items that are considered not to be present in the pDNS database yet.

        Note:
            The main reason for differentiating between new and updated entries (with respect to the pDNS database, not
            the cache) is to allow bulk operations in SQLAlchemy; it must be known if 'INSERT' or 'UPDATE' statements
            should be used.

        Args:
            for_bulk (bool): If true, a list of dictionaries will be returned (suitable for SQLAlchemy bulk operations),
                if false, a list of record_data named tuples will be returned.
                For more information about SQLAlchemy bulk operations, see `the SQLAlchemy documentation on bulk
                operations`_.

                .. _the SQLAlchemy documentation on bulk operations:
                    https://docs.sqlalchemy.org/en/13/orm/persistence_techniques.html#bulk-operations.

        Returns:
            A list of either named tuples or dictionaries (see 'for_bulk' argument).
        """
        if for_bulk:
            return list(self.new_entries.values())
        else:
            return [LoaderCache._tupelise(i_k, i_v) for i_k, i_v in self.new_entries.items()]

    def get_to_update(self, for_bulk=False):
        """
        The same as :meth:`get_new_entries` but for entries considered to already be present in the pDNS database (not
        necessarily the cache).

        Args:
            for_bulk (bool): see argument with the same name documented for :meth:`get_new_entries`

        Returns:
            A list of either named tuples or dictionaries (see 'for_bulk' argument).
        """
        if for_bulk:
            return list(self.updated_entries.values())
        else:
            return [LoaderCache._tupelise(i_k, i_v) for i_k, i_v in self.updated_entries.items()]

    def add(self, item, mode=MODES.auto):
        """
        Add a new item to the cache.

        Args:
            item (record_data): The representation of the item to add to the cache.
            mode (mode): What mode to use (see documentation of mode for details) if the record is not yet in the cache.

        Returns:
            Nothing.
        """
        item = LoaderCache._dictionise(item)
        was_already_cached = 0

        # list(item.keys())[0] gets the "first" (i.e. only) element from the dict
        item_key, item_value = list(item.items())[0]

        try:
            # Check if key already exists in "new_entries"
            ex = self.new_entries[item_key]
            was_already_cached = self.MODES.new
        except KeyError:
            try:
                # Check if key already exists in "updated_entries"
                ex = self.updated_entries[item_key]
                was_already_cached = self.MODES.updated
            except KeyError:
                try:
                    # Check if key already exists in "cache_only_entries"
                    ex = self.cache_only_entries[item_key]
                    was_already_cached = self.MODES.cache_only
                except KeyError:
                    ex = None

        if ex:
            LoaderCache.merge(ex, item_value)
            # self._l.debug("was_already_cached: {}".format(was_already_cached))
            if was_already_cached == self.MODES.new:
                # if the entry already was in "new_entries", update it there
                self.new_entries.update(item)
            else:
                # if the entry already was in "updated_entries" or "cache_only entries", update it in "updated_entries"
                self.updated_entries.update(item)
            if was_already_cached == self.MODES.cache_only:
                # remove entry from "cache_only entries" if it was there as it is now a "to be updated" entry
                del self.cache_only_entries[item_key]
        else:
            if mode == self.MODES.auto or mode == self.MODES.new:
                # self._l.info()
                self._add_to_new(item)
            elif mode == self.MODES.cache_only:
                self._add_to_cache_only(item)
            else:
                self._add_to_update(item)

    def rollover(self):
        """
        Should be called after the pDNS database is updated with the currently cached entries (i.e. after the bulk
        operations are done for the lists returned by :meth:`get_new_entries` and :meth:`get_to_update`).

        This will 'move' all cached entries into the 'cache_only' status, indicating that they are 'known' but not
        'dirty' (in a cache's way of using that word).

        Returns:
            Nothing.
        """
        self.cache_only_entries.update(self.new_entries)
        self.new_entries.clear()
        self.cache_only_entries.update(self.updated_entries)
        self.updated_entries.clear()

    def clear(self):
        """
        Clear the cache (i.e. remove all entries).

        Returns:
            Nothing.
        """
        self.new_entries.clear()
        self.updated_entries.clear()
        self.cache_only_entries.clear()

    @staticmethod
    def _dictionise(item):
        """
        Convert 'item' (named tuple class:`record_data`) into a dictionary `{ key: item }`

        Args:
            item (class:`record_data`): the item to 'convert' into a dictionary

        Returns:
             dict with one key (item.key, if it was set) and item as its value
        """
        if not isinstance(item, dict):
            if item.key:
                key = item.key
            else:
                key = "{}|{}|{}".format(item.rrtype, item.rrname, item.rdata)
            dict_item = {
                key: {
                    "first_seen": item.first_seen,
                    "last_seen": item.last_seen,
                    "rrtype": item.rrtype,
                    "_rrname": item.rrname,
                    "hitcount": item.hitcount,
                    "_rdata": item.rdata,
                    "key": key,
                }
            }
        else:
            dict_item = item
        return dict_item

    @staticmethod
    def _tupelise(item_key, item_value):
        """
        Convert 'item_key, item_value' (value of type dictionary) into a named tuple class:`record_data`

        Args:
            item_key (str): the key that is used for the 'value dict'
            item_value (dict): a dictionary that holds the relevant data to create a class:`record_data`

        Returns:
            item (class:`record_data`): the item that results from 'converting' the dictionary
        """
        if not isinstance(item_value, dict):
            return item_value

        tup = record_data(
            item_value["first_seen"],
            item_value["last_seen"],
            item_value["rrtype"],
            item_value["_rrname"],
            item_value["hitcount"],
            item_value["_rdata"],
            item_key
        )

        return tup

    def _add_to_new(self, item):
        self.new_entries.update(item)

    def _add_to_update(self, item):
        self.updated_entries.update(item)

    def _add_to_cache_only(self, item):
        self.cache_only_entries.update(item)

    @staticmethod
    def merge(existing, new):
        """
        Merge two cached items by updating the *new* item's hitcount (add the existing item's count to it) and set the
        *new* item's first_seen and last_seen to the minimum (maximum) of the new and the existing item's values.

        Args:
            existing (dict): An item present in the cache
            new (dict): An item that should be updated with the info already present in the cache.

        Returns:
            Nothing, the *new* item will be updated in place.
        """
        new["hitcount"] += existing["hitcount"]
        try:
            if existing["first_seen"] < new["first_seen"]:
                new["first_seen"] = existing["first_seen"]
            if existing["last_seen"] > new["last_seen"]:
                new["last_seen"] = existing["last_seen"]
        except TypeError:
            print("ERROR REC: {} ({})".format(existing, new))
            raise


def sanitise_input(str_in):
    """DNS entries technically end in a dot but for pDNS purposes the dot is mainly cruft, so we remove it.

    Note:
        If the input string to this function is just a dot, it is kept. While a single dot might be 'surprising' it is
        still better than an empty string.
    """
    if str_in.endswith(".") and len(str_in) > 1:
        str_in = str_in[:-1]
    return str_in


def record_to_nt(rec):
    """Takes a dictionary style cache entry and returns a corresponding named tuple.

    Note:
        The "key" is not set because the other functions in this module do not require it (DRY).
    """
    first_seen = rec.first_seen
    last_seen = rec.last_seen
    rrtype = rec.rrtype
    rrname = rec.rrname
    hitcount = rec.hitcount
    rdata = rec.rdata

    return record_data(first_seen, last_seen, rrtype, rrname, hitcount, rdata, None)


"""
import logging
logging.basicConfig(level=logging.DEBUG)
from woohoo_pdns.util import BulkCache
bc = BulkCache()
a = {"k1": {"hitcount": 1, "first_seen": 10, "last_seen": 20}}
b = {"k2": {"hitcount": 2, "first_seen": 2, "last_seen": 40}}
c = {"k1": {"hitcount": 3, "first_seen": 12, "last_seen": 25}}
d = {"k1": {"hitcount": 5, "first_seen": 5, "last_seen": 10}}

bc.update(a)
bc.update(b)

bc.update(c)

bc.update(d)
"""
