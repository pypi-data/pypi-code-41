#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains couple of simple helpers for working with IDEA messages.
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import os

#
# Flask related modules.
#
import flask

#
# Custom modules.
#
import pyzenkit.jsonconf
import hawat.const
import mentat.services.eventstorage


_DB = None


def get_event_source_types():
    """
    Return list of all available event source types.
    """
    cache_dir = flask.current_app.config.get(hawat.const.CFGKEY_MENTAT_CACHE_DIR)
    return pyzenkit.jsonconf.json_load(os.path.join(cache_dir, 'itemset-stat-sourcetypes.json'))


def get_event_target_types():
    """
    Return list of all available event target types.
    """
    cache_dir = flask.current_app.config.get(hawat.const.CFGKEY_MENTAT_CACHE_DIR)
    return pyzenkit.jsonconf.json_load(os.path.join(cache_dir, 'itemset-stat-targettypes.json'))


def get_event_detector_types():
    """
    Return list of all available event detector types.
    """
    cache_dir = flask.current_app.config.get(hawat.const.CFGKEY_MENTAT_CACHE_DIR)
    return pyzenkit.jsonconf.json_load(os.path.join(cache_dir, 'itemset-stat-detectortypes.json'))


def get_event_detectors():
    """
    Return list of all available event detectors.
    """
    cache_dir = flask.current_app.config.get(hawat.const.CFGKEY_MENTAT_CACHE_DIR)
    return pyzenkit.jsonconf.json_load(os.path.join(cache_dir, 'itemset-stat-detectors.json'))


def get_event_categories():
    """
    Return list of all available event categories.
    """
    cache_dir = flask.current_app.config.get(hawat.const.CFGKEY_MENTAT_CACHE_DIR)
    return pyzenkit.jsonconf.json_load(os.path.join(cache_dir, 'itemset-stat-categories.json'))

def get_event_severities():
    """
    Return list of all available event severities.
    """
    cache_dir = flask.current_app.config.get(hawat.const.CFGKEY_MENTAT_CACHE_DIR)
    return pyzenkit.jsonconf.json_load(os.path.join(cache_dir, 'itemset-stat-severities.json'))

def get_event_classes():
    """
    Return list of all available event classes.
    """
    cache_dir = flask.current_app.config.get(hawat.const.CFGKEY_MENTAT_CACHE_DIR)
    return pyzenkit.jsonconf.json_load(os.path.join(cache_dir, 'itemset-stat-classes.json'))

def get_event_protocols():
    """
    Return list of all available event protocols.
    """
    cache_dir = flask.current_app.config.get(hawat.const.CFGKEY_MENTAT_CACHE_DIR)
    return pyzenkit.jsonconf.json_load(os.path.join(cache_dir, 'itemset-stat-protocols.json'))

def get_event_inspection_errs():
    """
    Return list of all available event inspection errors.
    """
    cache_dir = flask.current_app.config.get(hawat.const.CFGKEY_MENTAT_CACHE_DIR)
    return pyzenkit.jsonconf.json_load(os.path.join(cache_dir, 'itemset-stat-inspectionerrors.json'))

def db_settings(app):
    """
    Return database settings from Mentat core configurations.

    :return: Database settings.
    :rtype: dict
    """
    return app.mconfig


def db_init(app):
    """
    Initialize connection to event database.
    """
    mentat.services.eventstorage.init(db_settings(app))
    app.eventdb = mentat.services.eventstorage.service()


def db_get():
    """
    Opens a new database connection if there is none yet for the
    current application context.

    :return: Database storage handler.
    :rtype: flask_sqlalchemy.SQLAlchemy
    """
    return mentat.services.eventstorage.service()


def db_cursor():
    """
    Convenience method.
    """
    return db_get().session
