#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
Description
-----------

This pluggable module provides access to database status information. The
following information is provided:

* general statistics of event database:

  * general statistics of *events* table

    * estimated number of records
    * table size, index size, tablespace size and total size
    * oldest and youngest record timestamp, record timespan

  * general statistics of *event_thresholds* table

    * estimated number of records
    * table size, index size, tablespace size and total size
    * oldest and youngest record timestamp, record timespan

  * general statistics of *thresholds* table

    * estimated number of records
    * table size, index size, tablespace size and total size
    * oldest and youngest record timestamp, record timespan

* PostgreSQL configurations


Provided endpoints
------------------

``/dbstatus/view``
    Page providing read-only access various database status characteristics.

    *Authentication:* login required
    *Authorization:* ``admin`` role only
    *Methods:* ``GET``

"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime

#
# Flask related modules.
#
from flask_babel import lazy_gettext
from sqlalchemy import or_

#
# Custom modules.
#
import mentat.const
import mentat.system
from mentat.datatype.sqldb import UserModel, GroupModel, FilterModel, SettingsReportingModel

import hawat.menu
import hawat.acl
import hawat.events
from hawat.base import SimpleView, SQLAlchemyMixin, HTMLMixin, HawatBlueprint


BLUEPRINT_NAME = 'dbstatus'
"""Name of the blueprint as module global constant."""


class ViewView(HTMLMixin, SimpleView):
    """
    Application view providing access event database status information.
    """
    authentication = True

    authorization = [hawat.acl.PERMISSION_ADMIN]

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'view'

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'module-{}'.format(BLUEPRINT_NAME)

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Database status')

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Database status')

    def do_before_response(self, **kwargs):
        """*Implementation* of :py:func:`hawat.base.RenderableView.do_before_response`."""
        self.response_context.update(
            database_status_events = hawat.events.db_get().database_status(),
            sw_versions = mentat.system.analyze_versions()
        )

        dbstatistics_events = {
            'total_bytes': {
                x: y['total_bytes'] for x, y in self.response_context['database_status_events']['tables'].items()
            },
            'table_bytes': {
                x: y['table_bytes'] for x, y in self.response_context['database_status_events']['tables'].items()
            },
            'index_bytes': {
                x: y['index_bytes'] for x, y in self.response_context['database_status_events']['tables'].items()
            },
            'row_estimate': {
                x: y['row_estimate'] for x, y in self.response_context['database_status_events']['tables'].items()
            }
        }
        self.response_context.update(
            database_statistics_events = dbstatistics_events
        )


