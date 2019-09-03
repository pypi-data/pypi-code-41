#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains core application features for Hawat, the official user web
interface for the Mentat system.

The most important fetures of this module are the :py:func:`hawat.app.create_app`
and :py:func:`hawat.app.create_app_full` factory methods, that are responsible
for bootstrapping the whole application (see their documentation for more details).
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import sys
import traceback
import os
import uuid
import copy
import datetime
import jinja2
import yaml

#
# Flask related modules.
#
import flask
import flask_babel
#import flask_jsglue
import flask_migrate
import flask_login
import flask_principal

#
# Custom modules.
#
import mentat
import mentat._buildmeta
import mentat.idea.internal
import mentat.idea.jsondict
from mentat.datatype.sqldb import UserModel

import hawat.base
import hawat.const
import hawat.config
import hawat.acl
import hawat.log
import hawat.mailer
import hawat.db
import hawat.intl
import hawat.events
import hawat.errors
import hawat.utils
import hawat.jsglue


APP_NAME = 'hawat'
"""Name of the application as a constant for Flask."""


#-------------------------------------------------------------------------------


def create_app_full(
        config_dict   = None,
        config_object = 'hawat.config.ProductionConfig',
        config_file   = None,
        config_env    = 'FLASK_CONFIG_FILE'):
    """
    Factory function for building Hawat application. This function takes number of
    optional arguments, that can be used to create a very customized instance of
    Hawat application. This can be very usefull when extending applications`
    capabilities or for purposes of testing. Each of these arguments has default
    value for the most common application setup, so for disabling it entirely it
    is necessary to provide ``None`` as a value.

    :param dict config_dict: Initial default configurations.
    :param str config_object: Name of the class or module containing configurations.
    :param str config_file: Name of the file containing additional configurations.
    :param str config_env:  Name of the environment variable pointing to file containing configurations.
    :return: Hawat application
    :rtype: hawat.base.HawatApp
    """

    app = hawat.base.HawatApp(APP_NAME)

    if config_dict and isinstance(config_dict, dict):
        app.config.update(config_dict)
    app.config.update(
        hawat.config.get_app_root_relative_config()
    )
    if config_object:
        app.config.from_object(config_object)
    if config_file:
        app.config.from_pyfile(config_file)
    if config_env and os.getenv(config_env, None):
        app.config.from_envvar(config_env)

    _setup_app_logging(app)
    _setup_app_mailer(app)
    _setup_app_core(app)
    _setup_app_db(app)
    _setup_app_eventdb(app)
    _setup_app_auth(app)
    _setup_app_acl(app)
    _setup_app_intl(app)
    _setup_app_menu(app)
    _setup_app_blueprints(app)

    return app

def create_app():
    """
    Factory function for building Hawat application. This function does not take
    any arguments, any necessary customizations must be done using environment
    variables.

    :return: Hawat application
    :rtype: hawat.base.HawatApp
    """
    config_name = os.getenv('FLASK_CONFIG', 'default')
    config_file = hawat.config.get_default_config_file()
    if not os.path.isfile(config_file):
        config_file = None
    return create_app_full(
        config_object = hawat.config.CONFIG_MAP[config_name],
        config_file = config_file
    )


#-------------------------------------------------------------------------------


def _setup_app_logging(app):
    """
    Setup logging to file and via email for given Hawat application. Logging
    capabilities are adjustable by application configuration.

    :param hawat.base.HawatApp app: Hawat application to be modified.
    :return: Modified Hawat application
    :rtype: hawat.base.HawatApp
    """
    hawat.log.setup_logging_default(app)
    hawat.log.setup_logging_file(app)
    if not app.debug:
        hawat.log.setup_logging_email(app)

    return app


def _setup_app_mailer(app):
    """
    Setup mailer service for Hawat application.

    :param hawat.base.HawatApp app: Hawat application to be modified.
    :return: Modified Hawat application
    :rtype: hawat.base.HawatApp
    """
    hawat.mailer.MAILER.init_app(app)
    app.mailer = hawat.mailer.MAILER

    return app


