#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains custom internal event timeline search form for Hawat.
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import wtforms

import flask_wtf
from flask_babel import lazy_gettext

import hawat.const
import hawat.db
import hawat.forms


class SimpleTimelineSearchForm(flask_wtf.FlaskForm):
    """
    Class representing simple event timeline search form.
    """
    source_addrs = hawat.forms.CommaListField(
        lazy_gettext('Source addresses:'),
        validators = [
            wtforms.validators.Required(),
            hawat.forms.check_network_record_list
        ]
    )
    dt_from = hawat.forms.SmartDateTimeField(
        lazy_gettext('Detection time from:'),
        validators = [
            wtforms.validators.Optional()
        ]
    )
    dt_to = hawat.forms.SmartDateTimeField(
        lazy_gettext('Detection time to:'),
        validators = [
            wtforms.validators.Optional()
        ]
    )
    submit = wtforms.SubmitField(
        lazy_gettext('Search')
    )

    @staticmethod
    def is_multivalue(field_name):
        """
        Check, if given form field is a multivalue field.

        :param str field_name: Name of the form field.
        :return: ``True``, if the field can contain multiple values, ``False`` otherwise.
        :rtype: bool
        """
        if field_name in ('source_addrs',):
            return True
        return False
