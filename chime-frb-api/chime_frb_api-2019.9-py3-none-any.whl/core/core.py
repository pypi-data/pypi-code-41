#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Core API Class Object
"""

import requests
import logging
import typing as t

JSON = t.Union[str, int, float, bool, None, t.Mapping[str, "JSON"], t.List["JSON"]]

# Logging Config
LOGGING_CONFIG = {}
logging_format = "[%(asctime)s] %(process)d-%(levelname)s "
logging_format += "%(module)s::%(funcName)s():l%(lineno)d: "
logging_format += "%(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO)


class API(object):
    """
    Application Programming Interface Base Class
    """

    def __init__(self, base_url: str = None):
        """
        API Initialization

        Parameters
        ----------
        base_url : str
            Base url for API
        """
        self.base_url = base_url

    def _post(self, url: str, payload: JSON) -> JSON:
        """
        HTTP Post

        Parameters
        ----------
        url : str
            HTTP Url
        payload : JSON Encodeable
            Post Payload

        Returns
        -------
        response : json

        Raises
        ------
        requests.exceptions.RequestException
        """
        try:
            response = requests.post(self.base_url + url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise e

    def _get(self, url: str) -> JSON:
        try:
            response = requests.get(self.base_url + url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise e

    def _delete(self, url: str) -> JSON:
        try:
            response = requests.delete(self.base_url + url)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise e

    def _put(self, url: str, payload: JSON) -> JSON:
        try:
            response = requests.put(self.base_url + url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise e