def _setup_app_core(app):
    """
    Setup application core for given Hawat application. The application core
    contains following features:

        * Error handlers
        * Default routes
        * Additional custom Jinja template variables
        * Additional custom Jinja template macros

    :param hawat.base.HawatApp app: Hawat application to be modified.
    :return: Modified Hawat application
    :rtype: hawat.base.HawatApp
    """
    @app.errorhandler(400)
    def eh_badrequest(err):  # pylint: disable=locally-disabled,unused-variable
        """Flask error handler to be called to service HTTP 400 error."""
        return hawat.errors.error_handler_switch(400, err)

    @app.errorhandler(403)
    def eh_forbidden(err):  # pylint: disable=locally-disabled,unused-variable
        """Flask error handler to be called to service HTTP 403 error."""
        return hawat.errors.error_handler_switch(403, err)

    @app.errorhandler(404)
    def eh_page_not_found(err):  # pylint: disable=locally-disabled,unused-variable
        """Flask error handler to be called to service HTTP 404 error."""
        return hawat.errors.error_handler_switch(404, err)

    @app.errorhandler(405)
    def eh_method_not_allowed(err):  # pylint: disable=locally-disabled,unused-variable
        """Flask error handler to be called to service HTTP 405 error."""
        return hawat.errors.error_handler_switch(405, err)

    @app.errorhandler(410)
    def eh_gone(err):  # pylint: disable=locally-disabled,unused-variable
        """Flask error handler to be called to service HTTP 410 error."""
        return hawat.errors.error_handler_switch(410, err)

    @app.errorhandler(500)
    def eh_internal_server_error(err):  # pylint: disable=locally-disabled,unused-variable
        """Flask error handler to be called to service HTTP 500 error."""
        flask.current_app.logger.critical(
            "Internal Server Error:\n%s",
            ''.join(
                traceback.TracebackException(
                    *sys.exc_info()
                ).format()
            )
        )
        return hawat.errors.error_handler_switch(500, err)

    @app.before_request
    def before_request():  # pylint: disable=locally-disabled,unused-variable
        """
        Use Flask`s :py:func:`flask.Flask.before_request` hook for performing
        various usefull tasks before each request.
        """
        flask.g.requeststart = datetime.datetime.utcnow()

    @app.context_processor
    def jinja_inject_variables():  # pylint: disable=locally-disabled,unused-variable
        """
        Inject additional variables into Jinja2 global template namespace.
        """
        return dict(
            hawat_version           = mentat.__version__,
            hawat_bversion          = mentat._buildmeta.__bversion__,  # pylint: disable=locally-disabled,protected-access
            hawat_bversion_full     = mentat._buildmeta.__bversion_full__,  # pylint: disable=locally-disabled,protected-access
            hawat_current_app       = flask.current_app,
            hawat_current_menu_main = flask.current_app.menu_main,
            hawat_current_menu_auth = flask.current_app.menu_auth,
            hawat_current_menu_anon = flask.current_app.menu_anon,
            hawat_current_view      = app.get_endpoint_class(flask.request.endpoint, True),
            hawat_chart_dimensions  = 'height:700px',
            hawat_logger            = flask.current_app.logger
        )

    @app.context_processor
    def jinja2_inject_functions():  # pylint: disable=locally-disabled,unused-variable,too-many-locals
        """
        Register additional helpers into Jinja2 global template namespace.
        """
        def get_endpoints_dict():
            """
            Return dictionary of all registered application view endpoints.
            """
            return flask.current_app.view_classes

        def get_endpoint_class(endpoint):
            """
            Return class reference to given view endpoint.

            :param str endpoint: Name of the view endpoint.
            """
            return app.get_endpoint_class(endpoint)

        def check_endpoint_exists(endpoint):
            """
            Check, that given application view endpoint exists and is registered within
            the application.

            :param str endpoint: Name of the view endpoint.
            :return: ``True`` in case endpoint exists, ``False`` otherwise.
            :rtype: bool
            """
            return endpoint in app.view_classes

        def get_icon(icon_name, default_icon = 'missing-icon'):
            """
            Get HTML icon markup for given icon. The icon will be looked up in
            the :py:const:`hawat.const.FA_ICONS` lookup table.

            :param str icon_name: Name of the icon.
            :param str default_icon: Name of the default icon.
            :return: Icon including HTML markup.
            :rtype: flask.Markup
            """
            return flask.Markup(
                hawat.const.FA_ICONS.get(
                    icon_name,
                    hawat.const.FA_ICONS.get(default_icon)
                )
            )

        def get_module_icon(endpoint):
            """
            Get HTML icon markup for parent module of given view endpoint.

            :param str endpoint: Name of the view endpoint.
            :return: Icon including HTML markup.
            :rtype: flask.Markup
            """
            return flask.Markup(
                hawat.const.FA_ICONS[app.view_classes.get(endpoint).module_ref().get_module_icon()]
            )

        def get_endpoint_icon(endpoint):
            """
            Get HTML icon markup for given view endpoint.

            :param str endpoint: Name of the view endpoint.
            :return: Icon including HTML markup.
            :rtype: flask.Markup
            """
            return flask.Markup(
                hawat.const.FA_ICONS[app.view_classes.get(endpoint).get_view_icon()]
            )

        def get_csag(group):
            """
            Return list of all registered context search actions under given group.

            :param str group: Name of the group.
            :return: List of all registered context search actions.
            :rtype: list
            """
            return app.get_csag(group)

        def get_country_flag(country):
            """
            Get URL to static country flag file.

            :param str country: Name of the icon.
            :return: Country including HTML markup.
            :rtype: flask.Markup
            """
            if not hawat.const.CRE_COUNTRY_CODE.match(country):
                return get_icon('flag')

            return flask.Markup(
                '<img src="{}">'.format(
                    flask.url_for(
                        'design.static',
                        filename = 'images/country-flags/flags-iso/shiny/16/{}.png'.format(
                            country.upper()
                        )
                    )
                )
            )

        def get_timedelta(tstamp):
            """
            Get timedelta from current UTC time and given datetime object.

            :param datetime.datetime: Datetime of the lower timedelta boundary.
            :return: Timedelta object.
            :rtype: datetime.timedelta
            """
            return datetime.datetime.utcnow() - tstamp

        def get_datetime_utc():
            """
            Get current UTC datetime.

            :return: Curent UTC datetime.
            :rtype: datetime.datetime
            """
            return datetime.datetime.utcnow()

        def get_datetime_local():
            """
            Get current local timestamp.

            :return: Curent local timestamp.
            :rtype: datetime.datetime
            """
            return datetime.datetime.now()

        def get_reporting_interval_name(seconds):
            """
            Get a name of reporting interval for given time delta.

            :param int seconds: Time interval delta in seconds.
            :return: Name of the reporting interval.
            :rtype: str
            """
            return mentat.const.REPORTING_INTERVALS_INV[seconds]

        def check_file_exists(filename):
            """
            Check, that given file exists in the filesystem.

            :param str filename: Name of the file to check.
            :return: Existence flag as ``True`` or ``False``.
            :rtype: bool
            """
            return os.path.isfile(filename)

        def in_query_params(haystack, needles, on_true = True, on_false = False, on_empty = False):
            """
            Utility method for checking that any needle from given list of needles is
            present in given haystack.
            """
            if not haystack:
                return on_empty
            for needle in needles:
                if needle in haystack:
                    return on_true
            return on_false

        def generate_query_params(baseparams, updates):
            """
            Generate query parameters for GET method form.

            :param dict baseparams: Original query parameters.
            :param dict updates: Updates for query parameters.
            :return: Deep copy of original parameters modified with given updates.
            :rtype: dict
            """
            result = copy.deepcopy(baseparams)
            result.update(updates)
            return result

        def include_raw(filename):
            """
            Include given file in raw form directly into the generated content.
            This may be usefull for example for including JavaScript files
            directly into the HTML page.
            """
            return jinja2.Markup(
                app.jinja_loader.get_source(app.jinja_env, filename)[0]
            )

        def json_to_yaml(json_data):
            """
            Include given file in raw form directly into the generated content.
            This may be usefull for example for including JavaScript files
            directly into the HTML page.
            """
            return yaml.dump(
                yaml.load(
                    json_data
                ),
                default_flow_style=False
            )

        def get_uuid4():
            """
            Generate random UUID identifier.
            """
            return uuid.uuid4()

        def get_limit_counter(limit = None):
            """
            Get fresh instance of limit counter.
            """
            if not limit:
                limit = flask.current_app.config['HAWAT_LIMIT_AODS']
            return hawat.utils.LimitCounter(limit)

        return dict(
            get_endpoints_dict    = get_endpoints_dict,
            get_endpoint_class    = get_endpoint_class,
            check_endpoint_exists = check_endpoint_exists,

            get_icon          = get_icon,
            get_module_icon   = get_module_icon,
            get_endpoint_icon = get_endpoint_icon,
            get_csag          = get_csag,
            get_country_flag  = get_country_flag,

            get_timedelta       = get_timedelta,
            get_datetime_utc    = get_datetime_utc,
            get_datetime_local  = get_datetime_local,

            get_datetime_window = hawat.base.HawatUtils.get_datetime_window,

            get_reporting_interval_name = get_reporting_interval_name,

            check_file_exists = check_file_exists,

            in_query_params       = in_query_params,
            generate_query_params = generate_query_params,

            current_datetime_utc = datetime.datetime.utcnow(),

            include_raw       = include_raw,
            json_to_yaml      = json_to_yaml,
            get_uuid4         = get_uuid4,
            get_limit_counter = get_limit_counter
        )

    class HawatJSONEncoder(flask.json.JSONEncoder):
        """
        Custom JSON encoder for converting anything into JSON strings.
        """
        def default(self, obj):  # pylint: disable=locally-disabled,method-hidden,arguments-differ
            try:
                if isinstance(obj, mentat.idea.internal.Idea):
                    return mentat.idea.jsondict.Idea(obj).data
            except:  # pylint: disable=locally-disabled,bare-except
                pass
            try:
                if isinstance(obj, datetime.datetime):
                    return obj.isoformat() + 'Z'
            except:  # pylint: disable=locally-disabled,bare-except
                pass
            try:
                return obj.to_dict()
            except:  # pylint: disable=locally-disabled,bare-except
                pass
            try:
                return str(obj)
            except:  # pylint: disable=locally-disabled,bare-except
                pass
            return flask.json.JSONEncoder.default(self, obj)

    app.json_encoder = HawatJSONEncoder

    @app.route('/hawat-main.js')
    def mainjs():  # pylint: disable=locally-disabled,unused-variable
        """
        Default route for main application JavaScript file.
        """
        return flask.make_response(
            flask.render_template('hawat-main.js'),
            200,
            {'Content-Type': 'text/javascript'}
        )

    # Initialize JSGlue plugin for using `flask.url_for()` method in JavaScript.
    #jsglue = flask_jsglue.JSGlue()
    jsglue = hawat.jsglue.JSGlue()
    jsglue.init_app(app)

    return app


