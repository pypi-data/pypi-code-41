import re
from enum import Enum
from urllib.parse import urljoin

import requests

COMMAND_SUFFIX = "Command"


def camel2kebab(string):
    """
    Transforms CamelCase to kebab-case

    Adapted from http://stackoverflow.com/questions/1796180/ddg#1796247

    :type string: basestring
    :rtype: basestring
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()


class StringListEnum(Enum):
    def __str__(self):
        return self.name.lower()

    @classmethod
    def get(cls, name, case_insensitive=True):
        """
        Tries to get the member of the given name

        Written for use with the `type` arg of
         argparse.ArgumentParser::add_argument

        :param name: name of the member
        :type name: basestring
        :param case_insensitive: Member names are typically uppercase
                                 so the given name will be uppsercased
        :type case_insensitive: boolean
        :return: 
        :rtype: 
        """
        if case_insensitive:
            name = name.upper()
        return cls.__members__.get(name)


class RelativeSession(requests.Session):
    def __init__(self, base_url):
        super(RelativeSession, self).__init__()
        self.__base_url = base_url

    def request(self, method, url, **kwargs):
        url = urljoin(self.__base_url, url)
        return super(RelativeSession, self).request(method, url, **kwargs)
