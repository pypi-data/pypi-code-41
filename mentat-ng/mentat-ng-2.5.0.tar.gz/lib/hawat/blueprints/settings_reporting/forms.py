#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains custom reporting settings management forms for Hawat.
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import os
import pytz
import wtforms
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from babel import Locale

#
# Flask related modules.
#
from flask_babel import gettext, lazy_gettext

#
# Custom modules.
#
import hawat.const
import hawat.db
import hawat.forms
import mentat.const
from mentat.datatype.sqldb import GroupModel


REPORT_TRANSLATIONS = '/etc/mentat/templates/reporter/translations'


def get_available_groups():
    """
    Query the database for list of all available groups.
    """
    return hawat.db.db_query(GroupModel).order_by(GroupModel.name).all()


def get_available_locales():
    """
    Get list available report translations.
    """
    locale_list = [['en', 'en']]

    if os.path.isdir(REPORT_TRANSLATIONS):
        for translation in os.listdir(REPORT_TRANSLATIONS):
            if translation[0] == '.':
                continue
            if os.path.isdir(os.path.join(REPORT_TRANSLATIONS, translation)):
                locale_list.append([translation, translation])

    locale_list = sorted(locale_list, key = lambda x: x[0])

    for translation in locale_list:
        locale_obj = Locale.parse(translation[0])
        translation[1] = locale_obj.language_name.lower()

    return locale_list


