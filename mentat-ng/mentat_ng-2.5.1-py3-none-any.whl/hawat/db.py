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


#
# Flask related modules.
#
import flask_sqlalchemy

#
# Custom modules.
#
import mentat.datatype.sqldb
import mentat.services.sqlstorage
from mentat.const import CKEY_CORE_DATABASE, CKEY_CORE_DATABASE_SQLSTORAGE
from hawat.const import CFGKEY_MENTAT_CORE


_DB = None


def db_settings(app):
    """
    Return database settings from Mentat core configurations.

    :return: Database settings.
    :rtype: dict
    """
    return app.config[CFGKEY_MENTAT_CORE][CKEY_CORE_DATABASE][CKEY_CORE_DATABASE_SQLSTORAGE]


def db_get():
    """
    Opens a new database connection if there is none yet for the
    current application context.

    :return: Database storage handler.
    :rtype: flask_sqlalchemy.SQLAlchemy
    """
    global _DB  # pylint: disable=locally-disabled,global-statement
    if not _DB:
        _DB = flask_sqlalchemy.SQLAlchemy(
            metadata    = mentat.datatype.sqldb.MODEL.metadata,
            model_class = mentat.datatype.sqldb.MODEL,
            query_class = mentat.services.sqlstorage.RetryingQuery
        )
        mentat.services.sqlstorage.set_manager(StorageServiceManager())

    return _DB


def db_session():
    """
    Convenience method.
    """
    return db_get().session


def db_query(dbmodel):
    """
    Convenience method.
    """
    return db_get().session.query(dbmodel)


class StorageService:  # pylint: disable=locally-disabled,too-few-public-methods
    """
    This is a thin proxy class, that can be used in place of :py:class:`mentat.services.sqlstorage.StorageService`.
    This is necessary for certain services like :py:mod:`mentat.services.whois`, that require
    some access to database storage service and are hardcoded to use :py:class:`mentat.services.sqlstorage.StorageService`.
    This is necessary when using the services from Flask framework, because there
    is another storage service management feature in place using the py:mod:`flask_sqlalchemy`
    module.
    """
    @property
    def session(self):
        """
        Thin proxy property for retrieving reference to current database session.
        """
        return db_session()


class StorageServiceManager:  # pylint: disable=locally-disabled,too-few-public-methods
    """
    This is a thin proxy class, that can be used in place of :py:class:`mentat.services.sqlstorage.StorageServiceManager`.
    This is necessary for certain services like :py:mod:`mentat.services.whois`, that require
    some access to database storage service manager and are hardcoded to use :py:class:`mentat.services.sqlstorage.StorageServiceManager`.
    This is necessary when using the services from Flask framework, because there
    is another storage service management feature in place using the py:mod:`flask_sqlalchemy`
    module.
    """
    @staticmethod
    def service():
        """
        Thin proxy property for retrieving reference to current database storage
        service.
        """
        return StorageService()
