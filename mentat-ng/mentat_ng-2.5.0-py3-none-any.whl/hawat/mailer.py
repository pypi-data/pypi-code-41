#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------

"""
This module contains mailing functions for Hawat application. They are built on
top of :py:mod:`flask_mail` extension.
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


import flask_mail


MAILER = flask_mail.Mail()
"""Global application resource: :py:mod:`flask_mail` mailer."""

def on_email_sent(message, app):
    """
    Signal handler for handling :py:func:`flask_mail.email_dispatched` signal.
    Log subject and recipients of all email that have been sent.
    """
    app.logger.info(
        "Sent email '%s' to '%s'",
        message.subject,
        ', '.join(message.recipients)
    )
flask_mail.email_dispatched.connect(on_email_sent)
