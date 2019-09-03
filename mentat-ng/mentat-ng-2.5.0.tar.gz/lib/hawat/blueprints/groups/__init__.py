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

This pluggable module provides access to group account management features. These
features include:

* general group account listing
* detailed group account view
* creating new group accounts
* updating existing group accounts
* deleting existing group accounts
* enabling existing group accounts
* disabling existing group accounts
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import pprint
#
# Flask related modules.
#
import flask
import flask_login
import flask_principal
from flask_babel import gettext, lazy_gettext

from sqlalchemy import and_, or_

#
# Custom modules.
#
from mentat.datatype.sqldb import UserModel, GroupModel, SettingsReportingModel,\
    FilterModel, NetworkModel, ItemChangeLogModel
from mentat.const import tr_

import hawat.acl
import hawat.db
import hawat.menu
from hawat.base import HTMLMixin, SQLAlchemyMixin, ItemListView,\
    ItemShowView, ItemCreateView, ItemUpdateView, ItemEnableView,\
    ItemDisableView, ItemObjectRelationView, ItemDeleteView, HawatBlueprint,\
    URLParamsBuilder

from hawat.blueprints.groups.forms import CreateGroupForm, UpdateGroupForm,\
    AdminUpdateGroupForm


BLUEPRINT_NAME = 'groups'
"""Name of the blueprint as module global constant."""


class ListView(HTMLMixin, SQLAlchemyMixin, ItemListView):
    """
    General group listing.
    """

    methods = ['GET']

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Group management')

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return GroupModel

    @classmethod
    def get_action_menu(cls):
        """*Implementation* of :py:func:`hawat.base.ItemListView.get_action_menu`."""
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            'endpoint',
            'create',
            endpoint = 'groups.create',
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
            endpoint = 'groups.show',
            hidetitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'update',
            endpoint = 'groups.update',
            hidetitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'disable',
            endpoint = 'groups.disable',
            hidetitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'enable',
            endpoint = 'groups.enable',
            hidetitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'delete',
            endpoint = 'groups.delete',
            hidetitle = True
        )
        return action_menu


