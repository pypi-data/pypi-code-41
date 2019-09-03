#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains default configurations for Hawat application. One of the
classes defined in this module may be passed as argument to :py:func:`hawat.app.create_app_full`
factory function to bootstrap Hawat default configurations. These values may be
then optionally overwritten by external configuration file and/or additional
configuration file defined indirrectly via environment variable. Please refer to
the documentation of :py:func:`hawat.app.create_app_full` factory function for more
details on this process.

There are following predefined configuration classess available:

:py:class:`hawat.config.ProductionConfig`
    Default configuration suite for production environments.

:py:class:`hawat.config.DevelopmentConfig`
    Default configuration suite for development environments.

:py:class:`hawat.config.TestingConfig`
    Default configuration suite for testing environments.

There is also following constant structure containing mapping of simple configuration
names to configuration classess:

:py:const:`CONFIG_MAP`

It is used from inside of :py:func:`hawat.app.create_app` factory method to pick
and apply correct configuration class to application. Please refer to the documentation
of :py:func:`hawat.app.create_app` factory function for more details on this process.
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import os
import socket
import collections

#
# Flask related modules.
#
from flask_babel import lazy_gettext

#
# Custom modules.
#
import pyzenkit.jsonconf
import pyzenkit.utils

import mentat.const
import hawat.const


class Config:  # pylint: disable=locally-disabled,too-few-public-methods
    """
    Base class for default configurations of Hawat application. You are free to
    extend and customize contents of this class to provide better default values
    for your particular environment.

    The configuration keys must be a valid Flask configuration and so they must
    be written in UPPERCASE to be correctly recognized.
    """

    #---------------------------------------------------------------------------
    # Flask internal configurations. Please refer to Flask documentation for
    # more information about each configuration key.
    #---------------------------------------------------------------------------

    DEBUG      = False
    TESTING    = False
    SECRET_KEY = 'default-secret-key'

    #---------------------------------------------------------------------------
    # Flask extension configurations. Please refer to the documentation of that
    # particular Flask extension for more details.
    #---------------------------------------------------------------------------

    #
    # Flask-WTF configurations.
    #
    WTF_CSRF_ENABLED = True

    #
    # Flask-Mail configurations.
    #
    MAIL_SERVER         = 'localhost'
    MAIL_PORT           = 25
    MAIL_USERNAME       = None
    MAIL_PASSWORD       = None
    MAIL_DEFAULT_SENDER = 'mentat@{}'.format(socket.getfqdn())
    MAIL_SUBJECT_PREFIX = '[Mentat]'

    #
    # Flask-Babel configurations.
    #
    BABEL_DEFAULT_LOCALE   = hawat.const.HAWAT_DEFAULT_LOCALE
    BABEL_DEFAULT_TIMEZONE = hawat.const.HAWAT_DEFAULT_TIMEZONE

    #
    # Flask-SQLAlchemy configurations.
    # Note: do not put 'SQLALCHEMY_DATABASE_URI' and 'SQLALCHEMY_ECHO' here.
    # These will be overwritten with the values in Mentat core database configurations.
    #
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #---------------------------------------------------------------------------
    # Custom application configurations.
    #---------------------------------------------------------------------------

    ROLES = hawat.const.HAWAT_ROLES
    """List of all valid user roles supported by the application."""

    SUPPORTED_LOCALES = collections.OrderedDict([
        ('en', 'English'),
        ('cs', 'Česky')
    ])
    """List of all languages (locales) supported by the application."""

    ENABLED_BLUEPRINTS = [
        'hawat.blueprints.auth_api',
        'hawat.blueprints.auth_env',
        'hawat.blueprints.design',
        'hawat.blueprints.home',
        'hawat.blueprints.reports',
        'hawat.blueprints.events',
        'hawat.blueprints.hosts',
        'hawat.blueprints.timeline',
        'hawat.blueprints.dnsr',
        #'hawat.blueprints.pdnsr',
        'hawat.blueprints.geoip',
        #'hawat.blueprints.nerd',
        'hawat.blueprints.whois',
        'hawat.blueprints.performance',
        'hawat.blueprints.status',
        'hawat.blueprints.dbstatus',
        'hawat.blueprints.devtools',
        'hawat.blueprints.users',
        'hawat.blueprints.groups',
        'hawat.blueprints.settings_reporting',
        'hawat.blueprints.filters',
        'hawat.blueprints.networks',
        'hawat.blueprints.changelogs',
    ]
    """List of requested application blueprints to be loaded during setup."""

    DISABLED_ENDPOINTS = []
    """List of endpoints disabled on application level."""

    HAWAT_LOGIN_VIEW = 'auth_env.login'
    """
    Default login view. Users will be redirected to this view in case they are not
    authenticated, but the authentication is required for the requested endpoint.
    """

    HAWAT_LOGIN_MSGCAT = 'info'
    """Default message category for messages related to user authentication."""

    HAWAT_ENDPOINT_HOME = 'home.index'
    """Homepage endpoint."""

    HAWAT_LOGIN_REDIRECT = 'home.index'
    """Default redirection endpoint after login."""

    HAWAT_LOGOUT_REDIRECT = 'home.index'
    """Default redirection endpoint after logout."""

    HAWAT_MENU_SKELETON = [
        {
            'entry_type': 'submenu',
            'ident': 'dashboards',
            'position': 100,
            'title': lazy_gettext('Dashboards'),
            'resptitle': True,
            'icon': 'section-dashboards'
        },
        {
            'entry_type': 'submenu',
            'ident': 'more',
            'position': 200,
            'title': lazy_gettext('More'),
            'resptitle': True,
            'icon': 'section-more',
        },
        {
            'entry_type': 'submenu',
            'ident': 'admin',
            'position': 300,
            'authentication': True,
            'authorization': ['power'],
            'title': lazy_gettext('Administration'),
            'resptitle': True,
            'icon': 'section-administration'
        },
        {
            'entry_type': 'submenu',
            'ident': 'developer',
            'position': 400,
            'authentication': True,
            'authorization': ['developer'],
            'title': lazy_gettext('Development'),
            'resptitle': True,
            'icon': 'section-development'
        }
    ]
    """Configuration of application menu skeleton."""

    HAWAT_ADMINS = ['root@{}'.format(socket.getfqdn())]
    """List of system administrator emails."""

    HAWAT_REPORT_FEEDBACK_MAILS = ['root@{}'.format(socket.getfqdn())]
    """List of system administrator emails, that receive feedback messages for reports."""

    HAWAT_LOG_DEFAULT_LEVEL = 'info'
    """Default logging level, case insensitive. One of the values ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``."""

    HAWAT_LOG_FILE_LEVEL = 'info'
    """File logging level, case insensitive. One of the values ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``."""

    HAWAT_LOG_EMAIL_LEVEL = 'error'
    """File logging level, case insensitive. One of the values ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``."""

    HAWAT_LOCAL_DEVELOPER_LOGIN = 'account@local'
    """Developer account for local development login."""

    HAWAT_CHART_TIMELINE_MAXSTEPS = 200
    """Maximal number of steps (bars) displayed in timeline chart."""

    HAWAT_LIMIT_AODS = 10
    """Limit for number of objects for which to automatically fetch additional data services."""


