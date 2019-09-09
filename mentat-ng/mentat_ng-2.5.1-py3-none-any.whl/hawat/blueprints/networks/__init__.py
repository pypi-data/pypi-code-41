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

This pluggable module provides access to network record management features. These
features include:

* general network record listing
* detailed network record view
* creating new network records
* updating existing network records
* deleting existing network records
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


#
# Flask related modules.
#
import flask
import flask_login
import flask_principal
from flask_babel import gettext, lazy_gettext

#
# Custom modules.
#
from mentat.datatype.sqldb import NetworkModel, GroupModel, ItemChangeLogModel

import hawat.base
import hawat.db
from hawat.base import HTMLMixin, SQLAlchemyMixin, ItemListView,\
    ItemShowView, ItemCreateView, HawatItemCreateForView, ItemUpdateView,\
    ItemDeleteView, HawatBlueprint
from hawat.blueprints.networks.forms import BaseNetworkForm, AdminNetworkForm


BLUEPRINT_NAME = 'networks'
"""Name of the blueprint as module global constant."""


class ListView(HTMLMixin, SQLAlchemyMixin, ItemListView):
    """
    General network record listing.
    """
    methods = ['GET']

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Network management')

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return NetworkModel

    @classmethod
    def get_action_menu(cls):
        """*Implementation* of :py:func:`hawat.base.ItemListView.get_action_menu`."""
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            'endpoint',
            'create',
            endpoint = 'networks.create',
            resptitle = True
        )
        return action_menu

    @classmethod
    def get_context_action_menu(cls):
        """*Implementation* of :py:func:`hawat.base.ItemListView.get_context_action_menu`."""
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            'endpoint',
            'show',
            endpoint = 'networks.show',
            hidetitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'update',
            endpoint = 'networks.update',
            hidetitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'delete',
            endpoint = 'networks.delete',
            hidetitle = True
        )
        return action_menu


class ShowView(HTMLMixin, SQLAlchemyMixin, ItemShowView):
    """
    Detailed network record view.
    """
    methods = ['GET']

    authentication = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('View details of network record &quot;%(item)s&quot;', item = kwargs['item'].netname)

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Show network record details')

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return NetworkModel

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
    def get_action_menu(cls):
        """
        Get action menu for particular item.
        """
        action_menu = hawat.menu.Menu()

        action_menu.add_entry(
            'endpoint',
            'update',
            endpoint = 'networks.update'
        )
        action_menu.add_entry(
            'endpoint',
            'delete',
            endpoint = 'networks.delete'
        )

        return action_menu

    def do_before_response(self, **kwargs):
        """
        *Hook method*. Implementation of :py:func:`hawat.base.HawatDbmodelView.do_before_render` interface.
        """
        item = self.response_context['item']
        if self.can_access_endpoint('networks.update', item = item) and self.has_endpoint('changelogs.search'):
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


