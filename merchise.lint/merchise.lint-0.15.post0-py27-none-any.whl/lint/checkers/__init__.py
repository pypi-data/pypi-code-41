#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (
    division as _py3_division,
    print_function as _py3_print,
    absolute_import as _py3_abs_import,
)

from .absolute_import_check import AbsoluteImportCheck  # noqa
from .pdb_check import AvoidPdb  # noqa
from .break_or_cont import BreakContinueCheck  # noqa
from .odoo_i18n import MangledI18NWithFStringsCheck  # noqa