class ShowView(HTMLMixin, SQLAlchemyMixin, ItemShowView):
    """
    Detailed group view.
    """

    methods = ['GET']

    authentication = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        if isinstance(kwargs['item'], GroupModel):
            return lazy_gettext('View details of group &quot;%(item)s&quot;', item = str(kwargs['item']))
        return lazy_gettext('View details of group &quot;%(item)s&quot;', item = str(kwargs['item'].group))

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Show group details')

    @classmethod
    def get_view_url(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_url`."""
        if isinstance(kwargs['item'], GroupModel):
            return flask.url_for(cls.get_view_endpoint(), item_id = kwargs['item'].get_id())
        return flask.url_for(cls.get_view_endpoint(), item_id = kwargs['item'].group.get_id())

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return GroupModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        """
        Perform access authorization for current user to particular item.
        """
        permission_mm = flask_principal.Permission(
            hawat.acl.MembershipNeed(kwargs['item'].id),
            hawat.acl.ManagementNeed(kwargs['item'].id)
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
            endpoint = 'groups.update',
            resptitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'disable',
            endpoint = 'groups.disable',
            resptitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'enable',
            endpoint = 'groups.enable',
            resptitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'delete',
            endpoint = 'groups.delete',
            resptitle = True
        )
        action_menu.add_entry(
            'submenu',
            'more',
            align_right = True,
            legend = gettext('More actions')
        )
        action_menu.add_entry(
            'endpoint',
            'more.createnetwork',
            endpoint = 'networks.createfor'
        )
        action_menu.add_entry(
            'endpoint',
            'more.createfilter',
            endpoint = 'filters.createfor'
        )
        return action_menu

    def do_before_response(self, **kwargs):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """*Implementation* of :py:func:`hawat.base.RenderableView.do_before_response`."""
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            'endpoint',
            'show',
            endpoint = 'users.show',
            hidetitle = True,
        )
        action_menu.add_entry(
            'submenu',
            'more',
            align_right = True,
            legend = gettext('More actions')
        )
        action_menu.add_entry(
            'endpoint',
            'more.add_membership',
            endpoint = 'users.addmembership'
        )
        action_menu.add_entry(
            'endpoint',
            'more.remove_membership',
            endpoint = 'users.removemembership'
        )
        action_menu.add_entry(
            'endpoint',
            'more.enable',
            endpoint = 'users.enable'
        )
        action_menu.add_entry(
            'endpoint',
            'more.disable',
            endpoint = 'users.disable'
        )
        action_menu.add_entry(
            'endpoint',
            'more.update',
            endpoint = 'users.update'
        )
        self.response_context.update(context_action_menu_users = action_menu)

        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            'endpoint',
            'show',
            endpoint = 'networks.show',
            hidetitle = True,
        )
        self.response_context.update(context_action_menu_networks = action_menu)

        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            'endpoint',
            'show',
            endpoint = 'filters.show',
            hidetitle = True,
        )
        self.response_context.update(context_action_menu_filters = action_menu)

        item = self.response_context['item']
        if self.can_access_endpoint('groups.update', item = item) and self.has_endpoint('changelogs.search'):
            self.response_context.update(
                context_action_menu_changelogs = self.get_endpoint_class('changelogs.search').get_context_action_menu()
            )

            item_changelog = self.dbsession.query(ItemChangeLogModel).\
                filter(
                    or_(
                        # Changelogs related directly to group item.
                        and_(
                            ItemChangeLogModel.model == item.__class__.__name__,
                            ItemChangeLogModel.model_id == item.id
                        ),
                        # Changelogs related to group reporting settings item.
                        and_(
                            ItemChangeLogModel.model == SettingsReportingModel.__name__,
                            ItemChangeLogModel.model_id.in_(
                                self.dbsession.query(SettingsReportingModel.id).filter(SettingsReportingModel.group_id == item.id)
                            )
                        ),
                        # Changelogs related to all group reporting filters.
                        and_(
                            ItemChangeLogModel.model == FilterModel.__name__,
                            ItemChangeLogModel.model_id.in_(
                                self.dbsession.query(FilterModel.id).filter(FilterModel.group_id == item.id)
                            )
                        ),
                        # Changelogs related to all group network records.
                        and_(
                            ItemChangeLogModel.model == NetworkModel.__name__,
                            ItemChangeLogModel.model_id.in_(
                                self.dbsession.query(NetworkModel.id).filter(NetworkModel.group_id == item.id)
                            )
                        )
                    )
                ).\
                order_by(ItemChangeLogModel.createtime.desc()).\
                limit(100).\
                all()
            self.response_context.update(item_changelog = item_changelog)


class ShowByNameView(ShowView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    Detailed group view by group name.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'show_by_name'

    @classmethod
    def get_view_template(cls):
        """*Implementation* of :py:func:`hawat.base.RenderableView.get_view_template`."""
        return '{}/show.html'.format(cls.module_name)

    @property
    def search_by(self):
        """
        *Interface implementation* of :py:func:`hawat.base.ItemShowView.search_by`.
        """
        return self.dbmodel.name


class CreateView(HTMLMixin, SQLAlchemyMixin, ItemCreateView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for creating new groups.
    """

    methods = ['GET','POST']

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Create group')

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Create new group')

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return GroupModel

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_success`."""
        return gettext('Group <strong>%(item_id)s</strong> was successfully created.', item_id = str(kwargs['item']))

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext('Unable to create new group.')

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext('Canceled creating new group.')

    @staticmethod
    def get_item_form():
        """*Implementation* of :py:func:`hawat.base.ItemCreateView.get_item_form`."""
        return CreateGroupForm()

    def do_before_action(self, item):
        """
        *Hook method*. Will be called before successfull insertion of the item into
        the database.
        """
        # Create empty reporting settings object and assign it to the group.
        SettingsReportingModel(group = item)


class UpdateView(HTMLMixin, SQLAlchemyMixin, ItemUpdateView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for updating existing groups.
    """

    methods = ['GET','POST']

    authentication = True

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Update')

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Update details of group &quot;%(item)s&quot;', item = str(kwargs['item']))

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Update group details')

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
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
        return gettext('Group <strong>%(item_id)s</strong> was successfully updated.', item_id = str(kwargs['item']))

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext('Unable to update group <strong>%(item_id)s</strong>.', item_id = str(kwargs['item']))

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext('Canceled updating group <strong>%(item_id)s</strong>.', item_id = str(kwargs['item']))

    @staticmethod
    def get_item_form(item):
        """*Implementation* of :py:func:`hawat.base.ItemUpdateView.get_item_form`."""
        admin = flask_login.current_user.has_role('admin')
        if not admin:
            form = UpdateGroupForm(obj = item)
        else:
            form = AdminUpdateGroupForm(db_item_id = item.id, obj = item)
        return form


class AddMemberView(HTMLMixin, SQLAlchemyMixin, ItemObjectRelationView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for enabling existing groups.
    """
    methods = ['GET','POST']

    authentication = True

    @classmethod
    def get_view_name(cls):
        return 'addmember'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return gettext('Add group member')

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'action-add-member'

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext(
            'Add user &quot;%(user_id)s&quot; to group &quot;%(group_id)s&quot;',
            user_id  = str(kwargs['other']),
            group_id = str(kwargs['item'])
        )

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return GroupModel

    @property
    def dbmodel_other(self):
        """*Implementation* of :py:func:`hawat.base.AddMemberView.dbmodel_other`."""
        return UserModel

    #---------------------------------------------------------------------------

    @classmethod
    def authorize_item_action(cls, **kwargs):
        """
        Perform access authorization for current user to particular item.
        """
        permission_m = flask_principal.Permission(
            hawat.acl.ManagementNeed(kwargs['item'].id)
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_m.can()

    @classmethod
    def validate_item_change(cls, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        """
        Perform validation of particular change to given item.
        """
        # Reject item change in case given item is already enabled.
        if kwargs['other'] in kwargs['item'].members:
            return False
        return True

    @classmethod
    def change_item(cls, **kwargs):
        """
        *Interface implementation* of :py:func:`hawat.base.ItemChangeView.change_item`.
        """
        kwargs['item'].members.append(kwargs['other'])
        try:
            kwargs['item'].members_wanted.remove(kwargs['other'])
        except ValueError:
            pass
        if kwargs['other'].is_state_disabled():
            kwargs['other'].set_state_enabled()
            flask.current_app.send_infomail('users.enable', account = kwargs['other'])

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_success`."""
        return gettext(
            'User <strong>%(user_id)s</strong> was successfully added as a member to group <strong>%(group_id)s</strong>.',
            user_id  = str(kwargs['other']),
            group_id = str(kwargs['item'])
        )

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext(
            'Unable to add user <strong>%(user_id)s</strong> as a member to group <strong>%(group_id)s</strong>.',
            user_id  = str(kwargs['other']),
            group_id = str(kwargs['item'])
        )

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext(
            'Canceled adding user <strong>%(user_id)s</strong> as a member to group <strong>%(group_id)s</strong>.',
            user_id  = str(kwargs['other']),
            group_id = str(kwargs['item'])
        )


class RemoveMemberView(HTMLMixin, SQLAlchemyMixin, ItemObjectRelationView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for removing users from existing groups.
    """
    methods = ['GET','POST']

    authentication = True

    @classmethod
    def get_view_name(cls):
        return 'removemember'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return gettext('Remove group member')

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'action-rem-member'

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext(
            'Remove user &quot;%(user_id)s&quot; from group &quot;%(group_id)s&quot;',
            user_id  = str(kwargs['other']),
            group_id = str(kwargs['item'])
        )

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return GroupModel

    @property
    def dbmodel_other(self):
        """*Implementation* of :py:func:`hawat.base.AddMemberView.dbmodel_other`."""
        return UserModel

    #---------------------------------------------------------------------------

    @classmethod
    def authorize_item_action(cls, **kwargs):
        """
        Perform access authorization for current user to particular item.
        """
        permission_m = flask_principal.Permission(
            hawat.acl.ManagementNeed(kwargs['item'].id)
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_m.can()

    @classmethod
    def validate_item_change(cls, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        """
        Perform validation of particular change to given item.
        """
        # Reject item change in case given item is already enabled.
        if kwargs['other'] not in kwargs['item'].members:
            return False
        return True

    @classmethod
    def change_item(cls, **kwargs):
        """
        *Interface implementation* of :py:func:`hawat.base.ItemChangeView.change_item`.
        """
        kwargs['item'].members.remove(kwargs['other'])

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_success`."""
        return gettext(
            'User <strong>%(user_id)s</strong> was successfully removed as a member from group <strong>%(group_id)s</strong>.',
            user_id  = str(kwargs['other']),
            group_id = str(kwargs['item'])
        )

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext(
            'Unable to remove user <strong>%(user_id)s</strong> as a member from group <strong>%(group_id)s</strong>.',
            user_id  = str(kwargs['other']),
            group_id = str(kwargs['item'])
        )

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext(
            'Canceled removing user <strong>%(user_id)s</strong> as a member from group <strong>%(group_id)s</strong>.',
            user_id  = str(kwargs['other']),
            group_id = str(kwargs['item'])
        )


class EnableView(HTMLMixin, SQLAlchemyMixin, ItemEnableView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for enabling existing groups.
    """
    methods = ['GET','POST']

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Enable group &quot;%(item)s&quot;', item = str(kwargs['item']))

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return GroupModel

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_success`."""
        return gettext('Group <strong>%(item_id)s</strong> was successfully enabled.', item_id = str(kwargs['item']))

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext('Unable to enable group <strong>%(item_id)s</strong>.', item_id = str(kwargs['item']))

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext('Canceled enabling group <strong>%(item_id)s</strong>.', item_id = str(kwargs['item']))


class DisableView(HTMLMixin, SQLAlchemyMixin, ItemDisableView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for deleting existing user accounts.
    """
    methods = ['GET','POST']

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Disable group &quot;%(item)s&quot;', item = str(kwargs['item']))

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return GroupModel

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_success`."""
        return gettext('Group <strong>%(item_id)s</strong> was successfully disabled.', item_id = str(kwargs['item']))

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext('Unable to disable group <strong>%(item_id)s</strong>.', item_id = str(kwargs['item']))

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext('Canceled disabling group <strong>%(item_id)s</strong>.', item_id = str(kwargs['item']))


class DeleteView(HTMLMixin, SQLAlchemyMixin, ItemDeleteView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for deleting existing groups.
    """

    methods = ['GET','POST']

    authentication = True

    authorization = [hawat.acl.PERMISSION_ADMIN]

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """
        *Interface implementation* of :py:func:`hawat.base.BaseView.get_menu_legend`.
        """
        return lazy_gettext('Delete group &quot;%(item)s&quot;', item = str(kwargs['item']))

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return GroupModel

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_success`."""
        return gettext('Group <strong>%(item_id)s</strong> was successfully and permanently deleted.', item_id = str(kwargs['item']))

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext('Unable to delete group <strong>%(item_id)s</strong>.', item_id = str(kwargs['item']))

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext('Canceled deleting group <strong>%(item_id)s</strong>.', item_id = str(kwargs['item']))


#-------------------------------------------------------------------------------


class GroupsBlueprint(HawatBlueprint):
    """
    Hawat pluggable module - abuse groups.
    """

    @classmethod
    def get_module_title(cls):
        """*Implementation* of :py:func:`hawat.base.HawatBlueprint.get_module_title`."""
        return lazy_gettext('Group management pluggable module')

    def register_app(self, app):
        """
        *Callback method*. Will be called from :py:func:`hawat.base.HawatApp.register_blueprint`
        method and can be used to customize the Flask application object. Possible
        use cases:

        * application menu customization

        :param hawat.base.HawatApp app: Flask application to be customize.
        """

        def _fetch_my_groups():
            groups = {}
            for i in list(flask_login.current_user.memberships) + list(flask_login.current_user.managements):
                groups[str(i)] = i
            return list(sorted(groups.values(), key = str))

        app.menu_main.add_entry(
            'view',
            'admin.{}'.format(BLUEPRINT_NAME),
            position = 50,
            view = ListView
        )
        app.menu_auth.add_entry(
            'submenudb',
            'my_groups',
            position = 40,
            title = lazy_gettext('My groups'),
            resptitle = True,
            icon = 'module-groups',
            align_right = True,
            entry_fetcher = _fetch_my_groups,
            entry_builder = lambda x, y: hawat.menu.EndpointEntry(x, endpoint = 'groups.show', item = y, title = x, icon = 'module-groups')
        )

        # Register context actions provided by this module.
        app.set_csag(
            hawat.const.HAWAT_CSAG_ABUSE,
            tr_('View details of abuse group <strong>%(name)s</strong>'),
            ShowByNameView,
            URLParamsBuilder().add_rule('item_id')
        )


#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`hawat.base.HawatBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = GroupsBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates',
        url_prefix = '/{}'.format(BLUEPRINT_NAME)
    )

    hbp.register_view_class(ListView, '/list')
    hbp.register_view_class(CreateView, '/create')
    hbp.register_view_class(ShowView, '/<int:item_id>/show')
    hbp.register_view_class(ShowByNameView, '/<item_id>/show_by_name')
    hbp.register_view_class(UpdateView, '/<int:item_id>/update')
    hbp.register_view_class(AddMemberView, '/<int:item_id>/add_member/<int:other_id>')
    hbp.register_view_class(RemoveMemberView, '/<int:item_id>/remove_member/<int:other_id>')
    hbp.register_view_class(EnableView, '/<int:item_id>/enable')
    hbp.register_view_class(DisableView, '/<int:item_id>/disable')
    hbp.register_view_class(DeleteView, '/<int:item_id>/delete')

    return hbp
