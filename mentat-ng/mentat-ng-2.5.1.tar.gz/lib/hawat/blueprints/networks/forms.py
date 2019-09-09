#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains custom network record management forms for Hawat.
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import wtforms
from wtforms.ext.sqlalchemy.fields import QuerySelectField

#
# Flask related modules.
#
from flask_babel import lazy_gettext

#
# Custom modules.
#
import hawat.const
import hawat.db
import hawat.forms
from mentat.datatype.sqldb import GroupModel


def get_available_groups():
    """
    Query the database for list of all available groups.
    """
    return hawat.db.db_query(GroupModel).order_by(GroupModel.name).all()


class BaseNetworkForm(hawat.forms.BaseItemForm):
    """
    Class representing base network record form.
    """
    netname = wtforms.StringField(
        lazy_gettext('Netname:'),
        validators = [
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min = 3, max = 250)
        ]
    )
    source = wtforms.HiddenField(
        default = 'manual',
        validators = [
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min = 3, max = 50)
        ]
    )
    network = wtforms.TextAreaField(
        lazy_gettext('Network:'),
        validators = [
            wtforms.validators.DataRequired(),
            hawat.forms.check_network_record
        ]
    )
    description = wtforms.TextAreaField(
        lazy_gettext('Description:')
    )
    submit = wtforms.SubmitField(
        lazy_gettext('Submit')
    )
    cancel = wtforms.SubmitField(
        lazy_gettext('Cancel')
    )


class AdminNetworkForm(BaseNetworkForm):
    """
    Class representing network record create form.
    """
    group = QuerySelectField(
        lazy_gettext('Group:'),
        query_factory = get_available_groups,
        allow_blank = False
    )