def _setup_app_db(app):
    """
    Setup application database service for given Hawat application.

    :param hawat.base.HawatApp app: Hawat application to be modified.
    :return: Modified Hawat application
    :rtype: hawat.base.HawatApp
    """
    dbcfg = hawat.db.db_settings(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = dbcfg['url']
    app.config['SQLALCHEMY_ECHO']         = dbcfg['echo']

    dbh = hawat.db.db_get()
    dbh.init_app(app)

    # Initialize database migration service and register it among the application
    # resources for possible future use.
    migrate = flask_migrate.Migrate(
        app       = app,
        db        = dbh,
        directory = os.path.realpath(
            os.path.join(
                os.path.dirname(
                    os.path.abspath(__file__)
                ),
                'migrations'
            )
        )
    )
    app.set_resource(hawat.const.RESOURCE_MIGRATE, migrate)

    app.logger.info("Connected to database via SQLAlchemy")

    return app


def _setup_app_eventdb(app):
    """
    Setup application database service for given Hawat application.

    :param hawat.base.HawatApp app: Hawat application to be modified.
    :return: Modified Hawat application
    :rtype: hawat.base.HawatApp
    """
    hawat.events.db_init(app)
    app.logger.info("Connected to event database")

    return app


def _setup_app_auth(app):
    """
    Setup application authentication features.

    :param hawat.base.HawatApp app: Hawat application to be modified.
    :return: Modified Hawat application
    :rtype: hawat.base.HawatApp
    """

    lim = flask_login.LoginManager()
    lim.init_app(app)
    lim.login_view = app.config['HAWAT_LOGIN_VIEW']
    lim.login_message = flask_babel.gettext("Please log in to access this page.")
    lim.login_message_category = app.config['HAWAT_LOGIN_MSGCAT']

    app.set_resource(hawat.const.RESOURCE_LOGIN_MANAGER, lim)

    @lim.user_loader
    def load_user(user_id):  # pylint: disable=locally-disabled,unused-variable
        """
        Flask-Login callback for loading current user`s data.
        """
        return hawat.db.db_get().session.query(UserModel).filter(UserModel.id == user_id).one_or_none()

    @app.route('/logout')
    @flask_login.login_required
    def logout():  # pylint: disable=locally-disabled,unused-variable
        """
        Flask-Login callback for logging out current user.
        """
        flask.current_app.logger.info(
            "User '{}' just logged out.".format(
                str(flask_login.current_user)
            )
        )
        flask_login.logout_user()
        flask.flash(
            flask_babel.gettext('You have been successfully logged out.'),
            hawat.const.HAWAT_FLASH_SUCCESS
        )

        # Remove session keys set by Flask-Principal.
        for key in ('identity.name', 'identity.auth_type'):
            flask.session.pop(key, None)

        # Tell Flask-Principal the identity changed.
        flask_principal.identity_changed.send(
            flask.current_app._get_current_object(),  # pylint: disable=locally-disabled,protected-access
            identity = flask_principal.AnonymousIdentity()
        )

        # Force user to index page.
        return flask.redirect(
            flask.url_for(
                flask.current_app.config['HAWAT_LOGOUT_REDIRECT']
            )
        )

    return app

def _setup_app_acl(app):
    """
    Setup application ACL features.

    :param hawat.base.HawatApp app: Hawat application to be modified.
    :return: Modified Hawat application
    :rtype: hawat.base.HawatApp
    """
    fpp = flask_principal.Principal(app, skip_static = True)
    app.set_resource(hawat.const.RESOURCE_PRINCIPAL, fpp)

    @flask_principal.identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):  # pylint: disable=locally-disabled,unused-variable,unused-argument
        """
        Flask-Principal callback for populating user identity object after login.
        """
        # Set the identity user object.
        identity.user = flask_login.current_user

        if not flask_login.current_user.is_authenticated:
            flask.current_app.logger.debug(
                "Loaded ACL identity for anonymous user '{}'.".format(
                    str(flask_login.current_user)
                )
            )
            return
        flask.current_app.logger.debug(
            "Loading ACL identity for user '{}'.".format(
                str(flask_login.current_user)
            )
        )

        # Add the UserNeed to the identity.
        if hasattr(flask_login.current_user, 'get_id'):
            identity.provides.add(
                flask_principal.UserNeed(flask_login.current_user.id)
            )

        # Assuming the User model has a list of roles, update the
        # identity with the roles that the user provides.
        if hasattr(flask_login.current_user, 'roles'):
            for role in flask_login.current_user.roles:
                identity.provides.add(
                    flask_principal.RoleNeed(role)
                )

        # Assuming the User model has a list of group memberships, update the
        # identity with the groups that the user is member of.
        if hasattr(flask_login.current_user, 'memberships'):
            for group in flask_login.current_user.memberships:
                identity.provides.add(
                    hawat.acl.MembershipNeed(group.id)
                )

        # Assuming the User model has a list of group managements, update the
        # identity with the groups that the user is manager of.
        if hasattr(flask_login.current_user, 'managements'):
            for group in flask_login.current_user.managements:
                identity.provides.add(
                    hawat.acl.ManagementNeed(group.id)
                )

    @app.context_processor
    def utility_acl_processor():  # pylint: disable=locally-disabled,unused-variable
        """
        Register additional helpers related to authorization into Jinja global
        namespace to enable them within the templates.
        """
        def can_access_endpoint(endpoint, item = None):
            """
            Check if currently logged-in user can access given endpoint/view.

            :param str endpoint: Name of the application endpoint.
            :param item: Optional item for additional validations.
            :return: ``True`` in case user can access the endpoint, ``False`` otherwise.
            :rtype: bool
            """
            return flask.current_app.can_access_endpoint(endpoint, item = item)

        def permission_can(permission_name):
            """
            Manually check currently logged-in user for given permission.

            :param str permission_name: Name of the permission.
            :return: Check result.
            :rtype: bool
            """
            return hawat.acl.PERMISSIONS[permission_name].can()

        def is_it_me(item):
            """
            Check if given user account is mine.
            """
            return item.id == flask_login.current_user.id

        return dict(
            can_access_endpoint = can_access_endpoint,
            permission_can      = permission_can,
            is_it_me            = is_it_me
        )

    return app


