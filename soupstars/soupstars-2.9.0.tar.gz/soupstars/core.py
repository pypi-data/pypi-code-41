"""
Primary objects here
"""

import importlib
import json
import re

import requests
from bs4 import BeautifulSoup


def parse(function):
    function._soupstar = True
    return function


class BeautifulSoupStar(BeautifulSoup):
    """
    An enhanced BeautifulSoup object, with additional helper methods
    """

    def find_text(self, text):
        regex = re.compile(text)
        result = self.find(text=re.compile(regex))
        if result:
            return result.parent

    def find_class(self, klass):
        regex = re.compile(klass)
        return self.find_all(attrs={'class': regex})

    def links(self, format=True):
        return [a.get('href') for a in self.find_all('a')]

    def title(self):
        return self.find('title').text


# TODO: methodology for catching parser errors
# TODO: methodology for using a "save" function
# TODO: figure out passing params to the init
#   Use the params passed by the caller
#   Otherwise use the attributes defined on the module
# TODO: figure out running parsers from anywhere, ie relative paths
class SoupStar(object):
    """
    The primary SoupStar object
    """

    def __init__(self, module, url=None):
        self.module_string = module
        self.module = importlib.import_module(module)
        self.url = url or self.module.url
        self.loaded = False
        self.errors = {}

    @property
    def parsers(self):
        # Any function from the module that has been tagged with @parse
        return {k: v for k, v in vars(self.module).items()
                if hasattr(v, '_soupstar')}

    def load(self):
        self.response = requests.get(self.url)
        self.soup = BeautifulSoupStar(
            self.response.content,
            features="html.parser"
        )
        self.soup.response = self.response
        self.soup.url = self.url
        self.loaded = True

    def to_tuples(self):
        if not self.loaded:
            self.load()

        for parser_name, parser_func in self.parsers.items():
            yield parser_name, parser_func(self.soup)

    def to_dict(self):
        return {
            'data': dict(self.to_tuples()),
            'status': self.response.status_code,
            'url': self.url,
            'errors': self.errors
        }

    def to_json(self):
        return json.dumps(self.to_dict(), default=str)
