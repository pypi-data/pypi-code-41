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

This pluggable module provides default authentication service based on server
environment. In this case the burden of performing actual authentication is
on the web server used for serving the web interface. The authentication module
then simply uses selected environment variables set up by the server after
successfull authentication.

This module also provides interface for automated user account registration. The
registration form is pre-filled with data gathered again from server environment.
The login may not be changed and the value fetched from environment is always used.
Other account attributes like name or email address may be tweaked by user before
submitting the registration form. Administrator and user are both notified via
email about the fact new account was just created.


Environment variables
--------------------------------------------------------------------------------

Currently following environment variables set up by the HTTP server are supported:

``eppn``,``REMOTE_USER`` (*MANDATORY*)
    The ``eppn`` server variable is set up by the _shibd_ daemon implementing the
    Shibboleth SSO service. The ``REMOTE_USER`` variable is set up by many
    authentication providers. This environment variable is of course mandatory
    and it is used as an account username (login).

``cn``,``givenName``,``sn`` (*OPTIONAL*)
    The ``cn`` server variable is used to fill in user`s name, when available.
    When not available, user`s name is constructed as contatenation of ``givenName``
    and ``sn`` server variables. When none of the above is available, user has to
    input his/her name manually during registration process.

``perunPreferredMail``,``mail`` (*OPTIONAL*)
    The ``perunPreferredMail`` server variable is used to fill in user`s email
    address, when available. When not available, the first email address from
    ``email`` server variable is used. When none of the above is available, user
    has to input his/her email manually during registration process.

``perunOrganizationName``,``o`` (*OPTIONAL*)
    The ``perunOrganizationName`` server variable is used to fill in user`s home
    organization name, when available. When not available, the value of ``o``
    server variable is used. When none of the above is available, user
    has to input his/her home organization name manually during registration process.


Provided endpoints
--------------------------------------------------------------------------------

``/auth_env/login``
    Page providing login functionality via server set environment variables.

    * *Authentication:* no authentication
    * *Methods:* ``GET``

``/auth_env/register``
    User account registration using server set environment variables.

    * *Authentication:* no authentication
    * *Methods:* ``GET``, ``POST``
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import sys
import datetime
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
import hawat.db
import hawat.forms
from hawat.base import HTMLMixin, SQLAlchemyMixin, RenderableView, HawatBlueprint
from hawat.blueprints.auth_env.forms import RegisterUserAccountForm


BLUEPRINT_NAME = 'auth_env'
"""Name of the blueprint as module global constant."""


class RegistrationException(Exception):
    """
    Exception describing problems with new user account registration.
    """
    def __init__(self, description):
        super().__init__()
        self.description = description

    def __str__(self):
        return str(self.description)


def get_login_from_environment():
    """
    Get user account login from appropriate environment variable(s).
    """
    return flask.request.environ.get(
        'eppn',
        flask.request.environ.get('REMOTE_USER', None)
    )