def _setup_app_intl(app):
    """
    Setup application`s internationalization sybsystem.

    :param hawat.base.HawatApp app: Hawat application to be modified.
    :return: Modified Hawat application
    :rtype: hawat.base.HawatApp
    """
    hawat.intl.BABEL.init_app(app)
    app.set_resource(hawat.const.RESOURCE_BABEL, hawat.intl.BABEL)
    app.cli.add_command(hawat.intl.WINTL_CLI)
    app.cli.add_command(hawat.intl.RINTL_CLI)

    @app.route('/locale/<code>')
    def locale(code):  # pylint: disable=locally-disabled,unused-variable
        """
        Application route providing users with the option of changing locale.
        """
        if code not in flask.current_app.config['SUPPORTED_LOCALES']:
            return flask.abort(404)

        if flask_login.current_user.is_authenticated:
            flask_login.current_user.locale = code
            # Make sure current user is in SQLAlchemy session. Turns out, this
            # step is not necessary and current user is already in session,
            # because it was fetched from database few moments ago.
            #hawat.db.db_session().add(flask_login.current_user)
            hawat.db.db_session().commit()

        flask.session['locale'] = code
        flask_babel.refresh()

        flask.flash(
            flask.Markup(flask_babel.gettext(
                'Locale was succesfully changed to <strong>%(lcln)s (%(lclc)s)</strong>.',
                lclc = code,
                lcln = flask.current_app.config['SUPPORTED_LOCALES'][code]
            )),
            hawat.const.HAWAT_FLASH_SUCCESS
        )

        # Redirect user back to original page.
        return flask.redirect(
            hawat.forms.get_redirect_target(
                default_url = flask.url_for(
                    flask.current_app.config['HAWAT_ENDPOINT_HOME']
                )
            )
        )

    @app.before_request
    def before_request():  # pylint: disable=locally-disabled,unused-variable
        """
        Use Flask`s :py:func:`flask.Flask.before_request` hook for storing
        currently selected locale and timezone to request`s session storage.
        """
        if 'locale' not in flask.session:
            flask.session['locale'] = hawat.intl.get_locale()
        if 'timezone' not in flask.session:
            flask.session['timezone'] = hawat.intl.get_timezone()

    @app.context_processor
    def utility_processor():  # pylint: disable=locally-disabled,unused-variable
        """
        Register additional internationalization helpers into Jinja global namespace.
        """

        return dict(
            babel_get_locale         = hawat.intl.get_locale,
            babel_get_timezone       = hawat.intl.get_timezone,
            babel_format_datetime    = flask_babel.format_datetime,
            babel_format_timedelta   = flask_babel.format_timedelta,
            babel_format_decimal     = flask_babel.format_decimal,
            babel_format_percent     = flask_babel.format_percent,
            babel_format_bytes       = hawat.intl.babel_format_bytes,
            babel_translate_locale   = hawat.intl.babel_translate_locale,
            babel_language_in_locale = hawat.intl.babel_language_in_locale
        )

    return app


def _setup_app_menu(app):
    """
    Setup default application menu skeleton.

    :param hawat.base.HawatApp app: Hawat application to be modified.
    :return: Modified Hawat application
    :rtype: hawat.base.HawatApp
    """
    for entry in app.config[hawat.const.CFGKEY_HAWAT_MENU_SKELETON]:
        app.menu_main.add_entry(**entry)

    return app


def _setup_app_blueprints(app):
    """
    Setup application blueprints.

    :param hawat.base.HawatApp app: Hawat application to be modified.
    :return: Modified Hawat application
    :rtype: hawat.base.HawatApp
    """
    app.register_blueprints()

    return app
