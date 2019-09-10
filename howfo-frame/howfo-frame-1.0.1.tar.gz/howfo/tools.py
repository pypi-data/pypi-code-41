# -*- coding: utf-8 -*-
"""
    howfo.tools
    Implements various tools.
    :copyright: 2019 Kalaiya86
    :license: MIT License
"""

import os

from howfo.helpers import create_app


base_path = os.path.dirname(os.path.abspath(__file__))

create_app('project', base_path)

