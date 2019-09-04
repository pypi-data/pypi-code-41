# coding: utf-8

"""
    Felix' Website mit Blog
    The api of my blog.

    Contact: felix@felix-scholz.org
"""
from __future__ import absolute_import

__version__ = '0.0.15'

from website_python_client.configuration import Configuration
from website_python_client.exceptions import (
    OpenApiException,
    ApiException,
    ApiNotFoundException,
    ApiKeyError,
    ApiTypeError,
    ApiValueError
)
