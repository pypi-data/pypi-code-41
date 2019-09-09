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
--------------------------------------------------------------------------------

This Hawat pluggable module provides special authentication method, that is
particularly usable for developers and enables them to impersonate any user.

After enabling this module special authentication endpoint will be available
and will provide simple authentication form with list of all currently available
user accounts. It will be possible for that user to log in as any other user
without entering password.

This module is disabled by default in *production* environment and enabled by
default in *development* environment.

.. warning::

    This module must never ever be enabled on production systems, because it is
    a huge security risk and enables possible access control management violation.
    You have been warned!


Provided endpoints
--------------------------------------------------------------------------------

``/auth_dev/login``
    Page providing special developer login form.

    * *Authentication:* no authentication
    * *Methods:* ``GET``, ``POST``
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import sys
import traceback
import sqlalchemy

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
from mentat.datatype.sqldb import UserModel, ItemChangeLogModel
import hawat.const
import hawat.forms
from hawat.base import HTMLMixin, SQLAlchemyMixin, SimpleView, RenderableView, HawatBlueprint
from hawat.blueprints.auth_dev.forms import LoginForm, RegisterUserAccountForm


BLUEPRINT_NAME = 'auth_dev'
"""Name of the blueprint as module global constant."""


class LoginView(HTMLMixin, SQLAlchemyMixin, SimpleView):
    """
    View enabling special developer login.
    """
    methods = ['GET', 'POST']

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'login'

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'login'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Developer login')

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    def dispatch_request(self):
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the *Flask* framework to service the request.
        """
        form = LoginForm()

        if form.validate_on_submit():
            dbsess = hawat.db.db_get().session
            try:
                user = dbsess.query(UserModel).filter(UserModel.login == form.login.data).one()

                if not user.enabled:
                    self.flash(
                        flask.Markup(gettext(
                            'Please be aware, that the account for user <strong>%(login)s (%(name)s)</strong> is currently disabled.',
                            login = user.login,
                            name = user.fullname
                        )),
                        hawat.const.HAWAT_FLASH_FAILURE
                    )

                flask_login.login_user(user)

                # Tell Flask-Principal the identity changed. Access to private method
                # _get_current_object is according to the Flask documentation:
                #   http://flask.pocoo.org/docs/1.0/reqcontext/#notes-on-proxies
                flask_principal.identity_changed.send(
                    flask.current_app._get_current_object(),   # pylint: disable=locally-disabled,protected-access
                    identity = flask_principal.Identity(user.get_id())
                )

                self.flash(
                    flask.Markup(gettext(
                        'You have been successfully logged in as <strong>%(user)s</strong>.',
                        user = str(user)
                    )),
                    hawat.const.HAWAT_FLASH_SUCCESS
                )
                self.logger.info(
                    "User '{}' successfully logged in with 'auth_dev'.".format(
                        user.login
                    )
                )

                # Redirect user back to original page.
                return self.redirect(
                    default_url = flask.url_for(
                        flask.current_app.config['HAWAT_LOGIN_REDIRECT']
                    )
                )

            except sqlalchemy.orm.exc.MultipleResultsFound:
                self.logger.error(
                    "Multiple results found for user login '{}'.".format(
                        form.login.data
                    )
                )
                self.abort(500)

            except sqlalchemy.orm.exc.NoResultFound:
                self.flash(
                    gettext('You have entered wrong login credentials.'),
                    hawat.const.HAWAT_FLASH_FAILURE
                )

            except Exception:  # pylint: disable=locally-disabled,broad-except
                self.flash(
                    flask.Markup(gettext(
                        "Unable to perform developer login as <strong>%(user)s</strong>.",
                        user = str(form.login.data)
                    )),
                    hawat.const.HAWAT_FLASH_FAILURE
                )
                flask.current_app.log_exception_with_label(
                    traceback.TracebackException(*sys.exc_info()),
                    'Unable to perform developer login.',
                )

        self.response_context.update(
            form = form,
            next = hawat.forms.get_redirect_target()
        )
        return self.generate_response()


class RegisterView(HTMLMixin, SQLAlchemyMixin, RenderableView):
    """
    View responsible for registering new user account into application.
    """
    methods = ['GET', 'POST']

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'register'

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'register'

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Register (dev)')

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('User account registration (dev)')

    @classmethod
    def get_view_template(cls):
        return '{}/registration.html'.format(BLUEPRINT_NAME)

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    @staticmethod
    def get_item_form():
        """
        Get user account registration form object.
        """
        roles = list(zip(flask.current_app.config['ROLES'], flask.current_app.config['ROLES']))
        locales = list(flask.current_app.config['SUPPORTED_LOCALES'].items())

        return RegisterUserAccountForm(
            choices_roles = roles,
            choices_locales = locales
        )

    def changelog_log(self, item, json_state_before = '', json_state_after = ''):
        """
        Log item action into changelog. One of the method arguments is permitted
        to be left out. This enables logging create and delete actions.

        :param mentat.datatype.sqldb.MODEL item: Item that is being changed.
        :param str json_state_before: JSON representation of item state before action.
        :param str json_state_after: JSON representation of item state after action.
        """
        if not json_state_before and not json_state_after:
            raise ValueError("Invalid use of changelog_log() method, both of the arguments are null.")

        chlog = ItemChangeLogModel(
            model     = item.__class__.__name__,
            model_id  = item.id,
            endpoint  = self.get_view_endpoint(),
            module    = self.module_name,
            operation = self.get_view_name(),
            before    = json_state_before,
            after     = json_state_after
        )
        chlog.calculate_diff()
        self.dbsession.add(chlog)
        self.dbsession.commit()

    def dispatch_request(self):
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the *Flask* framework to service the request.
        """
        form = self.get_item_form()

        if form.validate_on_submit():
            form_data = form.data

            if form_data[hawat.const.HAWAT_FORM_ACTION_CANCEL]:
                self.flash(
                    gettext('Account registration canceled.'),
                    hawat.const.HAWAT_FLASH_INFO
                )
                return self.redirect(
                    default_url = flask.url_for(
                        flask.current_app.config['HAWAT_ENDPOINT_HOME']
                    )
                )

            if form_data[hawat.const.HAWAT_FORM_ACTION_SUBMIT]:
                try:
                    # Populate the user object from form data and make sure the
                    # account has default 'user' role and is disabled by default.
                    item = self.dbmodel()
                    form.populate_obj(item)
                    item.roles = [hawat.const.HAWAT_ROLE_USER]
                    item.enabled = False

                    self.dbsession.add(item)
                    self.dbsession.commit()

                    # Log the item creation into changelog.
                    self.changelog_log(item, '', item.to_json())

                    # Send information about new account registration to system
                    # admins. Use default locale for email content translations.
                    mail_locale = flask.current_app.config['BABEL_DEFAULT_LOCALE']
                    with force_locale(mail_locale):
                        msg = flask_mail.Message(
                            gettext(
                                "[Mentat] Account registration (dev) - %(item_id)s",
                                item_id = item.login
                            ),
                            recipients = flask.current_app.config['HAWAT_ADMINS']
                        )
                        msg.body = flask.render_template(
                            'auth_env/email_registration_admins.txt',
                            account = item,
                            justification = form_data['justification']
                        )
                        flask.current_app.mailer.send(msg)

                    # Send information about new account registration to the user.
                    # Use user`s locale for email content translations.
                    mail_locale = item.locale
                    if not mail_locale:
                        mail_locale = flask.current_app.config['BABEL_DEFAULT_LOCALE']
                    with force_locale(mail_locale):
                        msg = flask_mail.Message(
                            gettext(
                                "[Mentat] Account registration (dev) - %(item_id)s",
                                item_id = item.login
                            ),
                            recipients = [item.email]
                        )
                        msg.body = flask.render_template(
                            'auth_env/email_registration_user.txt',
                            account = item,
                            justification = form_data['justification']
                        )
                        flask.current_app.mailer.send(msg)

                    self.flash(
                        flask.Markup(gettext(
                            'User account <strong>%(login)s (%(name)s)</strong> was successfully registered.',
                            login = item.login,
                            name = item.fullname
                        )),
                        hawat.const.HAWAT_FLASH_SUCCESS
                    )
                    return self.redirect(default_url = self.get_url_next())

                except Exception:  # pylint: disable=locally-disabled,broad-except
                    self.flash(
                        gettext('Unable to register new user account.'),
                        hawat.const.HAWAT_FLASH_FAILURE
                    )
                    flask.current_app.log_exception_with_label(
                        traceback.TracebackException(*sys.exc_info()),
                        'Unable to register new user account.',
                    )

        self.response_context.update(
            form_url = flask.url_for('{}.{}'.format(
                self.module_name,
                self.get_view_name()
            )),
            form = form
        )
        return self.generate_response()


