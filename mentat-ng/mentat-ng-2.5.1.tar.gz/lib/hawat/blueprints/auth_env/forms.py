#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains custom user account registration form for Hawat.
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import wtforms
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField

#
# Flask related modules.
#
from flask_babel import lazy_gettext

#
# Custom modules.
#
import hawat.db
from hawat.blueprints.users.forms import BaseUserAccountForm
from mentat.datatype.sqldb import GroupModel


def get_available_groups():
    """
    Query the database for list of all available groups.
    """
    return hawat.db.db_query(GroupModel).order_by(GroupModel.name).all()


class RegisterUserAccountForm(BaseUserAccountForm):
    """
    Class representing user account registration form.
    """
    memberships_wanted = QuerySelectMultipleField(
        lazy_gettext('Requested group memberships:'),
        query_factory = get_available_groups,
        allow_blank = True
    )
    justification = wtforms.TextAreaField(
        lazy_gettext('Justification:'),
        validators = [
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min = 10, max = 500)
        ]
    )
