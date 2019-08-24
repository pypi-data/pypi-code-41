# -*- coding: utf-8 -*-
"""OpenAPI core module"""
from openapi_core.shortcuts import (
    create_spec, validate_parameters, validate_body, validate_data,
)

__author__ = 'Shagaleev Alexey'
__email__ = 'alexey.shagaleev@yandex.ru'
__version__ = '0.12.0'
__url__ = 'https://github.com/ShagaleevAlexey/openapi-core'
__license__ = 'BSD 3-Clause License'

__all__ = [
    'create_spec', 'validate_parameters', 'validate_body', 'validate_data',
]
