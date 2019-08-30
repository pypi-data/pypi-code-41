import json
from collections import OrderedDict

from .exceptions import UnknownLatestVersion


def json_dump(data, io):
    """
    Loads JSON data, preserving order.
    """
    json.dump(data, io, ensure_ascii=False, indent=2, separators=(',', ': '))


def json_loads(data):
    """
    Loads JSON data, preserving order.
    """
    return json.loads(data, object_pairs_hook=OrderedDict)


def get_latest_version(versions):
    """
    Returns the identifier of the latest version from a list of versions of the same extension.
    """
    if len(versions) == 1:
        return versions[0]

    for version in versions:
        if version.version == 'master':
            return version

    dated = list(filter(lambda version: version.date, versions))
    if dated:
        return max(dated, key=lambda version: version.date)

    raise UnknownLatestVersion
