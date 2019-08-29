# -*- coding: utf-8 -*-

# auxilium
# --------
# A Python project for an automated test and deploy toolkit - 100%
# reusable.
# 
# Author:   sonntagsgesicht
# Version:  0.1, copyright Thursday, 29 August 2019
# Website:  https://github.com/sonntagsgesicht/auxilium
# License:  Apache License 2.0 (see LICENSE file)


__doc__ = 'A Python project for an automated test and deploy toolkit - 100% reusable.'
__version__ = '0.1'
__dev_status__ = '3 - Alpha'
__date__ = 'Thursday, 29 August 2019'
__author__ = 'sonntagsgesicht'
__email__ = __author__ + '@icloud.com'
__url__ = 'https://github.com/' + __author__ + '/' + __name__
__license__ = 'Apache License 2.0'
__dependencies__ = 'pylint', 'coverage', 'bandit', 'twine', 'sphinx', 'sphinx_rtd_theme', 'flake8'
__dependency_links__ = ()
__data__ = ('data/pkg.zip',)
__scripts__ = ('auxilium/scripts/auxilium',)

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

from .tools.doc_tools import set_timestamp, replace_headers
from .tools.rst_tools import replacements_str, replacements_from_pkg, replacements_from_cls, replacements
from .tools.pkg_tools import create_project
