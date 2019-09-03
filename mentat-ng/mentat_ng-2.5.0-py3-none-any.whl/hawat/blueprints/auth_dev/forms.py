#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains custom developer login form for Hawat.
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


#
# Flask related modules.
#
import wtforms
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
import flask_wtf
from flask_babel import lazy_gettext

#
# Custom modules.
#
from mentat.datatype.sqldb import UserModel, GroupModel

import hawat.db
from hawat.blueprints.users.forms import check_id_existence, BaseUserAccountForm


def get_available_groups():
    """
    Query the database for list of all available groups.
    """
    return hawat.db.db_query(GroupModel).order_by(GroupModel.name).all()


class LoginForm(flask_wtf.FlaskForm):
    """
    Class representing developer authentication login form. This form provides
    list of all currently existing user accounts in simple selectbox, so that
    the developer can quickly login as different user.
    """
    login  = wtforms.SelectField(
        lazy_gettext('User account:'),
        validators = [
            wtforms.validators.DataRequired()
        ]
    )
    submit = wtforms.SubmitField(
        lazy_gettext('Login')
    )
    cancel = wtforms.SubmitField(
        lazy_gettext('Cancel')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_choices()

    def set_choices(self):
        """
        Load list of all user accounts and populate the ``choices`` attribute of
        the ``login`` selectbox.
        """
        dbsess = hawat.db.db_get().session
        users = dbsess.query(UserModel).order_by(UserModel.login).all()

        choices = []
        for usr in users:
            choices.append((usr.login, "{} ({}, #{})".format(usr.fullname, usr.login, usr.id)))
        choices = sorted(choices, key=lambda x: x[1])
        self.login.choices = choices


class RegisterUserAccountForm(BaseUserAccountForm):
    """
    Class representing user account registration form.
    """
    login = wtforms.StringField(
        lazy_gettext('Login:'),
        validators = [
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min = 3, max = 50),
            hawat.forms.check_login,
            check_id_existence
        ]
    )
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