class DashboardView(HTMLMixin, SQLAlchemyMixin, SimpleView):  # pylint: disable=locally-disabled,abstract-method
    """
    View responsible for presenting database dashboard.
    """
    authentication = True

    authorization = [hawat.acl.PERMISSION_ADMIN]

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'dashboard'

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Object management')

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Object management dashboards')

    @classmethod
    def get_view_template(cls):
        """*Implementation* of :py:func:`hawat.base.RenderableView.get_view_template`."""
        return '{}/dashboard.html'.format(cls.module_name)

    #---------------------------------------------------------------------------


    def do_before_response(self, **kwargs):
        """*Implementation* of :py:func:`hawat.base.RenderableView.do_before_response`."""
        self.response_context['users_disabled'] = self.dbquery(UserModel).\
            filter(UserModel.enabled == False).\
            order_by(UserModel.createtime.desc()).\
            all()
        self.response_context['users_nomemberships'] = self.dbquery(UserModel).\
            filter(~UserModel.memberships.any()).\
            order_by(UserModel.createtime.desc()).\
            all()
        self.response_context['users_noroles'] = self.dbquery(UserModel).\
            filter(UserModel.roles == []).\
            order_by(UserModel.createtime.desc()).\
            all()
        self.response_context['users_nologin'] = self.dbquery(UserModel).\
            filter(
                or_(
                    UserModel.logintime.is_(None),
                    UserModel.logintime <= (datetime.datetime.utcnow() - datetime.timedelta(days = 365))
                )
            ).\
            order_by(UserModel.createtime.desc()).\
            all()

        self.response_context['groups_disabled'] = self.dbquery(GroupModel).\
            filter(GroupModel.enabled == False).\
            order_by(GroupModel.createtime.desc()).\
            all()
        self.response_context['groups_nomembers'] = self.dbquery(GroupModel).\
            filter(~GroupModel.members.any()).\
            order_by(GroupModel.createtime.desc()).\
            all()
        self.response_context['groups_nomanagers'] = self.dbquery(GroupModel).\
            filter(~GroupModel.members.any()).\
            order_by(GroupModel.createtime.desc()).\
            all()
        self.response_context['groups_nonetworks'] = self.dbquery(GroupModel).\
            filter(~GroupModel.networks.any()).\
            order_by(GroupModel.createtime.desc()).\
            all()

        self.response_context['filters_disabled'] = self.dbquery(FilterModel).\
            filter(FilterModel.enabled == False).\
            order_by(FilterModel.createtime.desc()).\
            all()
        self.response_context['filters_nohits'] = self.dbquery(FilterModel).\
            filter(FilterModel.hits == 0).\
            order_by(FilterModel.createtime.desc()).\
            all()
        self.response_context['filters_future'] = self.dbquery(FilterModel).\
            filter(FilterModel.valid_from > (datetime.datetime.utcnow() + datetime.timedelta(days = 14))).\
            order_by(FilterModel.createtime.desc()).\
            all()
        self.response_context['filters_expired'] = self.dbquery(FilterModel).\
            filter(FilterModel.valid_to < datetime.datetime.utcnow()).\
            order_by(FilterModel.createtime.desc()).\
            all()

        self.response_context['settingsrep_muted'] = self.dbquery(SettingsReportingModel).\
            filter(SettingsReportingModel.mute == True).\
            order_by(SettingsReportingModel.createtime.desc()).\
            all()
        self.response_context['settingsrep_redirected'] = self.dbquery(SettingsReportingModel).\
            filter(SettingsReportingModel.redirect == True).\
            order_by(SettingsReportingModel.createtime.desc()).\
            all()
        self.response_context['settingsrep_modenone'] = self.dbquery(SettingsReportingModel).\
            filter(SettingsReportingModel.mode == mentat.const.REPORTING_MODE_NONE).\
            order_by(SettingsReportingModel.createtime.desc()).\
            all()
        self.response_context['settingsrep_attachcsv'] = self.dbquery(SettingsReportingModel).\
            filter(SettingsReportingModel.attachments.in_([mentat.const.REPORTING_ATTACH_CSV, mentat.const.REPORTING_ATTACH_ALL])).\
            order_by(SettingsReportingModel.createtime.desc()).\
            all()
        self.response_context['settingsrep_emailscust'] = self.dbquery(SettingsReportingModel).\
            filter(SettingsReportingModel.emails != []).\
            order_by(SettingsReportingModel.createtime.desc()).\
            all()
        self.response_context['settingsrep_timingcust'] = self.dbquery(SettingsReportingModel).\
            filter(SettingsReportingModel.timing == mentat.const.REPORTING_TIMING_CUSTOM).\
            order_by(SettingsReportingModel.createtime.desc()).\
            all()

        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            'endpoint',
            'show',
            endpoint = 'users.show',
            hidetitle = True,
            legend = lambda **x: lazy_gettext('View details of user account &quot;%(item)s&quot;', item = x['item'].login)
        )
        action_menu.add_entry(
            'submenu',
            'more',
            legend = lazy_gettext('More actions')
        )
        action_menu.add_entry(
            'endpoint',
            'more.update',
            endpoint = 'users.update',
            legend = lambda **x: lazy_gettext('Update details of user account &quot;%(item)s&quot;', item = x['item'].login)
        )
        action_menu.add_entry(
            'endpoint',
            'more.disable',
            endpoint = 'users.disable',
            icon = 'action-disable-user',
            legend = lambda **x: lazy_gettext('Disable user account &quot;%(item)s&quot;', item = x['item'].login)
        )
        action_menu.add_entry(
            'endpoint',
            'more.enable',
            endpoint = 'users.enable',
            icon = 'action-enable-user',
            legend = lambda **x: lazy_gettext('Enable user account &quot;%(item)s&quot;', item = x['item'].login)
        )
        action_menu.add_entry(
            'endpoint',
            'more.delete',
            endpoint = 'users.delete',
            icon = 'action-delete-user',
            legend = lambda **x: lazy_gettext('Delete user account &quot;%(item)s&quot;', item = x['item'].login)
        )
        self.response_context['context_action_menu_user'] = action_menu

        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            'endpoint',
            'show',
            endpoint = 'groups.show',
            hidetitle = True,
            legend = lambda **x: lazy_gettext('View details of group &quot;%(item)s&quot;', item = str(x['item']))
        )
        action_menu.add_entry(
            'submenu',
            'more',
            legend = lazy_gettext('More actions')
        )
        action_menu.add_entry(
            'endpoint',
            'more.update',
            endpoint = 'groups.update',
            legend = lambda **x: lazy_gettext('Update details of group &quot;%(item)s&quot;', item = str(x['item']))
        )
        action_menu.add_entry(
            'endpoint',
            'more.disable',
            endpoint = 'groups.disable',
            legend = lambda **x: lazy_gettext('Disable group &quot;%(item)s&quot;', item = str(x['item']))
        )
        action_menu.add_entry(
            'endpoint',
            'more.enable',
            endpoint = 'groups.enable',
            legend = lambda **x: lazy_gettext('Enable group &quot;%(item)s&quot;', item = str(x['item']))
        )
        action_menu.add_entry(
            'endpoint',
            'more.delete',
            endpoint = 'groups.delete',
            legend = lambda **x: lazy_gettext('Delete group &quot;%(item)s&quot;', item = str(x['item']))
        )
        self.response_context['context_action_menu_group'] = action_menu

        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            'endpoint',
            'show',
            endpoint = 'filters.show',
            hidetitle = True,
            legend = lambda **x: lazy_gettext('View details of reporting filter &quot;%(item)s&quot;', item = x['item'].name)
        )
        action_menu.add_entry(
            'submenu',
            'more',
            legend = lazy_gettext('More actions')
        )
        action_menu.add_entry(
            'endpoint',
            'more.update',
            endpoint = 'filters.update',
            legend = lambda **x: lazy_gettext('Update details of reporting filter &quot;%(item)s&quot;', item = x['item'].name)
        )
        action_menu.add_entry(
            'endpoint',
            'more.disable',
            endpoint = 'filters.disable',
            legend = lambda **x: lazy_gettext('Disable reporting filter &quot;%(item)s&quot;', item = x['item'].name)
        )
        action_menu.add_entry(
            'endpoint',
            'more.enable',
            endpoint = 'filters.enable',
            legend = lambda **x: lazy_gettext('Enable reporting filter &quot;%(item)s&quot;', item = x['item'].name)
        )
        action_menu.add_entry(
            'endpoint',
            'more.delete',
            endpoint = 'filters.delete',
            legend = lambda **x: lazy_gettext('Delete reporting filter &quot;%(item)s&quot;', item = x['item'].name)
        )
        self.response_context['context_action_menu_filter'] = action_menu


#-------------------------------------------------------------------------------


class DatabaseStatusBlueprint(HawatBlueprint):
    """
    Hawat pluggable module - database status.
    """

    @classmethod
    def get_module_title(cls):
        """*Implementation* of :py:func:`hawat.base.HawatBlueprint.get_module_title`."""
        return lazy_gettext('Database status overview pluggable module')

    def register_app(self, app):
        """
        *Callback method*. Will be called from :py:func:`hawat.base.HawatApp.register_blueprint`
        method and can be used to customize the Flask application object. Possible
        use cases:

        * application menu customization

        :param hawat.base.HawatApp app: Flask application to be customize.
        """
        app.menu_main.add_entry(
            'view',
            'dashboards.dbstatus',
            position = 100,
            view = DashboardView
        )
        app.menu_main.add_entry(
            'view',
            'admin.{}'.format(BLUEPRINT_NAME),
            position = 30,
            view = ViewView
        )


#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`hawat.base.HawatBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = DatabaseStatusBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates',
        url_prefix = '/{}'.format(BLUEPRINT_NAME)
    )

    hbp.register_view_class(ViewView, '/view')
    hbp.register_view_class(DashboardView, '/dashboard')

    return hbp
