#!/usr/bin/env python
from clima import c, Schema
import requests
import logging


@c
class C(Schema):
    debug: bool = False  # Enable verbose printout
    url: str = 'https://pypi.org'  # This will be overriden by foo.cfg


c: C = c


@c
class MyCurl:
    # data = ''

    def _configure(self):
        if c.debug:
            logging.getLogger('requests').setLevel(logging.DEBUG)

    def headers(self):
        """This here, prints my age"""
        self._configure()
        res = requests.get(c.url)
        print(res.headers)