class ProductionConfig(Config):  # pylint: disable=locally-disabled,too-few-public-methods
    """
    Class containing application configurations for *production* environment.
    """


class DevelopmentConfig(Config):  # pylint: disable=locally-disabled,too-few-public-methods
    """
    Class containing application configurations for *development* environment.
    """

    #---------------------------------------------------------------------------
    # Flask internal configurations. Please refer to Flask documentation for
    # more information about each configuration key.
    #---------------------------------------------------------------------------


    DEBUG = True
    """Overwrite default :py:const:`hawat.config.Config.DEBUG`."""

    #---------------------------------------------------------------------------
    # Custom application configurations.
    #---------------------------------------------------------------------------

    ENABLED_BLUEPRINTS = [
        'hawat.blueprints.auth_api',
        'hawat.blueprints.auth_dev',
        'hawat.blueprints.auth_env',
        'hawat.blueprints.design',
        'hawat.blueprints.home',
        'hawat.blueprints.reports',
        'hawat.blueprints.events',
        'hawat.blueprints.hosts',
        'hawat.blueprints.timeline',
        'hawat.blueprints.dnsr',
        #'hawat.blueprints.pdnsr',
        'hawat.blueprints.geoip',
        #'hawat.blueprints.nerd',
        'hawat.blueprints.whois',
        'hawat.blueprints.performance',
        'hawat.blueprints.status',
        'hawat.blueprints.dbstatus',
        'hawat.blueprints.devtools',
        'hawat.blueprints.users',
        'hawat.blueprints.groups',
        'hawat.blueprints.settings_reporting',
        'hawat.blueprints.filters',
        'hawat.blueprints.networks',
        'hawat.blueprints.changelogs',
    ]
    """Overwrite default :py:const:`hawat.config.Config.ENABLED_BLUEPRINTS`."""

    HAWAT_LOGIN_VIEW = 'auth_dev.login'
    """Overwrite default :py:const:`hawat.config.Config.HAWAT_LOGIN_VIEW`."""


class TestingConfig(Config):  # pylint: disable=locally-disabled,too-few-public-methods
    """
    Class containing *testing* Hawat applications` configurations.
    """

    #---------------------------------------------------------------------------
    # Flask internal configurations. Please refer to Flask documentation for
    # more information about each configuration key.
    #---------------------------------------------------------------------------


    TESTING = True
    """Overwrite default :py:const:`hawat.config.Config.TESTING`."""


CONFIG_MAP = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing':     TestingConfig,
    'default':     ProductionConfig
}
"""Configuration map for easy mapping of configuration aliases to config objects."""

def get_app_root_relative_config():
    """
    These configurations are relative to APP_ROOT_PATH environment setting and
    must be handled separately.
    """
    return {
        'MENTAT_CORE': pyzenkit.jsonconf.config_load_dir(
            pyzenkit.utils.get_resource_path(mentat.const.PATH_CFG_CORE)
        ),
        'MENTAT_PATHS': {
            'path_crn': pyzenkit.utils.get_resource_path(mentat.const.PATH_CRN),
            'path_cfg': pyzenkit.utils.get_resource_path(mentat.const.PATH_CFG),
            'path_var': pyzenkit.utils.get_resource_path(mentat.const.PATH_VAR),
            'path_log': pyzenkit.utils.get_resource_path(mentat.const.PATH_LOG),
            'path_run': pyzenkit.utils.get_resource_path(mentat.const.PATH_RUN),
            'path_tmp': pyzenkit.utils.get_resource_path(mentat.const.PATH_TMP),
        },
        'MENTAT_CACHE_DIR': pyzenkit.utils.get_resource_path(
            os.path.join(mentat.const.PATH_VAR, 'cache')
        ),
        'MENTAT_CONTROLLER_CFG': pyzenkit.utils.get_resource_path(
            os.path.join(mentat.const.PATH_CFG, 'mentat-controller.py.conf')
        ),
        'HAWAT_LOG_FILE': pyzenkit.utils.get_resource_path(
            os.path.join(mentat.const.PATH_LOG, 'mentat-hawat.py.log')
        )
    }

def get_default_config_file():
    return os.path.join(
        pyzenkit.utils.get_resource_path(mentat.const.PATH_CFG),
        'mentat-hawat.py.conf'
    )
