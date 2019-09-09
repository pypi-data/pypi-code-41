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

This pluggable module provides access to user account management features. These
features include:

* general user account listing
* detailed user account view
* creating new user accounts
* updating existing user accounts
* deleting existing user accounts
* enabling existing user accounts
* disabling existing user accounts
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


#
# Flask related modules.
#
import flask
import flask_login
import flask_principal
import flask_mail
from flask_babel import gettext, lazy_gettext, force_locale

#
# Custom modules.
#
from mentat.datatype.sqldb import UserModel, GroupModel, ItemChangeLogModel

import hawat.const
import hawat.db
import hawat.acl
from hawat.base import HTMLMixin, SQLAlchemyMixin, ItemListView,\
    ItemShowView, ItemCreateView, ItemUpdateView, ItemEnableView,\
    ItemDisableView, ItemDeleteView, ItemObjectRelationView, HawatBlueprint
from hawat.blueprints.users.forms import CreateUserAccountForm, UpdateUserAccountForm,\
    AdminUpdateUserAccountForm


BLUEPRINT_NAME = 'users'
"""Name of the blueprint as module global constant."""


class ListView(HTMLMixin, SQLAlchemyMixin, ItemListView):
    """
    General user account listing.
    """
    methods = ['GET']

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('User management')

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    @classmethod
    def get_action_menu(cls):
        """*Implementation* of :py:func:`hawat.base.ItemListView.get_action_menu`."""
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            'endpoint',
            'create',
            endpoint = 'users.create',
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
            endpoint = 'users.show',
            hidetitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'update',
            endpoint = 'users.update',
            hidetitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'disable',
            endpoint = 'users.disable',
            hidetitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'enable',
            endpoint = 'users.enable',
            hidetitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'delete',
            endpoint = 'users.delete',
            hidetitle = True
        )
        return action_menu


class ShowView(HTMLMixin, SQLAlchemyMixin, ItemShowView):
    """
    Detailed user account view.
    """
    methods = ['GET']

    authentication = True

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'action-show-user'

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Show details of user account &quot;%(item)s&quot;', item = kwargs['item'].login)

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Show user account details')

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        """
        Perform access authorization for current user to particular item.
        """
        # Each user must be able to view his/her account.
        permission_me = flask_principal.Permission(
            flask_principal.UserNeed(kwargs['item'].id)
        )
        # Managers of the groups the user is member of may view his/her account.
        needs = [hawat.acl.ManagementNeed(x.id) for x in kwargs['item'].memberships]
        permission_mngr = flask_principal.Permission(*needs)
        return hawat.acl.PERMISSION_POWER.can() or permission_mngr.can() or permission_me.can()

    @classmethod
    def get_action_menu(cls):
        """
        Get action menu for particular item.
        """
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            'endpoint',
            'update',
            endpoint = 'users.update',
            resptitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'disable',
            endpoint = 'users.disable',
            resptitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'enable',
            endpoint = 'users.enable',
            resptitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'delete',
            endpoint = 'users.delete',
            resptitle = True
        )
        return action_menu

    def do_before_response(self, **kwargs):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """*Implementation* of :py:func:`hawat.base.RenderableView.do_before_response`."""
        item = self.response_context['item']
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            'endpoint',
            'show',
            endpoint = 'groups.show',
            hidetitle = True
        )
        action_menu.add_entry(
            'submenu',
            'more',
            align_right = True,
            legend = gettext('More actions')
        )
        action_menu.add_entry(
            'endpoint',
            'more.add_member',
            endpoint = 'groups.addmember'
        )
        action_menu.add_entry(
            'endpoint',
            'more.remove_member',
            endpoint = 'groups.removemember'
        )
        action_menu.add_entry(
            'endpoint',
            'more.enable',
            endpoint = 'groups.enable'
        )
        action_menu.add_entry(
            'endpoint',
            'more.disable',
            endpoint = 'groups.disable'
        )
        action_menu.add_entry(
            'endpoint',
            'more.update',
            endpoint = 'groups.update'
        )
        self.response_context.update(context_action_menu_groups = action_menu)

        if self.has_endpoint('changelogs.search'):
            self.response_context.update(
                context_action_menu_changelogs = self.get_endpoint_class('changelogs.search').get_context_action_menu()
            )

            if self.can_access_endpoint('users.update', item = item) and self.has_endpoint('changelogs.search'):

                item_changelog = self.dbsession.query(ItemChangeLogModel).\
                    filter(ItemChangeLogModel.model == item.__class__.__name__).\
                    filter(ItemChangeLogModel.model_id == item.id).\
                    order_by(ItemChangeLogModel.createtime.desc()).\
                    limit(100).\
                    all()
                self.response_context.update(item_changelog = item_changelog)

                user_changelog = self.dbsession.query(ItemChangeLogModel).\
                    filter(ItemChangeLogModel.author_id == item.id).\
                    order_by(ItemChangeLogModel.createtime.desc()).\
                    limit(100).\
                    all()
                self.response_context.update(user_changelog = user_changelog)


