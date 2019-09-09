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

This pluggable module provides access to group reporting settings management features.
These features include:

* detailed reporting settings view
* creating new reporting settings
* updating existing reporting settings
* deleting existing reporting settings
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


#
# Flask related modules.
#
import flask
import flask_principal
from flask_babel import gettext, lazy_gettext

#
# Custom modules.
#
import mentat.reports.utils
from mentat.datatype.sqldb import SettingsReportingModel, ItemChangeLogModel

import hawat.db
from hawat.base import HTMLMixin, SQLAlchemyMixin, ItemShowView,\
    ItemCreateView, ItemUpdateView, HawatBlueprint
from hawat.blueprints.settings_reporting.forms import CreateSettingsReportingForm,\
    UpdateSettingsReportingForm


BLUEPRINT_NAME = 'settings_reporting'
"""Name of the blueprint as module global constant."""


class ShowView(HTMLMixin, SQLAlchemyMixin, ItemShowView):
    """
    Detailed reporting settings view.
    """
    methods = ['GET']

    authentication = True

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'module-settings-reporting'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Show reporting settings')

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return SettingsReportingModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        """
        Perform access authorization for current user to particular item.
        """
        permission_mm = flask_principal.Permission(
            hawat.acl.MembershipNeed(kwargs['item'].group.id),
            hawat.acl.ManagementNeed(kwargs['item'].group.id)
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_mm.can()

    @classmethod
    def get_breadcrumbs_menu(cls):  # pylint: disable=locally-disabled,unused-argument
        """
        Get breadcrumbs menu.
        """
        action_menu = hawat.menu.Menu()

        action_menu.add_entry(
            'endpoint',
            'home',
            endpoint = flask.current_app.config['HAWAT_ENDPOINT_HOME']
        )
        action_menu.add_entry(
            'endpoint',
            'list',
            endpoint = 'groups.list'
        )
        action_menu.add_entry(
            'endpoint',
            'pshow',
            endpoint = 'groups.show'
        )
        action_menu.add_entry(
            'endpoint',
            'show',
            endpoint = '{}.show'.format(cls.module_name),
        )

        return action_menu

    @classmethod
    def get_action_menu(cls):
        """
        Get action menu for particular item.
        """
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            'endpoint',
            'showgroup',
            endpoint = 'groups.show',
            title = lazy_gettext('Group')
        )
        action_menu.add_entry(
            'endpoint',
            'update',
            endpoint = 'settings_reporting.update'
        )
        return action_menu

    def do_before_response(self, **kwargs):
        """
        *Hook method*. Implementation of :py:func:`hawat.base.HawatDbmodelView.do_before_render` interface.
        """
        item = self.response_context['item']
        system_default_repsettings = mentat.reports.utils.ReportingSettings(
            item.group
        )
        self.response_context.update(
            system_default_repsettings = system_default_repsettings
        )

        if self.can_access_endpoint('settings_reporting.update', item = item) and self.has_endpoint('changelogs.search'):
            self.response_context.update(
                context_action_menu_changelogs = self.get_endpoint_class('changelogs.search').get_context_action_menu()
            )

            item_changelog = self.dbsession.query(ItemChangeLogModel).\
                filter(ItemChangeLogModel.model == item.__class__.__name__).\
                filter(ItemChangeLogModel.model_id == item.id).\
                order_by(ItemChangeLogModel.createtime.desc()).\
                limit(100).\
                all()
            self.response_context.update(item_changelog = item_changelog)

def _fill_in_timing_defaults(form):
    for attr in sorted(mentat.const.REPORTING_TIMING_ATTRS.keys()):
        if getattr(form, attr).data is None:
            getattr(form, attr).data = mentat.const.REPORTING_INTERVALS[
                mentat.const.REPORTING_TIMING_ATTRS[attr]
            ]

class CreateView(HTMLMixin, SQLAlchemyMixin, ItemCreateView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for creating new reporting settings.
    """
    methods = ['GET','POST']

    authentication = True

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Create reporting settings')

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Create new reporting settings')

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return SettingsReportingModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        """
        Perform access authorization for current user to particular item.
        """
        permission_m = flask_principal.Permission(
            hawat.acl.ManagementNeed(kwargs['item'].group.id)
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_m.can()

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_success`."""
        return gettext('Reporting settings <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong> were successfully created.', item_id = str(kwargs['item']), parent_id = str(kwargs['item'].group))

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext('Unable to create new reporting settings for group <strong>%(parent_id)s</strong>.', parent_id = str(kwargs['item'].group))

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext('Canceled creating new reporting settings for group <strong>%(parent_id)s</strong>.', parent_id = str(kwargs['item'].group))

    @staticmethod
    def get_item_form():
        """*Implementation* of :py:func:`hawat.base.ItemCreateView.get_item_form`."""
        return CreateSettingsReportingForm()

    def do_before_response(self, **kwargs):
        """
        *Hook method*. Implementation of :py:func:`hawat.base.HawatDbmodelView.do_before_render` interface.
        """
        _fill_in_timing_defaults(self.response_context['form'])


class UpdateView(HTMLMixin, SQLAlchemyMixin, ItemUpdateView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for updating existing reporting settings.
    """
    methods = ['GET','POST']

    authentication = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Update details of reporting settings for group &quot;%(item)s&quot;', item = kwargs['item'].group.name)

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Update reporting settings details')

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return SettingsReportingModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        """
        Perform access authorization for current user to particular item.
        """
        permission_m = flask_principal.Permission(
            hawat.acl.ManagementNeed(kwargs['item'].group.id)
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_m.can()

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_success`."""
        return gettext('Reporting settings <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong> were successfully updated.', item_id = str(kwargs['item']), parent_id = str(kwargs['item'].group))

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext('Unable to update reporting settings <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong>.', item_id = str(kwargs['item']), parent_id = str(kwargs['item'].group))

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext('Canceled updating reporting settings <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong>.', item_id = str(kwargs['item']), parent_id = str(kwargs['item'].group))

    @staticmethod
    def get_item_form(item):
        """*Implementation* of :py:func:`hawat.base.ItemUpdateView.get_item_form`."""
        return UpdateSettingsReportingForm(obj = item)

    def get_url_next(self):
        """
        *Hook method*. Implementation of :py:func:`hawat.base.ItemUpdateView.get_url_next` interface.
        """
        return flask.url_for('groups.list')

    def do_before_response(self, **kwargs):
        """
        *Hook method*. Implementation of :py:func:`hawat.base.HawatDbmodelView.do_before_render` interface.
        """
        _fill_in_timing_defaults(self.response_context['form'])


#-------------------------------------------------------------------------------


class SettingsReportingBlueprint(HawatBlueprint):
    """
    Hawat pluggable module - reporting settings.
    """

    @classmethod
    def get_module_title(cls):
        """*Implementation* of :py:func:`hawat.base.HawatBlueprint.get_module_title`."""
        return lazy_gettext('Reporting settings management pluggable module')


#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`hawat.base.HawatBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = SettingsReportingBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates',
        url_prefix = '/{}'.format(BLUEPRINT_NAME)
    )

    hbp.register_view_class(CreateView, '/create')
    hbp.register_view_class(ShowView, '/<int:item_id>/show')
    hbp.register_view_class(UpdateView, '/<int:item_id>/update')

    return hbp
