#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains very thin database abstraction layer and access functions for
Hawat. It is a wrapper around `SQLAlchemy <http://www.sqlalchemy.org/>`__ library.
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import os

#
# Flask related modules.
#
import click
import flask
from flask.cli import AppGroup
import flask_babel
import flask_login
from babel import Locale


import pyzenkit.utils
import hawat.const


BABEL = flask_babel.Babel()
@BABEL.localeselector
def get_locale():  # pylint: disable=locally-disabled,unused-variable
    """
    Implementation of locale selector for :py:mod:`flask_babel`.
    """
    # If a user is logged in, try to use the locale from the user settings.
    if flask_login.current_user.is_authenticated:
        if hasattr(flask_login.current_user, 'locale') and flask_login.current_user.locale:
            flask.session['locale'] = flask_login.current_user.locale

    # Store the best locale selection into the session.
    if 'locale' not in flask.session or not flask.session['locale']:
        flask.session['locale'] = flask.request.accept_languages.best_match(
            flask.current_app.config['SUPPORTED_LOCALES'].keys()
        )

    if 'locale' in flask.session and flask.session['locale']:
        return flask.session['locale']
    return flask.current_app.config['BABEL_DEFAULT_LOCALE']

@BABEL.timezoneselector
def get_timezone():  # pylint: disable=locally-disabled,unused-variable
    """
    Implementation of timezone selector for :py:mod:`flask_babel`.
    """
    # If a user is logged in, try to use the timezone from the user settings.
    if flask_login.current_user.is_authenticated:
        if hasattr(flask_login.current_user, 'timezone') and flask_login.current_user.timezone:
            flask.session['timezone'] = flask_login.current_user.timezone

    # Store the default timezone selection into the session.
    if 'timezone' not in flask.session or not flask.session['timezone']:
        flask.session['timezone'] = flask.current_app.config['BABEL_DEFAULT_TIMEZONE']

    return flask.session['timezone']


def babel_format_bytes(size, unit = 'B', step_size = 1024):
    """
    Format given numeric value to human readable string describing size in
    B/KB/MB/GB/TB.

    :param int size: Number to be formatted.
    :param enum unit: Starting unit, possible values are ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB'].
    :param int step_size: Size of the step between units.
    :return: Formatted and localized string.
    :rtype: string
    """
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
    idx_max = len(units) - 1
    unit = unit.upper()
    for idx, val in enumerate(units):
        # Skip the last step, there is no next unit defined after exabyte.
        if idx == idx_max:
            break
        if size > step_size:
            if unit == val:
                size = size / step_size
                unit = units[idx+1]
        else:
            break
    return '{} {}'.format(
        flask_babel.format_decimal(size),
        unit
    )

def babel_translate_locale(locale_id, with_current = False):
    """
    Translate given locale language. By default return language in locale`s
    language. Optionaly return language in given locale`s language.
    """
    locale_obj = Locale.parse(locale_id)
    if not with_current:
        return locale_obj.language_name
    return locale_obj.get_language_name(flask_babel.get_locale())

def babel_language_in_locale(locale_id = 'en'):
    """
    Translate given locale language. By default return language in locale`s
    language. Optionaly return language in given locale`s language.
    """
    locale_obj = Locale.parse(flask_babel.get_locale())
    return locale_obj.get_language_name(locale_id)


#-------------------------------------------------------------------------------


TRANSLATIONS_ROOT = os.path.relpath(os.path.dirname(__file__))
TRANSLATIONS_CFG  = os.path.join(TRANSLATIONS_ROOT, 'babel.cfg')
TRANSLATIONS_POT  = os.path.join(TRANSLATIONS_ROOT, 'messages.pot')
TRANSLATIONS_DIR  = os.path.join(TRANSLATIONS_ROOT, 'translations')

CMD_BABEL_EXTRACT = 'pybabel extract -F {} -o {} -k lazy_gettext -k tr_ {}'.format(
    TRANSLATIONS_CFG,
    TRANSLATIONS_POT,
    TRANSLATIONS_ROOT
)
CMD_BABEL_UPDATE = 'pybabel update -i {} -d {}'.format(
    TRANSLATIONS_POT,
    TRANSLATIONS_DIR,
)
CMD_BABEL_COMPILE = 'pybabel compile -d {}'.format(
    TRANSLATIONS_DIR
)
CMD_BABEL_INIT = 'pybabel init -i {} -d {} -l {{}}'.format(
    TRANSLATIONS_POT,
    TRANSLATIONS_DIR,
)


WINTL_CLI = AppGroup('webintl', help = "Web interface translation module.")


@WINTL_CLI.command('update')
def intl_update():
    """Update all existing translation message catalogs."""
    _extract()
    _update()
    _clean()


@WINTL_CLI.command('compile')
def intl_compile():
    """Compile all existing message translation catalogs."""
    _compile()


def validate_lang(ctx, param, value):
    """Validate ``login/email`` command line parameter."""
    if value:
        if hawat.const.CRE_LANG_CODE.match(value):
            return value
        raise click.BadParameter(
            "Value '{}' does not look like valid language code.".format(value)
        )
    return value

@WINTL_CLI.command()
@click.argument('lang', callback = validate_lang)
def init(lang):
    """Initialize a new language translation."""
    _extract()
    _init(lang)
    _clean()


def _extract():
    click.secho("\n***Extracting web interface translations ***\n", fg = 'yellow')
    click.echo("$ {}\n".format(CMD_BABEL_EXTRACT))
    if os.system(CMD_BABEL_EXTRACT):
        raise RuntimeError('pybabel extract command failed')
    click.secho("[OK] Successfully extracted translations", fg = 'green')

