import json
import re
import six


def normalise_string(string):
    """ Strips trailing whitespace from string, lowercases it and replaces
        spaces with underscores
    """
    string = (string.strip()).lower()
    return re.sub(r'\W+', '_', string)


def json_decode(data):
    """
    Decodes the given JSON as primitives
    """
    if isinstance(data, six.binary_type):
        data = data.decode('utf-8')

    return json.loads(data)
