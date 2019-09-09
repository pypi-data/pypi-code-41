#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains custom reporting filter management forms for Hawat.
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import pynspect.gparser

import wtforms
from wtforms.ext.sqlalchemy.fields import QuerySelectField

#
# Flask related modules.
#
import flask_wtf
from flask_babel import gettext, lazy_gettext

#
# Custom modules.
#
import hawat.db
import hawat.forms
from mentat.datatype.sqldb import GroupModel
from mentat.const import REPORTING_FILTER_BASIC, REPORTING_FILTER_ADVANCED
from mentat.idea.internal import Idea


def get_available_groups():
    """
    Query the database for list of all available groups.
    """
    return hawat.db.db_query(GroupModel).order_by(GroupModel.name).all()


def check_filter(form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating Pynspect filter.
    """
    psr = pynspect.gparser.PynspectFilterParser()
    psr.build()
    try:
        psr.parse(field.data)
    except Exception as err:
        raise wtforms.validators.ValidationError(
            gettext(
                'Filtering rule parse error: "%(error)s".',
                error = str(err)
            )
        )

def check_event(form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating IDEA event JSON.
    """
    try:
        Idea.from_json(field.data)
    except Exception as err:
        raise wtforms.validators.ValidationError(
            gettext(
                'Event JSON parse error: "%(error)s".',
                error = str(err)
            )
        )


#-------------------------------------------------------------------------------


class BaseFilterForm(hawat.forms.BaseItemForm):
    """
    Class representing base reporting filter form.
    """
    name = wtforms.StringField(
        lazy_gettext('Name:'),
        validators = [
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min = 3, max = 250)
        ]
    )
    type = wtforms.SelectField(
        lazy_gettext('Type:'),
        validators = [
            wtforms.validators.DataRequired(),
        ],
        choices = [
            (REPORTING_FILTER_BASIC,    lazy_gettext('Basic')),
            (REPORTING_FILTER_ADVANCED, lazy_gettext('Advanced'))
        ]
    )
    description = wtforms.TextAreaField(
        lazy_gettext('Description:'),
        validators = [
            wtforms.validators.DataRequired(),
        ]
    )
    filter = wtforms.TextAreaField(
        lazy_gettext('Filter:'),
        validators = [
            wtforms.validators.Optional(),
            check_filter
        ]
    )
    detectors = wtforms.SelectMultipleField(
        lazy_gettext('Detectors:'),
        validators = [
            wtforms.validators.Optional(),
        ],
        choices = [('', lazy_gettext('<< no preference >>'))],
        filters = [lambda x: x or []]
    )
    categories = wtforms.SelectMultipleField(
        lazy_gettext('Categories:'),
        validators = [
            wtforms.validators.Optional(),
        ],
        choices = [('', lazy_gettext('<< no preference >>'))],
        filters = [lambda x: x or []]
    )
    ips = hawat.forms.CommaListField(
        lazy_gettext('Source IPs:'),
        validators = [
            wtforms.validators.Optional(),
            hawat.forms.check_network_record_list
        ],
        widget = wtforms.widgets.TextArea()
    )
    valid_from = hawat.forms.SmartDateTimeField(
        lazy_gettext('Valid from:'),
        validators = [
            wtforms.validators.Optional()
        ]
    )
    valid_to = hawat.forms.SmartDateTimeField(
        lazy_gettext('Valid to:'),
        validators = [
            wtforms.validators.Optional()
        ]
    )
    enabled = wtforms.RadioField(
        lazy_gettext('State:'),
        validators = [
            wtforms.validators.InputRequired(),
        ],
        choices = [
            (True,  lazy_gettext('Enabled')),
            (False, lazy_gettext('Disabled'))
        ],
        filters = [hawat.forms.str_to_bool],
        coerce = hawat.forms.str_to_bool
    )
    submit = wtforms.SubmitField(
        lazy_gettext('Submit')
    )
    preview = wtforms.SubmitField(
        lazy_gettext('Preview')
    )
    cancel = wtforms.SubmitField(
        lazy_gettext('Cancel')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.detectors.choices[1:]  = kwargs['choices_detectors']
        self.categories.choices[1:] = kwargs['choices_categories']


class AdminFilterForm(BaseFilterForm):
    """
    Class representing reporting filter create form.
    """
    group = QuerySelectField(
        lazy_gettext('Group:'),
        query_factory = get_available_groups,
        allow_blank = False
    )

class PlaygroundFilterForm(flask_wtf.FlaskForm):
    """
    Class representing IP geolocation search form.
    """
    filter = wtforms.TextAreaField(
        lazy_gettext('Filtering rule:'),
        validators = [
            wtforms.validators.DataRequired(),
            check_filter
        ]
    )
    event = wtforms.TextAreaField(
        lazy_gettext('IDEA event:'),
        validators = [
            wtforms.validators.DataRequired(),
            check_event
        ]
    )
    submit = wtforms.SubmitField(
        lazy_gettext('Check')
    )
