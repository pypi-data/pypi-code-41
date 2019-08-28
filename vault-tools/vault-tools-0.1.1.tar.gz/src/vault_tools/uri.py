#!/usr/bin/env python3
"""
Fetches secrets from vault from environment variables prefixed with secret://vault/[...]
"""
import urllib.parse as url_parser

from functools import lru_cache
from typing import Any

from conversion import convert_bool

SECRET_PREFIX = 'secret'


class SecretURI:
    """
    An interface around urllib functions to expose URI details as attributes

    ParseResult(scheme='secret', netloc='vault', path='/secret/something', params='', query='key=name', fragment='')
    """
    def __init__(self, uri: str, default_key: str = 'value', default_write_env: bool = True):
        self.default_key = default_key
        self.uri_s = uri  # the string version of the URI
        self.default_write_env = default_write_env

    @property
    def encode(self) -> str:
        return self.get_param('encode')

    def get_param(self, key: str, default: Any = None) -> str:
        """
        Returns the first item in a value list within the dictionary key
        """
        value = self.params.get(key)

        item = value
        if isinstance(item, list):
            item = item[0]

        return item or default

    @property
    def is_secret(self) -> bool:
        """
        Returns whether the scheme is secret://
        """
        return self.uri.scheme == SECRET_PREFIX

    @property
    def key(self) -> str:
        """
        Returns the key in the query params or the default key name
        """
        return self.get_param('key', default=self.default_key)

    @property
    @lru_cache()
    def params(self) -> dict:
        """
        Returns parsed query parameters
        """
        return url_parser.parse_qs(self.uri.query)

    @property
    @lru_cache()
    def uri(self) -> url_parser.ParseResult:
        """
        Returns parsed URI
        """
        return url_parser.urlparse(self.uri_s)

    @property
    @lru_cache()
    def path(self):
        """
        Returns the secret's path from the URI
        """
        return self.uri.path

    @property
    @lru_cache()
    def write_env(self) -> bool:
        write_env = self.get_param('write_env')

        return convert_bool(write_env) if write_env else self.default_write_env