#-------------------------------------------------------------------------------


class DevAuthBlueprint(HawatBlueprint):
    """
    Hawat pluggable module - special developer authentication (*auth_dev*).
    """

    @classmethod
    def get_module_title(cls):
        """*Implementation* of :py:func:`hawat.base.HawatBlueprint.get_module_title`."""
        return gettext('Developer authentication service')

    def register_app(self, app):
        """
        *Callback method*. Will be called from :py:func:`hawat.base.HawatApp.register_blueprint`
        method and can be used to customize the Flask application object. Possible
        use cases:

        * application menu customization

        :param hawat.base.HawatApp app: Flask application to be customize.
        """
        app.menu_anon.add_entry(
            'view',
            'login_dev',
            position = 20,
            view = LoginView,
            hidelegend = True
        )
        app.menu_anon.add_entry(
            'view',
            'register_dev',
            position = 60,
            view = RegisterView,
            hidelegend = True
        )
        app.menu_auth.add_entry(
            'view',
            'login_dev',
            position = 50,
            view = LoginView,
            hidelegend = True
        )
        app.menu_auth.add_entry(
            'view',
            'register_dev',
            position = 60,
            view = RegisterView,
            hidelegend = True
        )


#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`hawat.base.HawatBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = DevAuthBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates',
        url_prefix = '/{}'.format(BLUEPRINT_NAME)
    )

    hbp.register_view_class(LoginView,    '/login')
    hbp.register_view_class(RegisterView, '/register')

    return hbp
