#!/usr/bin/env python


def sort_by(keys, contents, parser):
    """
    the default sort order is desc.
    :param keys: should be a list which has the index method.
    :param contents:
    :param parser:
    :return: new list
    """

    if parser.asc_key:
        index = keys.index(parser.asc_key)
        return sorted(contents, key=lambda x: x[index])
    elif parser.desc_key:
        index = keys.index(parser.desc_key)
        return sorted(contents, key=lambda x: x[index], reverse=True)

    return contents.copy()
