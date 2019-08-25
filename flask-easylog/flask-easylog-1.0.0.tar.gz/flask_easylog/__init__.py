#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module flask_easylog
--------------------

flask_easylog is a extension for flask application

"""

from .util import SpecificLevelLog, log
from .plugin import EasyLog, FMT_ACCESS_LOG, FMT_ACCESS_LOG_SEC
from .api import Api 
from .ui import Ui