def _update():
    click.secho("\n*** Updating all web interface message translation catalogs ***\n", fg = 'yellow')
    click.echo("$ {}\n".format(CMD_BABEL_UPDATE))
    if os.system(CMD_BABEL_UPDATE):
        raise RuntimeError('pybabel update command failed')
    click.secho("[OK] Successfully updated all message translation catalogs", fg = 'green')

def _compile():
    click.secho("\n*** Compiling all web interface message translation catalogs ***\n", fg = 'yellow')
    click.echo("$ {}\n".format(CMD_BABEL_COMPILE))
    if os.system(CMD_BABEL_COMPILE):
        raise RuntimeError('pybabel compile command failed')
    click.secho("[OK] Successfully compiled all message translation catalogs", fg = 'green')

def _init(lang):
    click.secho("\n*** Initializing new web interface translation ***\n", fg = 'yellow')
    click.echo("Locale name: {}\n".format(lang))
    click.echo("$ {}\n".format(CMD_BABEL_INIT.format(lang)))
    if os.system(CMD_BABEL_INIT.format(lang)):
        raise RuntimeError('pybabel init command failed')
    click.secho(
        "[OK] Successfully initialized translations for '{}' language.".format(lang),
        fg = 'green'
    )

def _clean():
    os.remove(TRANSLATIONS_POT)


#-------------------------------------------------------------------------------


RINTL_CLI   = AppGroup('repintl', help = "Reporting translation module.")
RINTL_COMPS = ('informant', 'reporter')

@RINTL_CLI.command('update')
def rintl_update():
    """Update all existing reporting translation message catalogs."""
    _rep_extract()
    _rep_update()
    _rep_clean()


@RINTL_CLI.command('compile')
def rintl_compile():
    """Compile all existing reporting message translation catalogs."""
    _rep_compile()

@RINTL_CLI.command()
@click.argument('lang', callback = validate_lang)
def rinit(lang):
    """Initialize a new reporting language translation."""
    _rep_extract()
    _rep_init(lang)
    _rep_clean()


def _rep_extract():
    click.secho("\n***Extracting reporting translations ***\n", fg = 'yellow')
    for component in RINTL_COMPS:
        cmd = _get_cmd_rep_extract(component)
        click.echo("$ {}\n".format(cmd))
        if os.system(cmd):
            raise RuntimeError('pybabel extract command failed')
    click.secho(
        "[OK] Successfully extracted translations",
        fg = 'green'
    )

def _rep_update():
    click.secho("\n*** Updating all reporting message translation catalogs ***\n", fg = 'yellow')
    for component in RINTL_COMPS:
        cmd = _get_cmd_rep_update(component)
        click.echo("$ {}\n".format(cmd))
        if os.system(cmd):
            raise RuntimeError('pybabel update command failed')
    click.secho(
        "[OK] Successfully updated all message translation catalogs",
        fg = 'green'
    )

def _rep_compile():
    click.secho("\n*** Compiling all reporting message translation catalogs ***\n", fg = 'yellow')
    for component in RINTL_COMPS:
        cmd = _get_cmd_rep_compile(component)
        click.echo("$ {}\n".format(cmd))
        if os.system(cmd):
            raise RuntimeError('pybabel compile command failed')
    click.secho(
        "[OK] Successfully compiled all message translation catalogs",
        fg = 'green'
    )

def _rep_init(lang):
    click.secho("\n*** Initializing new reporting translation ***\n", fg = 'yellow')
    click.echo("Locale name: {}\n".format(lang))
    for component in RINTL_COMPS:
        cmd = _get_cmd_rep_init(component, lang)
        click.echo("$ {}\n".format(cmd))
        if os.system(cmd):
            raise RuntimeError('pybabel init command failed')
    click.secho(
        "[OK] Successfully initialized translations for '{}' language.".format(lang),
        fg = 'green'
    )

def _rep_clean():
    for component in RINTL_COMPS:
        os.remove(
            os.path.join(
                '/etc/mentat/templates',
                component,
                'messages.pot'
            )
        )

# ---

def _get_cmd_rep_extract(component):
    return 'pybabel extract -F {} -o {} -k lazy_gettext -k tr_ --no-location {} /var/mentat/venv/lib/python3.5/site-packages'.format(
        os.path.join(
            '/etc/mentat/templates',
            component,
            'babel-venv.cfg'
        ),
        os.path.join(
            '/etc/mentat/templates',
            component,
            'messages.pot'
        ),
        os.path.join(
            '/etc/mentat/templates',
            component
        )
    )

def _get_cmd_rep_update(component):
    return 'pybabel update -i {} -d {}'.format(
        os.path.join(
            '/etc/mentat/templates',
            component,
            'messages.pot'
        ),
        os.path.join(
            '/etc/mentat/templates',
            component,
            'translations'
        )
    )

def _get_cmd_rep_compile(component):
    return 'pybabel compile -d {}'.format(
        os.path.join(
            '/etc/mentat/templates',
            component,
            'translations'
        )
    )

def _get_cmd_rep_init(component, lang):
    return 'pybabel init -i {} -d {} -l {}'.format(
        os.path.join(
            '/etc/mentat/templates',
            component,
            'messages.pot'
        ),
        os.path.join(
            '/etc/mentat/templates',
            component,
            'translations'
        ),
        lang
    )