class CreateView(HTMLMixin, SQLAlchemyMixin, ItemCreateView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for creating new network records.
    """
    methods = ['GET','POST']

    authentication = True

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Create network record')

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Create new network record')

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return NetworkModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        """
        Perform access authorization for current user to particular item.
        """
        return hawat.acl.PERMISSION_POWER.can()

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_success`."""
        return gettext('Network record <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong> was successfully created.', item_id = str(kwargs['item']), parent_id = str(kwargs['item'].group))

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext('Unable to create new network record for group <strong>%(parent_id)s</strong>.', parent_id = str(kwargs['item'].group))

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext('Canceled creating new network record for group <strong>%(parent_id)s</strong>.', parent_id = str(kwargs['item'].group))

    @staticmethod
    def get_item_form():
        """*Implementation* of :py:func:`hawat.base.ItemCreateView.get_item_form`."""
        return AdminNetworkForm()


class CreateForView(HTMLMixin, SQLAlchemyMixin, HawatItemCreateForView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for creating new network records.
    """
    methods = ['GET','POST']

    authentication = True

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'module-{}'.format(BLUEPRINT_NAME)

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Create network record')

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """
        *Interface implementation* of :py:func:`hawat.base.BaseView.get_menu_legend`.
        """
        return lazy_gettext('Create network record for group &quot;%(item)s&quot;', item = str(kwargs['item']))

    @classmethod
    def get_view_url(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_url`."""
        return flask.url_for(cls.get_view_endpoint(), parent_id = kwargs['item'].id)

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Create new network record for group')

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return NetworkModel

    @property
    def dbmodel_par(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return GroupModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        """
        Perform access authorization for current user to particular item.
        """
        permission_m = flask_principal.Permission(
            hawat.acl.ManagementNeed(kwargs['item'].id)
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_m.can()

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_success`."""
        return gettext('Network record <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong> was successfully created.', item_id = str(kwargs['item']), parent_id = str(kwargs['parent']))

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext('Unable to create new network record for group <strong>%(parent_id)s</strong>.', parent_id = str(kwargs['parent']))

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext('Canceled creating new network record for group <strong>%(parent_id)s</strong>.', parent_id = str(kwargs['parent']))

    @staticmethod
    def get_item_form():
        """*Implementation* of :py:func:`hawat.base.ItemCreateView.get_item_form`."""
        return BaseNetworkForm()

    @staticmethod
    def add_parent_to_item(item, parent):
        """
        *Hook method*. Implementation of :py:func:`hawat.base.HawatItemCreateForView.add_parent_to_item` interface.
        """
        item.group = parent


class UpdateView(HTMLMixin, SQLAlchemyMixin, ItemUpdateView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for updating existing network records.
    """
    methods = ['GET','POST']

    authentication = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Update details of network record &quot;%(item)s&quot;', item = kwargs['item'].netname)

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Update network record details')

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return NetworkModel

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
        return gettext('Network record <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong> was successfully updated.', item_id = str(kwargs['item']), parent_id = str(kwargs['item'].group))

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext('Unable to update network record <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong>.', item_id = str(kwargs['item']), parent_id = str(kwargs['item'].group))

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext('Canceled updating network record <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong>.', item_id = str(kwargs['item']), parent_id = str(kwargs['item'].group))

    @staticmethod
    def get_item_form(item):
        """*Implementation* of :py:func:`hawat.base.ItemUpdateView.get_item_form`."""
        admin = flask_login.current_user.has_role('admin')
        if not admin:
            return BaseNetworkForm(obj = item)

        return AdminNetworkForm(obj = item)


class DeleteView(HTMLMixin, SQLAlchemyMixin, ItemDeleteView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for deleting existing network records.
    """
    methods = ['GET','POST']

    authentication = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """
        *Interface implementation* of :py:func:`hawat.base.BaseView.get_menu_legend`.
        """
        return lazy_gettext('Delete network record &quot;%(item)s&quot;', item = kwargs['item'].netname)

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return NetworkModel

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
        return gettext('Network record <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong> was successfully and permanently deleted.', item_id = str(kwargs['item']), parent_id = str(kwargs['item'].group))

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext('Unable to permanently delete network record <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong>.', item_id = str(kwargs['item']), parent_id = str(kwargs['item'].group))

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext('Canceled deleting network record <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong>.', item_id = str(kwargs['item']), parent_id = str(kwargs['item'].group))


#-------------------------------------------------------------------------------


class NetworksBlueprint(HawatBlueprint):
    """
    Hawat pluggable module - networks.
    """

    @classmethod
    def get_module_title(cls):
        """*Implementation* of :py:func:`hawat.base.HawatBlueprint.get_module_title`."""
        return lazy_gettext('Network record management pluggable module')

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
            'admin.{}'.format(BLUEPRINT_NAME),
            position = 70,
            view = ListView
        )


#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`hawat.base.HawatBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = NetworksBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates',
        url_prefix = '/{}'.format(BLUEPRINT_NAME)
    )

    hbp.register_view_class(ListView, '/list')
    hbp.register_view_class(CreateView, '/create')
    hbp.register_view_class(CreateForView, '/createfor/<int:parent_id>')
    hbp.register_view_class(ShowView, '/<int:item_id>/show')
    hbp.register_view_class(UpdateView, '/<int:item_id>/update')
    hbp.register_view_class(DeleteView, '/<int:item_id>/delete')

    return hbp