class MeView(ShowView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    Detailed user account view for currently logged-in user.
    """
    methods = ['GET']

    authentication = True

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'me'

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'profile'

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('My account')

    @classmethod
    def get_view_url(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_url`."""
        return flask.url_for(cls.get_view_endpoint())

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('My user account')

    @classmethod
    def get_view_template(cls):
        """*Implementation* of :py:func:`hawat.base.RenderableView.get_view_template`."""
        return '{}/show.html'.format(BLUEPRINT_NAME)

    @classmethod
    def authorize_item_action(cls, **kwargs):
        """
        Perform access authorization for current user to particular item.
        """
        return True

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
            'show',
            endpoint = '{}.me'.format(cls.module_name)
        )
        return action_menu

    #---------------------------------------------------------------------------

    def dispatch_request(self):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the *Flask* framework to service the request.

        Single item with given unique identifier will be retrieved from database
        and injected into template to be displayed to the user.
        """
        item_id = flask_login.current_user.get_id()
        item = self.dbquery().filter(self.dbmodel.id == item_id).first()
        if not item:
            self.abort(404)

        self.response_context.update(
            item_id = item_id,
            item = item,
            breadcrumbs_menu = self.get_breadcrumbs_menu(),
            action_menu = self.get_action_menu()
        )

        self.do_before_response()

        return self.generate_response()


class CreateView(HTMLMixin, SQLAlchemyMixin, ItemCreateView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for creating new user accounts.
    """
    methods = ['GET','POST']

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'action-create-user'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Create new user account')

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_success`."""
        return gettext('User account <strong>%(item_id)s</strong> was successfully created.', item_id = str(kwargs['item']))

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext('Unable to create new user account.')

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext('Canceled creating new user account.')

    @staticmethod
    def get_item_form():
        """*Implementation* of :py:func:`hawat.base.ItemCreateView.get_item_form`."""
        #
        # Inject list of choices for supported locales and roles. Another approach
        # would be to let the form get the list on its own, however that would create
        # dependency on application object.
        #
        roles = list(zip(flask.current_app.config['ROLES'], flask.current_app.config['ROLES']))
        locales = list(flask.current_app.config['SUPPORTED_LOCALES'].items())

        return CreateUserAccountForm(
            choices_roles = roles,
            choices_locales = locales
        )


class UpdateView(HTMLMixin, SQLAlchemyMixin, ItemUpdateView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for updating existing user accounts.
    """
    methods = ['GET','POST']

    authentication = True

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'action-update-user'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Update user account details')

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Update details of user account &quot;%(item)s&quot;', item = kwargs['item'].login)

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        """
        Perform access authorization for current user to particular item.
        """
        permission_me = flask_principal.Permission(
            flask_principal.UserNeed(kwargs['item'].id)
        )
        return hawat.acl.PERMISSION_ADMIN.can() or permission_me.can()

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_success`."""
        return gettext('User account <strong>%(item_id)s</strong> was successfully updated.', item_id = str(kwargs['item']))

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext('Unable to update user account <strong>%(item_id)s</strong>.', item_id = str(kwargs['item']))

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext('Canceled updating user account <strong>%(item_id)s</strong>.', item_id = str(kwargs['item']))

    @staticmethod
    def get_item_form(item):
        """*Implementation* of :py:func:`hawat.base.ItemUpdateView.get_item_form`."""

        #
        # Inject list of choices for supported locales and roles. Another approach
        # would be to let the form get the list on its own, however that would create
        # dependency on application object.
        #
        roles = list(zip(flask.current_app.config['ROLES'], flask.current_app.config['ROLES']))
        locales = list(flask.current_app.config['SUPPORTED_LOCALES'].items())

        admin = flask_login.current_user.has_role('admin')
        if not admin:
            form = UpdateUserAccountForm(
                choices_roles = roles,
                choices_locales = locales,
                obj = item
            )
        else:
            form = AdminUpdateUserAccountForm(
                choices_roles = roles,
                choices_locales = locales,
                db_item_id = item.id,
                obj = item
            )
        return form


class AddMembershipView(HTMLMixin, SQLAlchemyMixin, ItemObjectRelationView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for enabling existing groups.
    """
    methods = ['GET','POST']

    authentication = True

    @classmethod
    def get_view_name(cls):
        return 'addmembership'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return gettext('Add group membership')

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'action-add-member'

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext(
            'Add user &quot;%(user_id)s&quot; to group &quot;%(group_id)s&quot;',
            user_id  = str(kwargs['item']),
            group_id = str(kwargs['other'])
        )

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    @property
    def dbmodel_other(self):
        """*Implementation* of :py:func:`hawat.base.AddMemberView.dbmodel_other`."""
        return GroupModel

    #---------------------------------------------------------------------------

    @classmethod
    def authorize_item_action(cls, **kwargs):
        """
        Perform access authorization for current user to particular item.
        """
        permission_m = flask_principal.Permission(
            hawat.acl.ManagementNeed(kwargs['other'].id)
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_m.can()

    @classmethod
    def validate_item_change(cls, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        """
        Perform validation of particular change to given item.
        """
        # Reject item change in case given item is already enabled.
        if kwargs['other'] in kwargs['item'].memberships:
            return False
        return True

    @classmethod
    def change_item(cls, **kwargs):
        """
        *Interface implementation* of :py:func:`hawat.base.ItemChangeView.change_item`.
        """
        kwargs['item'].memberships.append(kwargs['other'])
        try:
            kwargs['item'].memberships_wanted.remove(kwargs['other'])
        except ValueError:
            pass
        if kwargs['item'].is_state_disabled():
            kwargs['item'].set_state_enabled()
            flask.current_app.send_infomail('users.enable', account = kwargs['item'])

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_success`."""
        return gettext(
            'User <strong>%(user_id)s</strong> was successfully added as a member to group <strong>%(group_id)s</strong>.',
            user_id  = str(kwargs['item']),
            group_id = str(kwargs['other'])
        )

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext(
            'Unable to add user <strong>%(user_id)s</strong> as a member to group <strong>%(group_id)s</strong>.',
            user_id  = str(kwargs['item']),
            group_id = str(kwargs['other'])
        )

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext(
            'Canceled adding user <strong>%(user_id)s</strong> as a member to group <strong>%(group_id)s</strong>.',
            user_id  = str(kwargs['item']),
            group_id = str(kwargs['other'])
        )


class RemoveMembershipView(HTMLMixin, SQLAlchemyMixin, ItemObjectRelationView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for removing users from existing groups.
    """
    methods = ['GET','POST']

    authentication = True

    @classmethod
    def get_view_name(cls):
        return 'removemembership'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return gettext('Remove group membership')

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'action-rem-member'

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext(
            'Remove user &quot;%(user_id)s&quot; from group &quot;%(group_id)s&quot;',
            user_id  = str(kwargs['item']),
            group_id = str(kwargs['other'])
        )

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    @property
    def dbmodel_other(self):
        """*Implementation* of :py:func:`hawat.base.AddMemberView.dbmodel_other`."""
        return GroupModel

    #---------------------------------------------------------------------------

    @classmethod
    def authorize_item_action(cls, **kwargs):
        """
        Perform access authorization for current user to particular item.
        """
        permission_m = flask_principal.Permission(
            hawat.acl.ManagementNeed(kwargs['other'].id)
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_m.can()

    @classmethod
    def validate_item_change(cls, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        """
        Perform validation of particular change to given item.
        """
        # Reject item change in case given item is already enabled.
        if kwargs['other'] not in kwargs['item'].memberships:
            return False
        return True

    @classmethod
    def change_item(cls, **kwargs):
        """
        *Interface implementation* of :py:func:`hawat.base.ItemChangeView.change_item`.
        """
        try:
            kwargs['item'].memberships.remove(kwargs['other'])
        except ValueError:
            pass

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_success`."""
        return gettext(
            'User <strong>%(user_id)s</strong> was successfully removed as a member from group <strong>%(group_id)s</strong>.',
            user_id  = str(kwargs['item']),
            group_id = str(kwargs['other'])
        )

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext(
            'Unable to remove user <strong>%(user_id)s</strong> as a member from group <strong>%(group_id)s</strong>.',
            user_id  = str(kwargs['item']),
            group_id = str(kwargs['other'])
        )

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext(
            'Canceled removing user <strong>%(user_id)s</strong> as a member from group <strong>%(group_id)s</strong>.',
            user_id  = str(kwargs['item']),
            group_id = str(kwargs['other'])
        )


class EnableView(HTMLMixin, SQLAlchemyMixin, ItemEnableView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for enabling existing user accounts.
    """
    methods = ['GET','POST']

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'action-enable-user'

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Enable user account &quot;%(item)s&quot;', item = kwargs['item'].login)

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_success`."""
        return gettext('User account <strong>%(item_id)s</strong> was successfully enabled.', item_id = str(kwargs['item']))

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext('Unable to enable user account <strong>%(item_id)s</strong>.', item_id = str(kwargs['item']))

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext('Canceled enabling user account <strong>%(item_id)s</strong>.', item_id = str(kwargs['item']))

    #---------------------------------------------------------------------------

    @classmethod
    def send_infomail(cls, account):
        """Send infomail about user account activation."""
        mail_locale = account.locale
        if not mail_locale:
            mail_locale = flask.current_app.config['BABEL_DEFAULT_LOCALE']

        with force_locale(mail_locale):
            msg = flask_mail.Message(
                gettext(
                    "[Mentat] Account activation - %(item_id)s",
                    item_id = account.login
                ),
                recipients = [account.email],
                bcc = flask.current_app.config['HAWAT_ADMINS']
            )
            msg.body = flask.render_template(
                'users/email_activation.txt',
                account = account
            )
            flask.current_app.mailer.send(msg)

    def do_after_action(self, item):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.do_after_action`."""
        self.send_infomail(item)


class DisableView(HTMLMixin, SQLAlchemyMixin, ItemDisableView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for deleting existing user accounts.
    """
    methods = ['GET','POST']

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'action-disable-user'

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Disable user account &quot;%(item)s&quot;', item = kwargs['item'].login)

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_success`."""
        return gettext('User account <strong>%(item_id)s</strong> was successfully disabled.', item_id = str(kwargs['item']))

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext('Unable to disable user account <strong>%(item_id)s</strong>.', item_id = str(kwargs['item']))

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext('Canceled disabling user account <strong>%(item_id)s</strong>.', item_id = str(kwargs['item']))


class DeleteView(HTMLMixin, SQLAlchemyMixin, ItemDeleteView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for deleting existing user accounts.
    """
    methods = ['GET','POST']

    authentication = True

    authorization = [hawat.acl.PERMISSION_ADMIN]

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'action-delete-user'

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Delete user account &quot;%(item)s&quot;', item = kwargs['item'].login)

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_success`."""
        return gettext('User account <strong>%(item_id)s</strong> was successfully and permanently deleted.', item_id = str(kwargs['item']))

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext('Unable to delete user account <strong>%(item_id)s</strong>.', item_id = str(kwargs['item']))

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext('Canceled deleting user account <strong>%(item_id)s</strong>.', item_id = str(kwargs['item']))


#-------------------------------------------------------------------------------


class UsersBlueprint(HawatBlueprint):
    """
    Hawat pluggable module - users.
    """

    @classmethod
    def get_module_title(cls):
        """*Implementation* of :py:func:`hawat.base.HawatBlueprint.get_module_title`."""
        return lazy_gettext('User account management pluggable module')

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
            position = 40,
            group = lazy_gettext('Object management'),
            view = ListView
        )
        app.menu_auth.add_entry(
            'view',
            'my_account',
            position = 10,
            view = MeView,
            params = lambda: {'item': flask_login.current_user}
        )

        app.set_infomailer('users.enable', EnableView.send_infomail)


#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`hawat.base.HawatBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = UsersBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates',
        url_prefix = '/{}'.format(BLUEPRINT_NAME)
    )

    hbp.register_view_class(ListView, '/list')
    hbp.register_view_class(CreateView, '/create')
    hbp.register_view_class(ShowView, '/<int:item_id>/show')
    hbp.register_view_class(MeView, '/me')
    hbp.register_view_class(UpdateView, '/<int:item_id>/update')
    hbp.register_view_class(AddMembershipView, '/<int:item_id>/add_membership/<int:other_id>')
    hbp.register_view_class(RemoveMembershipView, '/<int:item_id>/remove_membership/<int:other_id>')
    hbp.register_view_class(EnableView, '/<int:item_id>/enable')
    hbp.register_view_class(DisableView, '/<int:item_id>/disable')
    hbp.register_view_class(DeleteView, '/<int:item_id>/delete')

    return hbp