def check_defined_when_custom(form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating reporting timing settings for 'custom' setting.
    """
    if form.timing.data and form.timing.data == mentat.const.REPORTING_TIMING_CUSTOM:
        if field.data is not None:
            return
        raise wtforms.validators.ValidationError(
            gettext(
                'The "%(val)s" reporting timing must be set to valid value for "custom" reporting timing.',
                val = str(field.name)
            )
        )


class BaseSettingsReportingForm(hawat.forms.BaseItemForm):
    """
    Class representing base reporting settings form.
    """
    mode = wtforms.SelectField(
        lazy_gettext('Reporting mode:'),
        validators = [
            wtforms.validators.Optional(),
        ],
        choices = [
            ('',                                  lazy_gettext('<< system default >>')),
            (mentat.const.REPORTING_MODE_SUMMARY, lazy_gettext('summary')),
            (mentat.const.REPORTING_MODE_EXTRA,   lazy_gettext('extra')),
            (mentat.const.REPORTING_MODE_BOTH,    lazy_gettext('both')),
            (mentat.const.REPORTING_MODE_NONE,    lazy_gettext('none'))
        ],
        filters = [lambda x: x or None]
    )
    attachments = wtforms.SelectField(
        lazy_gettext('Report attachments:'),
        validators = [
            wtforms.validators.Optional(),
        ],
        choices = [
            ('',                                 lazy_gettext('<< system default >>')),
            (mentat.const.REPORTING_ATTACH_JSON, lazy_gettext('json')),
            (mentat.const.REPORTING_ATTACH_CSV,  lazy_gettext('csv')),
            (mentat.const.REPORTING_ATTACH_ALL,  lazy_gettext('all')),
            (mentat.const.REPORTING_ATTACH_NONE, lazy_gettext('none'))
        ],
        filters = [lambda x: x or None]
    )
    emails = hawat.forms.CommaListField(
        lazy_gettext('Target emails:'),
        validators = [
            wtforms.validators.Optional(),
            hawat.forms.check_email_list
        ]
    )
    mute = hawat.forms.RadioFieldWithNone(
        lazy_gettext('Mute reporting:'),
        validators = [
            wtforms.validators.Optional(),
        ],
        choices = [
            (None,  lazy_gettext('System default')),
            (True,  lazy_gettext('Enabled')),
            (False, lazy_gettext('Disabled'))
        ],
        filters = [hawat.forms.str_to_bool_with_none],
        coerce = hawat.forms.str_to_bool_with_none
    )
    redirect = hawat.forms.RadioFieldWithNone(
        lazy_gettext('Report redirection:'),
        validators = [
            wtforms.validators.Optional(),
        ],
        choices = [
            (None,  lazy_gettext('System default')),
            (True,  lazy_gettext('Enabled')),
            (False, lazy_gettext('Disabled'))
        ],
        filters = [hawat.forms.str_to_bool_with_none],
        coerce = hawat.forms.str_to_bool_with_none
    )
    compress = hawat.forms.RadioFieldWithNone(
        lazy_gettext('Attachment compression:'),
        validators = [
            wtforms.validators.Optional(),
        ],
        choices = [
            (None,  lazy_gettext('System default')),
            (True,  lazy_gettext('Enabled')),
            (False, lazy_gettext('Disabled'))
        ],
        filters = [hawat.forms.str_to_bool_with_none],
        coerce = hawat.forms.str_to_bool_with_none
    )
    template = wtforms.StringField(
        lazy_gettext('Template:'),
        validators = [
            wtforms.validators.Optional()
        ],
        filters = [lambda x: x or None]
    )
    locale = wtforms.SelectField(
        lazy_gettext('Locale:'),
        validators = [
            wtforms.validators.Optional(),
        ],
        choices = [('', lazy_gettext('<< system default >>'))] + get_available_locales(),
        filters = [lambda x: x or None]
    )
    timezone = wtforms.SelectField(
        lazy_gettext('Timezone:'),
        validators = [
            wtforms.validators.Optional(),
        ],
        choices = [('', lazy_gettext('<< system default >>'))] + list(zip(pytz.common_timezones, pytz.common_timezones)),
        filters = [lambda x: x or None]
    )
    max_attachment_size = hawat.forms.SelectFieldWithNone(
        lazy_gettext('Attachment size limit:'),
        validators = [
            wtforms.validators.Optional(),
        ],
        coerce = hawat.forms.str_to_int_with_none,
        choices = [
            (None, lazy_gettext('<< system default >>')),
            (0, lazy_gettext('<< no limit >>'))
        ] + list(reversed(sorted(mentat.const.REPORT_ATTACHMENT_SIZES.items(), key = lambda x: x[0]))),
        default = mentat.const.DFLT_REPORTING_MAXATTACHSIZE
    )
    timing = hawat.forms.RadioFieldWithNone(
        lazy_gettext('Reporting timing:'),
        validators = [
            wtforms.validators.Optional(),
        ],
        choices = [
            (None,                                  lazy_gettext('System default')),
            (mentat.const.REPORTING_TIMING_DEFAULT, lazy_gettext('Default')),
            (mentat.const.REPORTING_TIMING_CUSTOM,  lazy_gettext('Custom'))
        ],
        filters = [lambda x: x or None]
    )
    timing_per_lo = wtforms.SelectField(
        lazy_gettext('Reporting period:'),
        validators = [
            wtforms.validators.Optional(),
            check_defined_when_custom
        ],
        coerce = int,
        choices = [y for y in sorted(mentat.const.REPORTING_INTERVALS_INV.items(), key = lambda x: x[0]) if y[0] != 0],
        default = 3600
    )
    timing_thr_lo = wtforms.SelectField(
        lazy_gettext('Reporting threshold:'),
        validators = [
            wtforms.validators.Optional(),
            check_defined_when_custom
        ],
        coerce = int,
        choices = sorted(mentat.const.REPORTING_INTERVALS_INV.items(), key = lambda x: x[0]),
        default = mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_LOW_THR]
    )
    timing_rel_lo = wtforms.SelectField(
        lazy_gettext('Reporting relapse:'),
        validators = [
            wtforms.validators.Optional(),
            check_defined_when_custom
        ],
        coerce = int,
        choices = sorted(mentat.const.REPORTING_INTERVALS_INV.items(), key = lambda x: x[0]),
        default = mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_LOW_REL]
    )
    timing_per_md = wtforms.SelectField(
        lazy_gettext('Reporting period:'),
        validators = [
            wtforms.validators.Optional(),
            check_defined_when_custom
        ],
        coerce = int,
        choices = [y for y in sorted(mentat.const.REPORTING_INTERVALS_INV.items(), key = lambda x: x[0]) if y[0] != 0],
        default = mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_MEDIUM_PER]
    )
    timing_thr_md = wtforms.SelectField(
        lazy_gettext('Reporting threshold:'),
        validators = [
            wtforms.validators.Optional(),
            check_defined_when_custom
        ],
        coerce = int,
        choices = sorted(mentat.const.REPORTING_INTERVALS_INV.items(), key = lambda x: x[0]),
        default = mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_MEDIUM_THR]
    )
    timing_rel_md = wtforms.SelectField(
        lazy_gettext('Reporting relapse:'),
        validators = [
            wtforms.validators.Optional(),
            check_defined_when_custom
        ],
        coerce = int,
        choices = sorted(mentat.const.REPORTING_INTERVALS_INV.items(), key = lambda x: x[0]),
        default = mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_MEDIUM_REL]
    )
    timing_per_hi = wtforms.SelectField(
        lazy_gettext('Reporting period:'),
        validators = [
            wtforms.validators.Optional(),
            check_defined_when_custom
        ],
        coerce = int,
        choices = [y for y in sorted(mentat.const.REPORTING_INTERVALS_INV.items(), key = lambda x: x[0]) if y[0] != 0],
        default = mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_HIGH_PER]
    )
    timing_thr_hi = wtforms.SelectField(
        lazy_gettext('Reporting threshold:'),
        validators = [
            wtforms.validators.Optional(),
            check_defined_when_custom
        ],
        coerce = int,
        choices = sorted(mentat.const.REPORTING_INTERVALS_INV.items(), key = lambda x: x[0]),
        default = mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_HIGH_THR]
    )
    timing_rel_hi = wtforms.SelectField(
        lazy_gettext('Reporting relapse:'),
        validators = [
            wtforms.validators.Optional(),
            check_defined_when_custom
        ],
        coerce = int,
        choices = sorted(mentat.const.REPORTING_INTERVALS_INV.items(), key = lambda x: x[0]),
        default = mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_HIGH_REL]
    )
    timing_per_cr = wtforms.SelectField(
        lazy_gettext('Reporting period:'),
        validators = [
            wtforms.validators.Optional(),
            check_defined_when_custom
        ],
        coerce = int,
        choices = [y for y in sorted(mentat.const.REPORTING_INTERVALS_INV.items(), key = lambda x: x[0]) if y[0] != 0],
        default = mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_CRITICAL_PER]
    )
    timing_thr_cr = wtforms.SelectField(
        lazy_gettext('Reporting threshold:'),
        validators = [
            wtforms.validators.Optional(),
            check_defined_when_custom
        ],
        coerce = int,
        choices = sorted(mentat.const.REPORTING_INTERVALS_INV.items(), key = lambda x: x[0]),
        default = mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_CRITICAL_THR]
    )
    timing_rel_cr = wtforms.SelectField(
        lazy_gettext('Reporting relapse:'),
        validators = [
            wtforms.validators.Optional(),
            check_defined_when_custom
        ],
        coerce = int,
        choices = sorted(mentat.const.REPORTING_INTERVALS_INV.items(), key = lambda x: x[0]),
        default = mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_CRITICAL_REL]
    )
    submit = wtforms.SubmitField(
        lazy_gettext('Submit')
    )
    cancel = wtforms.SubmitField(
        lazy_gettext('Cancel')
    )

class CreateSettingsReportingForm(BaseSettingsReportingForm):
    """
    Class representing reporting settings create form.
    """
    group = QuerySelectField(
        lazy_gettext('Group:'),
        query_factory = get_available_groups,
        allow_blank = False
    )

class UpdateSettingsReportingForm(BaseSettingsReportingForm):
    """
    Class representing reporting settings update form.
    """