class LoginView(HTMLMixin, RenderableView):
    """
    View responsible for user login via application environment.
    """
    methods = ['GET']

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
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Environment login')

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Login (env)')

    def dispatch_request(self):
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the *Flask* framework to service the request.
        """
        user_login = get_login_from_environment()
        if not user_login:
            self.flash(
                gettext('User login was not received, unable to perform login process.'),
                hawat.const.HAWAT_FLASH_FAILURE
            )
            self.abort(403)

        dbsess = hawat.db.db_get().session
        try:
            user = dbsess.query(UserModel).filter(UserModel.login == user_login).one()

        except sqlalchemy.orm.exc.MultipleResultsFound:
            self.logger.error(
                "Multiple results found for user login '{}'.".format(
                    user_login
                )
            )
            flask.abort(500)

        except sqlalchemy.orm.exc.NoResultFound:
            self.flash(
                gettext('You have entered wrong login credentials.'),
                hawat.const.HAWAT_FLASH_FAILURE
            )
            self.abort(403)

        if not user.enabled:
            self.flash(
                flask.Markup(gettext(
                    'Your user account <strong>%(login)s (%(name)s)</strong> is currently disabled, you are not permitted to log in.',
                    login = user.login,
                    name = user.fullname
                )),
                hawat.const.HAWAT_FLASH_FAILURE
            )
            self.abort(403)

        flask_login.login_user(user)

        # Mark the login time into database.
        user.logintime = datetime.datetime.utcnow()
        dbsess.commit()

        # Tell Flask-Principal the identity changed. Access to private method
        # _get_current_object is according to the Flask documentation:
        #   http://flask.pocoo.org/docs/1.0/reqcontext/#notes-on-proxies
        flask_principal.identity_changed.send(
            flask.current_app._get_current_object(),   # pylint: disable=locally-disabled,protected-access
            identity = flask_principal.Identity(user.get_id())
        )

        self.flash(
            flask.Markup(gettext(
                'You have been successfully logged in as <strong>%(login)s (%(name)s)</strong>.',
                login = user.login,
                name = user.fullname
            )),
            hawat.const.HAWAT_FLASH_SUCCESS
        )
        self.logger.info(
            "User '{}' successfully logged in with 'auth_env'.".format(
                user.login
            )
        )

        # Redirect user back to original page.
        return self.redirect(
            default_url = flask.url_for(
                flask.current_app.config['HAWAT_LOGIN_REDIRECT']
            )
        )


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
        return lazy_gettext('Register')

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('User account registration')

    @classmethod
    def get_view_template(cls):
        return '{}/registration.html'.format(BLUEPRINT_NAME)

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    def get_user_from_env(self):
        """
        Get user object populated with information gathered from server environment
        variables.
        """
        item = self.dbmodel()

        # Fetch login from server authentication headers (mandatory).
        item.login = get_login_from_environment()
        if not item.login:
            raise RegistrationException(
                gettext("Unable to retrieve account login from your authentication provider.")
            )

        # Try to fetch name from server authentication headers (optional).
        try:
            item.fullname = flask.request.environ.get(
                'cn',
                '{} {}'.format(
                    flask.request.environ['givenName'],
                    flask.request.environ['sn']
                )
            )
        except (KeyError, AttributeError):
            pass

        # Try to fetch email from server authentication headers (optional).
        try:
            item.email = flask.request.environ.get(
                'perunPreferredMail',
                flask.request.environ['mail'].split(';')[0]
            )
        except (KeyError, AttributeError):
            pass

        # Try to fetch organization from server authentication headers (optional).
        try:
            item.organization = flask.request.environ.get(
                'perunOrganizationName',
                flask.request.environ['o']
            )
        except (KeyError, AttributeError):
            pass

        return item

    @staticmethod
    def get_item_form(item):
        """
        Get user account registration form object.
        """
        locales = list(flask.current_app.config['SUPPORTED_LOCALES'].items())

        return RegisterUserAccountForm(
            obj = item,
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
        self.response_context.update(apacheenv = flask.request.environ)
        item = None

        # Attempt to create user object from server environment variables.
        try:
            item = self.get_user_from_env()
            self.response_context.update(item = item)
        except RegistrationException as exc:
            self.response_context.update(failure_reason = exc)
            return self.generate_response(
                view_template = 'auth_env/registration_unavailable.html'
            )

        # Perhaps the account already exists.
        user = self.dbquery().filter(self.dbmodel.login == item.login).first()
        if user:
            self.flash(
                flask.Markup(gettext(
                    'User account <strong>%(item_id)s</strong> already exists.',
                    item_id = str(user)
                )),
                hawat.const.HAWAT_FLASH_FAILURE
            )
            self.response_context.update(item = user)
            return self.generate_response(
                view_template = 'auth_env/registration_show.html'
            )

        form = self.get_item_form(item)

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
                                "[Mentat] Account registration - %(item_id)s",
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
                                "[Mentat] Account registration - %(item_id)s",
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
                    return self.generate_response(
                        view_template = 'auth_env/registration_show.html'
                    )

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


class EnvAuthBlueprint(HawatBlueprint):
    """
    Hawat pluggable module - environment based authentication (*auth_env*).
    """

    @classmethod
    def get_module_title(cls):
        """*Implementation* of :py:func:`hawat.base.HawatBlueprint.get_module_title`."""
        return gettext('Environment authentication service')

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
            'login_env',
            position = 10,
            view = LoginView,
            hidelegend = True
        )
        app.menu_anon.add_entry(
            'view',
            'register_env',
            position = 50,
            view = RegisterView,
            hidelegend = True
        )


#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`hawat.base.HawatBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = EnvAuthBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates',
        url_prefix = '/{}'.format(BLUEPRINT_NAME)
    )

    hbp.register_view_class(LoginView,    '/login')
    hbp.register_view_class(RegisterView, '/register')

    return hbp
