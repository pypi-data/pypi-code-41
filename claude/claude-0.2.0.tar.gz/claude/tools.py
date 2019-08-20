import logging
from functools import wraps

from lxml.cssselect import CSSSelector

from claude.config import AppConfig
from claude.memcache import MemcacheClient

logger = logging.getLogger(__name__)

def dict_merge(source, destination):
    """
    run me with nosetests --with-doctest file.py

    >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
    >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
    >>> dict_merge(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
    True
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            dict_merge(value, node)
        else:
            destination[key] = value

    return destination


def parse_temp(temp: str) -> int:
    """This magnificent function iterates throught the string and if found a non int char, breaks"""

    number = ""
    for char in temp:
        try:
            int(char)
            number += char
        except:
            break
    return number if int(number) else None


def tree_search(selector, tree, return_first = True):
    sel = CSSSelector(selector)
    res = sel(tree)
    if not len(res):
        return None
    return res[0] if return_first else res
