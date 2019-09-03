#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains implementations of base classes for Hawat application pluggable
modules. Since the Hawat application is based on excelent `Flask <http://flask.pocoo.org/>`__
microframework, the modularity and extendability of the application is already
built-in as `blueprint <http://flask.pocoo.org/docs/0.12/blueprints/>`__
feature. However this module provides customized classes for application,
blueprint and view, that provide some additional features that are out of the
scope of bare Flask microframework.

Module contents
---------------

* :py:class:`HawatApp`
* :py:class:`HawatBlueprint`
* :py:class:`HTMLMixin`
* :py:class:`AJAXMixin`

    * :py:class:`SnippetMixin`

* :py:class:`SQLAlchemyMixin`
* :py:class:`PsycopgMixin`
* :py:class:`BaseView`

    * :py:class:`FileNameView`
    * :py:class:`FileIdView`
    * :py:class:`RenderableView`

        * :py:class:`SimpleView`
        * :py:class:`BaseSearchView`
        * :py:class:`ItemListView`
        * :py:class:`ItemShowView`
        * :py:class:`ItemActionView`

            * :py:class:`ItemCreateView`
            * :py:class:`ItemCreateForView`
            * :py:class:`ItemUpdateView`
            * :py:class:`ItemDeleteView`
            * :py:class:`ItemChangeView`

                * :py:class:`ItemEnableView`
                * :py:class:`ItemDisableView`
                * :py:class:`ItemObjectRelationView`
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import re
import sys
import copy
import collections
import datetime
import weakref
import traceback
import sqlalchemy

#
# Flask related modules.
#
import werkzeug.routing
import werkzeug.utils
import flask
import flask.app
import flask.views
import flask_login
from flask_babel import gettext

#
# Custom modules.
#
import hawat.const
import hawat.menu
import hawat.db
import hawat.errors
from hawat.forms import get_redirect_target, ItemActionConfirmForm

import mentat.services.eventstorage
from mentat.datatype.sqldb import ItemChangeLogModel


class HawatAppException(Exception):
    """
    Custom class for Hawat application exceptions.
    """


class URLParamsBuilder:
    """
    Small utility class for building URL parameter dictionaries for various view
    endpoints.

    .. note::

        This class is still proof of concept and work in progress.
    """
    def __init__(self, skeleton = None):
        self.rules = []
        self.kwrules = {}
        self.skeleton = skeleton or {}

    @staticmethod
    def _add_scalar(dst, key, val):
        if val is not None:
            dst[key] = val

    @staticmethod
    def _add_vector(dst, key, val):
        if val is not None:
            dst.setdefault(key, []).append(val)

    def add_rule(self, key, as_list = False, optional = False):
        """
        Add new rule to URL parameter builder.

        :param str key: Name of the rule key.
        :param bool as_list: Indication that the rule parameter is a list of multiple values.
        :param bool optional: Indication that the rule parameter is optional.
        """
        if as_list:
            rule = [key, self._add_vector, True, optional]
            self.rules.append(rule)
        else:
            rule = [key, self._add_scalar, False, optional]
            self.rules.append(rule)
        return self

    def add_kwrule(self, key, as_list = False, optional = False):
        """
        Add new keyword rule to URL parameter builder.

        :param str key: Name of the rule key.
        :param bool as_list: Indication that the rule parameter is a list of multiple values.
        :param bool optional: Indication that the rule parameter is optional.
        """
        if as_list:
            rule = [key, self._add_vector, True, optional]
            self.kwrules[key] = rule
        else:
            rule = [key, self._add_scalar, False, optional]
            self.kwrules[key] = rule
        return self

    def get_params(self, *args, **kwargs):
        """
        Get URL parameters as dictionary with filled-in values.
        """
        tmp = copy.deepcopy(self.skeleton)
        for idx, rule in enumerate(self.rules):
            try:
                rule[1](tmp, rule[0], args[idx])
            except IndexError:
                if not rule[3]:
                    raise
        for key, rule in self.kwrules.items():
            if key in kwargs:
                rule[1](tmp, rule[0], kwargs[key])
        return tmp


class HawatUtils:
    """
    Small utility method class to enable use of those methods both in the view
    classes and in the Jinja2 templates.
    """
    @staticmethod
    def get_datetime_window(tiid, wtype, moment = None):
        """
        Get timestamp of given type ('current', 'previous', 'next') for given time
        window and optional time moment.
        """
        try:
            if not moment:
                moment = datetime.datetime.utcnow()
            return hawat.const.TIME_WINDOWS[tiid][wtype](moment)
        except:  # pylint: disable=locally-disabled,bare-except
            return None


class HawatApp(flask.Flask):
    """
    Custom implementation of :py:class:`flask.Flask` class. This class extends the
    capabilities of the base class with following additional features:

    Configuration based blueprint registration
        The application configuration file contains a directive describing list
        of requested blueprints/modules, that should be registered into the
        application. This enables administrator to very easily fine tune the
        application setup for each installation. See the :py:func:`hawat.base.HawatApp.register_blueprints`
        for more information on the topic.

    Application main menu management
        The application provides three distinct menus, that are at a disposal for
        blueprint/module designer.

    Mentat config access
        The application provides access to Mentat`s core configurations.
    """

    def __init__(self, import_name, **kwargs):
        super().__init__(import_name, **kwargs)

        self.menu_main = hawat.menu.Menu()
        self.menu_auth = hawat.menu.Menu()
        self.menu_anon = hawat.menu.Menu()
        self.csrf      = None

        self.view_classes = {}
        self.resources    = {}
        self.csag         = {}
        self.oads         = {}
        self.infomailers  = {}

    @property
    def mconfig(self):
        """
        Return Mentat specific configuration sub-dictionary.
        """
        return self.config[hawat.const.CFGKEY_MENTAT_CORE]

    @property
    def icons(self):
        """
        Application icon registry.
        """
        return hawat.const.FA_ICONS

    @flask.app.setupmethod
    def add_url_rule(self, rule, endpoint = None, view_func = None, provide_automatic_options = None, **options):
        """
        Reimplementation of :py:func:`flask.Flask.add_url_rule` method. This method
        is capable of disabling selected application endpoints. Keep in mind, that
        some URL rules (like application global 'static' endpoint) are created during
        the :py:func:`flask.app.Flask.__init__` method and cannot be disabled,
        because at that point the configuration of the application is not yet loaded.
        """
        if self.config.get('DISABLED_ENDPOINTS', None) and self.config['DISABLED_ENDPOINTS'] and endpoint:
            if endpoint in self.config['DISABLED_ENDPOINTS']:
                self.logger.warning(
                    "Application endpoint '%s' is disabled by configuration.",
                    endpoint
                )
                return
        super().add_url_rule(rule, endpoint, view_func, provide_automatic_options, **options)

    def register_blueprint(self, blueprint, **options):
        """
        Reimplementation of :py:func:`flask.Flask.register_blueprint` method. This
        method will perform standart blueprint registration and on top of that will
        perform following additional tasks:

            * Register blueprint into custom internal registry. The registry lies
              within application`s ``config`` under key :py:const:`hawat.const.CFGKEY_HAWAT_BLUEPRINTS`.
            * Call blueprint`s ``register_app`` method, if available, with ``self`` as only argument.

        :param hawat.base.HawatBlueprint blueprint: Blueprint to be registered.
        :param dict options: Additional options, will be passed down to :py:func:`flask.Flask.register_blueprint`.
        """
        super().register_blueprint(blueprint, **options)

        if isinstance(blueprint, HawatBlueprint):
            self.config.setdefault(
                hawat.const.CFGKEY_HAWAT_BLUEPRINTS,
                collections.OrderedDict()
            ).setdefault(blueprint.name, blueprint)

            if hasattr(blueprint, 'register_app'):
                blueprint.register_app(self)

            self.view_classes.update(blueprint.view_classes)

    def register_blueprints(self):
        """
        Register all configured application blueprints. The configuration comes
        from :py:const:`hawat.const.CFGKEY_ENABLED_BLUEPRINTS` configuration
        subkey, which must contain list of string names of required blueprints.
        The blueprint module must provide ``get_blueprint`` factory method, that
        must return valid instance of :py:class:`hawat.base.HawatBlueprint`. This
        method will call the :py:func:`hawat.base.HawatApp.register_blueprint` for
        each blueprint, that is being registered into the application.

        :raises hawat.base.HawatAppException: In case the factory method ``get_blueprint`` is not provided by loaded module.
        """
        for name in self.config[hawat.const.CFGKEY_ENABLED_BLUEPRINTS]:
            mod = werkzeug.utils.import_string(name)
            if hasattr(mod, 'get_blueprint'):
                self.register_blueprint(mod.get_blueprint())
            else:
                raise HawatAppException("Invalid blueprint module '{}', does not provide the 'get_blueprint' factory method.".format(name))

    def log_exception_with_label(self, tbexc, label = ''):
        """
        Log given exception traceback into application logger.
        """
        self.logger.error('%s%s', label, ''.join(tbexc.format()))  # pylint: disable=locally-disabled,no-member

    def has_endpoint(self, endpoint):
        """
        Check if given routing endpoint is available.

        :param str endpoint: Application routing endpoint.
        :return: ``True`` in case endpoint exists, ``False`` otherwise.
        :rtype: bool
        """
        return endpoint in self.view_classes

    def get_endpoint_class(self, endpoint, quiet = False):
        """
        Get reference to view class registered to given routing endpoint.

        :param str endpoint: Application routing endpoint.
        :return: Reference to view class.
        :rtype: class
        """
        if not endpoint in self.view_classes:
            if quiet:
                return None
            raise HawatAppException("Unknown endpoint name '{}'.".format(endpoint))
        return self.view_classes[endpoint]

    def can_access_endpoint(self, endpoint, **kwargs):
        """
        Check, that the current user can access given endpoint/view.

        :param str endpoint: Application routing endpoint.
        :param dict kwargs: Optional endpoint parameters.
        :return: ``True`` in case user can access the endpoint, ``False`` otherwise.
        :rtype: bool
        """
        try:
            view_class = self.get_endpoint_class(endpoint)

            # Reject unauthenticated users in case view requires authentication.
            if view_class.authentication:
                if not flask_login.current_user.is_authenticated:
                    return False

            # Check view authorization rules.
            if view_class.authorization:
                for auth_rule in view_class.authorization:
                    if not auth_rule.can():
                        return False

            # Check item action authorization callback, if exists.
            if hasattr(view_class, 'authorize_item_action'):
                if not view_class.authorize_item_action(**kwargs):
                    return False

            return True

        except HawatAppException:
            return False

    def get_resource(self, name):
        """
        Return reference to given registered resource.

        :param str name: Name of the resource.
        """
        return self.resources[name]()

    def set_resource(self, name, resource):
        """
        Store reference to given resource.

        :param str name: Name of the resource.
        :param resource: Resource to be registered.
        """
        self.resources[name] = weakref.ref(resource)

    def get_csag(self, group_name):
        """
        Return list of all registered context search actions for given group name
        (CSAG: Context Search Action Group).

        :param str group_name: Name of the group.
        :return: List of all registered context search actions.
        :rtype: list
        """
        return self.csag.get(group_name, [])

    def set_csag(self, group_name, title, view_class, params_builder):
        """
        Store new context search action for given group name (CSAG: Context Search
        Action Group).

        :param str group_name: Name of the group.
        :param str title: Title for the search action.
        :param class view_class: Associated view class.
        :param URLParamsBuilder params_builder: URL parameter builder for this action.
        """
        self.csag.setdefault(group_name, []).append({
            'title':  title,
            'view':   view_class,
            'params': params_builder
        })

    def set_csag_url(self, group_name, title, icon, url_builder):
        """
        Store new URL based context search action for given group name (CSAG: Context
        Search Action Group).

        :param str group_name: Name of the group.
        :param str title: Title for the search action.
        :param str icon: Icon for the search action.
        :param func url_builder: URL builder for this action.
        """
        self.csag.setdefault(group_name, []).append({
            'title': title,
            'icon':  icon,
            'url':   url_builder
        })

    def get_oads(self, group_name):
        """
        Return list of all registered object additional data services for given
        object group name (OADS: Additional Object Data Service).

        :param str group_name: Name of the group.
        :return: List of all object additional data services.
        :rtype: list
        """
        return self.oads.get(group_name, [])

    def set_oads(self, group_name, view_class, params_builder):
        """
        Store new object additional data services for given object group name
        (OADS: Additional Object Data Service).

        :param str group_name: Name of the group.
        :param class view_class: Associated view class.
        :param URLParamsBuilder params_builder: URL parameter builder for this action.
        """
        self.oads.setdefault(group_name, []).append({
            'view':     view_class,
            'params':   params_builder
        })

    def set_infomailer(self, name, mailer):
        """
        Register mailer handle to be usable by different web interface components.

        :param str name: Name of the informailer.
        :param callable mailer: Mailer handle.
        """
        self.infomailers.setdefault(name, []).append(mailer)

    def send_infomail(self, name, **kwargs):
        """
        Send emails through all registered infomailer handles.

        :param str name: Name of the informailer.
        :param **kwargs: Additional mailer arguments.
        """
        for mailer in self.infomailers[name]:
            mailer(**kwargs)


class HawatBlueprint(flask.Blueprint):
    """
    Custom implementation of :py:class:`flask.Blueprint` class. This class extends
    the capabilities of the base class with additional features:

        * Support for better integration into application and registration of view classes.
        * Support for custom tweaking of application object.
        * Support for custom style of authentication and authorization decorators
    """
    def __init__(self, name, import_name, **kwargs):
        super().__init__(name, import_name, **kwargs)

        self.view_classes = {}

    @classmethod
    def get_module_title(cls):
        """
        Get human readable name for this blueprint/module.

        :return: Name (short summary) of the blueprint/module.
        :rtype: str
        """
        raise NotImplementedError()

    def get_module_icon(self):
        """
        Return icon name for the module. Given name will be used as index to
        built-in icon registry.

        :return: Icon for the module.
        :rtype: str
        """
        return 'module-{}'.format(self.name).replace('_', '-')

    def register_app(self, app):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """
        *Hook method:* Custom callback, which will be called from
        :py:func:`hawat.base.HawatApp.register_blueprint` method and which can
        perform additional tweaking of Hawat application object.

        :param hawat.base.HawatApp app: Application object.
        """
        return

    def register_view_class(self, view_class, route_spec):
        """
        Register given view class into the internal blueprint registry.

        :param hawat.base.BaseView view_class: View class (not instance!)
        :param str route_spec: Routing information for the view.
        """
        view_class.module_ref  = weakref.ref(self)
        view_class.module_name = self.name

        # Obtain view function.
        view_func = view_class.as_view(view_class.get_view_name())

        # Apply authentication decorators (if requested).
        if view_class.authentication:
            view_func = flask_login.login_required(view_func)

        # Apply authorization decorators (if requested).
        if view_class.authorization:
            for auth in view_class.authorization:
                view_func = auth.require(403)(view_func)

        # Store the reference to view class to internal registry, so it can be
        # looked up within the application. This feature can be then used for
        # example for view link authorization (check, that current user has
        # privileges to access the view before generating link).
        self.view_classes[view_class.get_view_endpoint()] = view_class

        self.add_url_rule(route_spec, view_func = view_func)


#-------------------------------------------------------------------------------


class HTMLMixin:
    """
    Mixin class enabling rendering responses as HTML. Use it in your custom view
    classess based on :py:class:`hawat.base.RenderableView` to provide the
    ability to render Jinja2 template files into HTML responses.
    """

    @staticmethod
    def abort(status_code, message = None):  # pylint: disable=locally-disabled,unused-argument
        """
        Abort request processing with ``flask.abort`` function and custom status
        code and optional additional message. Return response as HTML error page.
        """
        flask.abort(status_code, message)

    def flash(self, message, category = 'info'):  # pylint: disable=locally-disabled,no-self-use
        """
        Display a one time message to the user. This implementation uses the
        :py:func:`flask.flash` method.

        :param str message: Message text.
        :param str category: Category of the flash message.
        """
        flask.flash(message, category)

    def redirect(self, target_url = None, default_url = None, exclude_url = None):  # pylint: disable=locally-disabled,no-self-use
        """
        Redirect user to different page. This implementation uses the
        :py:func:`flask.redirect` method to return valid HTTP redirection response.

        :param str target_url: Explicit redirection target, if possible.
        :param str default_url: Default redirection URL to use in case it cannot be autodetected from the response.
        :param str exclude_url: URL to which to never redirect (for example never redirect back to the item detail after the item deletion).
        """
        return flask.redirect(
            get_redirect_target(target_url, default_url, exclude_url)
        )

    def generate_response(self, view_template = None):
        """
        Generate the response appropriate for this view class, in this case HTML
        page.

        :param str view_template: Override internally preconfigured page template.
        """
        return flask.render_template(
            view_template or self.get_view_template(),
            **self.response_context
        )


class AJAXMixin:
    """
    Mixin class enabling rendering responses as JSON documents. Use it in your
    custom view classess based on based on :py:class:`hawat.base.RenderableView`
    to provide the ability to generate JSON responses.
    """
    KW_RESP_VIEW_TITLE     = 'view_title'
    KW_RESP_VIEW_ICON      = 'view_icon'
    KW_RESP_FLASH_MESSAGES = 'flash_messages'

    @staticmethod
    def abort(status_code, message = None):
        """
        Abort request processing with ``flask.abort`` function and custom status
        code and optional additional message. Return response as JSON document.
        """
        flask.abort(
            hawat.errors.api_error_response(
                status_code,
                message
            )
        )

    def flash(self, message, category = 'info'):  # pylint: disable=locally-disabled,no-self-use
        """
        Display a one time message to the user. This implementation uses the
        ``flash_messages`` subkey in returned JSON document to store the messages.

        :param str message: Message text.
        :param str category: Category of the flash message.
        """
        self.response_context.\
            setdefault(self.KW_RESP_FLASH_MESSAGES, {}).\
            setdefault(category, []).\
            append(message)

    def redirect(self, target_url = None, default_url = None, exclude_url = None):
        """
        Redirect user to different page. This implementation stores the redirection
        target to the JSON response.

        :param str target_url: Explicit redirection target, if possible.
        :param str default_url: Default redirection URL to use in case it cannot be autodetected from the response.
        :param str exclude_url: URL to which to never redirect (for example never redirect back to the item detail after the item deletion).
        """
        self.response_context.update(
            redirect = get_redirect_target(target_url, default_url, exclude_url)
        )
        return flask.jsonify(
            self.process_response_context()
        )

    def process_response_context(self):
        """
        Perform additional mangling with the response context before generating
        the response. This method can be useful to delete some context keys, that
        should not leave the server.

        :param dict response_context: Response context.
        :return: Possibly updated response context.
        :rtype: dict
        """
        # Prevent certain response context keys to appear in final response.
        for key in ('search_form', 'item_form'):
            try:
                del self.response_context[key]
            except KeyError:
                pass
        return self.response_context

    def generate_response(self, view_template = None):  # pylint: disable=locally-disabled,unused-argument
        """
        Generate the response appropriate for this view class, in this case JSON
        document.

        :param str view_template: Override internally preconfigured page template.
        """
        self.response_context[self.KW_RESP_VIEW_TITLE] = self.get_view_title()
        self.response_context[self.KW_RESP_VIEW_ICON]  = self.get_view_icon()

        flashed_messages = flask.get_flashed_messages(with_categories = True)
        if flashed_messages:
            for category, message in flashed_messages:
                self.response_context.\
                    setdefault(self.KW_RESP_FLASH_MESSAGES, {}).\
                    setdefault(category, []).\
                    append(message)

        return flask.jsonify(
            self.process_response_context()
        )


class SnippetMixin(AJAXMixin):
    """
    Mixin class enabling rendering responses as JSON documents. Use it in your
    custom view classess based on based on :py:class:`hawat.base.RenderableView`
    to provide the ability to generate JSON responses.
    """
    KW_RESP_SNIPPETS = 'snippets'
    KW_RESP_RENDER   = '_render'

    renders  = []
    snippets = []

    def _render_snippet(self, snippet_name, snippet_file = None):
        if not snippet_file:
            snippet_file = '{mod}/spt_{rdr}_{spt}.html'.format(
                mod = self.module_name,
                rdr = self.response_context[self.KW_RESP_RENDER],
                spt = snippet_name
            )
        self.response_context.setdefault(
            self.KW_RESP_SNIPPETS,
            {}
        )[snippet_name] = flask.render_template(
            snippet_file,
            **self.response_context
        )

    def _render_snippets(self, condition):
        if condition:
            for snippet in self.snippets:
                self._render_snippet(snippet)

    def flash(self, message, category = 'info'):  # pylint: disable=locally-disabled,no-self-use
        """
        Display a one time message to the user. This implementation uses the
        ``flash_messages`` subkey in returned JSON document to store the messages.

        :param str message: Message text.
        :param str category: Category of the flash message.
        """
        self.response_context.\
            setdefault(self.KW_RESP_SNIPPETS, {}).\
            setdefault(self.KW_RESP_FLASH_MESSAGES, {}).\
            setdefault(category, []).\
            append(
                flask.render_template(
                    'spt_flashmessage.html',
                    category = category,
                    message = message
                )
            )

    def generate_response(self, view_template = None):  # pylint: disable=locally-disabled,unused-argument
        """
        Generate the response appropriate for this view class, in this case JSON
        document containing ready to use HTML snippets.

        :param str view_template: Override internally preconfigured page template.
        """
        self.response_context[self.KW_RESP_VIEW_TITLE] = self.get_view_title()
        self.response_context[self.KW_RESP_VIEW_ICON]  = self.get_view_icon()
        self.response_context[self.KW_RESP_RENDER] = flask.request.args.get(
            'render',
            self.renders[0]
        ) or self.renders[0]
        if self.response_context[self.KW_RESP_RENDER] not in self.renders:
            self.abort(
                400,
                gettext(
                    'Invalid value %(val)s for snippet rendering parameter.',
                    val = self.response_context[self.KW_RESP_RENDER]
                )
            )

        flashed_messages = flask.get_flashed_messages(with_categories = True)
        if flashed_messages:
            for category, message in flashed_messages:
                self.response_context.\
                    setdefault(self.KW_RESP_SNIPPETS, {}).\
                    setdefault(self.KW_RESP_FLASH_MESSAGES, {}).\
                    setdefault(category, []).\
                    append(
                        flask.render_template(
                            'spt_flashmessage.html',
                            category = category,
                            message = message
                        )
                    )

        return flask.jsonify(
            self.process_response_context()
        )


class SQLAlchemyMixin:
    """
    Mixin class providing generic interface for interacting with SQL database
    backend through SQLAlchemy library.
    """

    @property
    def dbmodel(self):
        """
        This property must be implemented in each subclass to
        return reference to appropriate model class based on *SQLAlchemy* declarative
        base.
        """
        raise NotImplementedError()

    @property
    def search_by(self):
        """
        Return model`s attribute (column) according to which to search for the item.
        """
        return self.dbmodel.id

    @property
    def dbsession(self):
        """
        This property contains the reference to current *SQLAlchemy* database session.
        """
        return hawat.db.db_get().session

    def dbquery(self, dbmodel = None):
        """
        This property contains the reference to *SQLAlchemy* query object appropriate
        for particular ``dbmodel`` property.
        """
        return self.dbsession.query(dbmodel or self.dbmodel)

    def dbcolumn_min(self, dbcolumn):
        """
        Find and return the minimal value for given table column.
        """
        result = self.dbsession.query(sqlalchemy.func.min(dbcolumn)).one_or_none()
        if result:
            return result[0]
        return None

    def dbcolumn_max(self, dbcolumn):
        """
        Find and return the maximal value for given table column.
        """
        result = self.dbsession.query(sqlalchemy.func.max(dbcolumn)).one_or_none()
        if result:
            return result[0]
        return None

    @staticmethod
    def build_query(query, model, form_args):  # pylint: disable=locally-disabled,unused-argument
        """
        *Hook method*. Modify given query according to the given arguments.
        """
        return query

    def fetch(self, item_id):
        """
        Fetch item with given primary identifier from the database.
        """
        return self.dbquery().filter(self.search_by == item_id).first()

    def search(self, form_args):
        """
        Perform actual search with given query.
        """
        query = self.build_query(self.dbquery(), self.dbmodel, form_args)

        # Adjust the query according to the paging parameters.
        if 'limit' in form_args and form_args['limit']:
            query = query.limit(int(form_args['limit']))
            if 'page' in form_args and form_args['page'] and int(form_args['page']) > 1:
                query = query.offset((int(form_args['page']) - 1) * int(form_args['limit']))

        return query.all()


class PsycopgMixin:
    """
    Mixin class providing generic interface for interacting with SQL database
    backend through SQLAlchemy library.
    """

    def fetch(self, item_id):  # pylint: disable=locally-disabled,no-self-use
        """
        Fetch item with given primary identifier from the database.
        """
        return hawat.events.db_get().fetch_event(item_id)

    @staticmethod
    def get_db():
        """
        Get database connection service.

        :return: database connection service.
        :rtype: mentat.services.eventstorage.EventStorageService
        """
        return hawat.events.db_get()

    @staticmethod
    def get_event_factory():
        """
        Get reference to a item factory for converting database records into objects.
        """
        return mentat.services.eventstorage.record_to_idea

    @staticmethod
    def get_event_columns():
        """
        Get list of event database table column names.
        """
        return mentat.services.eventstorage.EVENT_COLUMNS

    def search(self, form_args):
        """
        Perform actual search of IDEA events using provided query arguments.

        :param dict form_args: Search query arguments.
        :return: Tuple containing number of items as integer and list of searched items.
        :rtype: tuple
        """
        items_count_total, items = hawat.events.db_get().search_events(
            form_args,
            event_factory = self.get_event_factory(),
            columns = self.get_event_columns()
        )
        self.response_context.update(
            sqlquery = hawat.events.db_get().cursor.lastquery.decode('utf-8')
        )
        return items


#-------------------------------------------------------------------------------


class BaseView(flask.views.View):
    """
    Base class for all custom Hawat application views.
    """

    module_ref = None
    """
    Weak reference to parent module of this view.
    """

    module_name = None
    """
    Name of the parent module (blueprint). Will be set up during the process
    of registering the view into the blueprint in :py:func:`hawat.base.HawatBlueprint.register_view_class`.
    """

    authentication = False
    """
    Similar to the ``decorators`` mechanism in Flask pluggable views, you may use
    this class variable to specify, that the view is protected by authentication.
    During the process of registering the view into the blueprint in
    :py:func:`hawat.base.HawatBlueprint.register_view_class` the view will be
    automatically decorated with :py:func:`flask_login.login_required` decorator.

    The advantage of using this in favor of ``decorators`` is that the application
    menu can automatically hide/show items inaccessible to current user.

    This is a scalar variable that must contain boolean ``True`` or ``False``.
    """

    authorization  = ()
    """
    Similar to the ``decorators`` mechanism in Flask pluggable views, you may use
    this class variable to specify, that the view is protected by authorization.
    During the process of registering the view into the blueprint in
    :py:func:`hawat.base.HawatBlueprint.register_view_class` the view will be
    automatically decorated with given authorization decorators.

    The advantage of using this in favor of ``decorators`` is that the application
    menu can automatically hide/show items inaccessible to current user.

    This is a list variable that must contain list of desired decorators.
    """

    @classmethod
    def get_view_name(cls):
        """
        Return unique name for the view. Name must be unique in the namespace of
        parent blueprint/module and should contain only characters ``[a-z0-9]``.
        It will be used for generating endpoint name for the view.

        *This method does not have any default implementation and must be overridden
        by a subclass.*

        :return: Name for the view.
        :rtype: str
        """
        raise NotImplementedError()

    @classmethod
    def get_view_endpoint(cls):
        """
        Return name of the routing endpoint for the view within the whole application.

        Default implementation generates the endpoint name by concatenating the
        module name and view name.

        :return: Routing endpoint for the view within the whole application.
        :rtype: str
        """
        return '{}.{}'.format(cls.module_name, cls.get_view_name())

    @classmethod
    def get_view_url(cls, **kwargs):
        """
        Return view URL.

        :param dict kwargs: Optional parameters.
        :return: URL for the view.
        :rtype: str
        """
        return flask.url_for(cls.get_view_endpoint(), **kwargs)

    @classmethod
    def get_view_icon(cls):
        """
        Return menu entry icon name for the view. Given name will be used as index
        to built-in icon registry.

        Default implementation generates the icon name by concatenating the prefix
        ``module-`` with module name.

        :return: Menu entry icon for the view.
        :rtype: str
        """
        return 'module-{}'.format(cls.module_name)

    @classmethod
    def get_view_title(cls, **kwargs):
        """
        Return title for the view, that will be displayed in the ``title`` tag of
        HTML ``head`` element and also as the content of page header in ``h2`` tag.

        Default implementation returns the return value of :py:func:`mydojo.base.BaseView.get_menu_title`
        method by default.

        :param dict kwargs: Optional parameters.
        :return: Title for the view.
        :rtype: str
        """
        raise NotImplementedError()

    @classmethod
    def get_menu_title(cls, **kwargs):
        """
        Return menu entry title for the view.

        Default implementation returns the return value of :py:func:`mydojo.base.BaseView.get_view_title`
        method by default.

        :param dict kwargs: Optional parameters.
        :return: Menu entry title for the view.
        :rtype: str
        """
        return cls.get_view_title(**kwargs)

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """
        Return menu entry legend for the view (menu entry hover tooltip).

        Default implementation returns the return value of :py:func:`mydojo.base.BaseView.get_menu_title`
        method by default.

        :param dict kwargs: Optional parameters.
        :return: Menu entry legend for the view.
        :rtype: str
        """
        return cls.get_menu_title(**kwargs)

    #---------------------------------------------------------------------------

    @staticmethod
    def can_access_endpoint(endpoint, **kwargs):
        """
        Check, that the current user can access given endpoint/view.

        :param str endpoint: Application routing endpoint.
        :param dict kwargs: Optional endpoint parameters.
        :return: ``True`` in case user can access the endpoint, ``False`` otherwise.
        :rtype: bool
        """
        return flask.current_app.can_access_endpoint(endpoint, **kwargs)

    @staticmethod
    def has_endpoint(endpoint):
        """
        Check if given routing endpoint is available within the application.

        :param str endpoint: Application routing endpoint.
        :return: ``True`` in case endpoint exists, ``False`` otherwise.
        :rtype: bool
        """
        return flask.current_app.has_endpoint(endpoint)

    @staticmethod
    def get_endpoint_class(endpoint):
        """
        Get reference to view class registered to given routing endpoint.

        :param str endpoint: Application routing endpoint.
        :return: Reference to view class.
        :rtype: class
        """
        return flask.current_app.get_endpoint_class(endpoint)

    #---------------------------------------------------------------------------

    @property
    def logger(self):
        """
        Return current application`s logger object.
        """
        return flask.current_app.logger


class FileNameView(BaseView):
    """
    Base class for direct file access views. These views can be used to access
    and serve files from arbitrary filesystem directories (that are accessible to
    application process). This can be very usefull for serving files like charts,
    that are periodically generated into configurable and changeable location.
    """

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'action-download'

    @classmethod
    def get_directory_path(cls):
        """
        Return absolute path to the directory, that will be used as a base path
        for serving files.

        *This method does not have any default implementation and must be overridden
        by a subclass.*

        :return: Absolute path to the directory for serving files.
        :rtype: str
        """
        raise NotImplementedError()

    @classmethod
    def validate_filename(cls, filename):
        """
        Validate given file name to prevent user from accessing restricted files.

        In default implementation all files pass the validation.

        :param str filename: Name of the file to be validated/filtered.
        :return: ``True`` in case file name is allowed, ``False`` otherwise.
        :rtype: bool
        """
        return bool(filename)

    def dispatch_request(self, filename):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.
        """
        if not self.validate_filename(filename):
            flask.abort(400)

        self.logger.info(
            "Serving file '{}' from directory '{}'.".format(
                filename,
                self.get_directory_path()
            )
        )
        return flask.send_from_directory(
            self.get_directory_path(),
            filename,
            as_attachment = True
        )


class FileIdView(BaseView):
    """
    Base class for indirrect file access views. These views can be used to access
    and serve files from arbitrary filesystem directories (that are accessible to
    application process). This can be very usefull for serving files like charts,
    that are periodically generated into configurable and changeable location.
    The difference between this view class and :py:class:`FileNameView` is,
    that is this case some kind of identifier is used to access the file and
    provided class method is responsible for translating this identifier into
    real file name.
    """

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'action-download'

    @classmethod
    def get_directory_path(cls, fileid, filetype):
        """
        This method must return absolute path to the directory, that will be
        used as a base path for serving files. Parameter ``fileid`` may be used
        internally to further customize the base directory, for example when
        serving some files places into subdirectories based on some part of the
        file name (for example to reduce total number of files in base directory).

        *This method does not have any default implementation and must be overridden
        by a subclass.*

        :param str fileid: Identifier of the requested file.
        :param str filetype: Type of the requested file.
        :return: Absolute path to the directory for serving files.
        :rtype: str
        """
        raise NotImplementedError()

    @classmethod
    def get_filename(cls, fileid, filetype):
        """
        This method must return actual name of the file based on given identifier
        and type.

        *This method does not have any default implementation and must be overridden
        by a subclass.*

        :param str fileid: Identifier of the requested file.
        :param str filetype: Type of the requested file.
        :return: Translated name of the file.
        :rtype: str
        """
        raise NotImplementedError()

    def dispatch_request(self, fileid, filetype):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.
        """
        basedirpath = self.get_directory_path(fileid, filetype)
        filename = self.get_filename(fileid, filetype)
        if not basedirpath or not filename:
            flask.abort(400)

        self.logger.info(
            "Serving file '{}' from directory '{}'.".format(
                filename,
                basedirpath
            )
        )
        return flask.send_from_directory(
            basedirpath,
            filename,
            as_attachment = True
        )


class RenderableView(BaseView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for all views, that are rendering content based on Jinja2 templates
    or returning JSON/XML data.
    """

    def __init__(self):
        self.response_context = {}

    def mark_time(self, ident, tag = 'default', label = 'Time mark', log = False):
        """
        Mark current time with given identifier and label for further analysis.
        This method can be usefull for measuring durations of various operations.
        """
        mark = [datetime.datetime.utcnow(), ident, tag, label]
        marks = self.response_context.setdefault('time_marks', [])
        marks.append(mark)

        if log:
            if len(marks) <= 1:
                self.logger.info(
                    'Mark {}:{} ({})'.format(*mark[1:])
                )
            else:
                self.logger.info(
                    'Mark {}:{} ({});delta={};delta0={}'.format(
                        *mark[1:],
                        (marks[-1][0]-marks[-2][0]).__str__(), # Time delta from last mark.
                        (marks[-1][0]-marks[0][0]).__str__()   # Time delta from first mark.
                    )
                )

    @classmethod
    def get_view_template(cls):
        """
        Return Jinja2 template file that should be used for rendering the view
        content. This default implementation works only in case the view class
        was properly registered into the parent blueprint/module with
        :py:func:`hawat.base.HawatBlueprint.register_view_class` method.

        :return: Jinja2 template file to use to render the view.
        :rtype: str
        """
        if cls.module_name:
            return '{}/{}.html'.format(cls.module_name, cls.get_view_name())
        raise RuntimeError("Unable to guess default view template, because module name was not yet set.")

    def do_before_response(self, **kwargs):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """
        This method will be called just before generating the response. By providing
        some meaningfull implementation you can use it for some simple item and
        response context mangling tasks.

        :param kwargs: Custom additional arguments.
        """

    def generate_response(self):
        """
        Generate the appropriate response from given response context.

        :param dict response_context: Response context as a dictionary
        """
        raise NotImplementedError()

    @staticmethod
    def abort(status_code, message = None):
        """
        Abort request processing with HTTP status code.
        """
        raise NotImplementedError()

    def flash(self, message, category = 'info'):
        """
        Flash information to the user.
        """
        raise NotImplementedError()

    def redirect(self, default_url = None, exclude_url = None):
        """
        Redirect user to different location.
        """
        raise NotImplementedError()


class SimpleView(RenderableView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for simple views. These are the most, well, simple views, that are
    rendering single template file or directly returning some JSON/XML data without
    any user parameters.

    In most use cases, it should be enough to just enhance the default implementation
    of :py:func:`hawat.base.RenderableView.get_response_context` to inject
    some additional variables into the template.
    """

    def dispatch_request(self):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.
        """
        self.do_before_response()
        return self.generate_response()


class BaseSearchView(RenderableView, HawatUtils):
    """
    Base class for search views.
    """
    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'search'

    #---------------------------------------------------------------------------

    @classmethod
    def get_quicksearch_by_time(cls):
        """
        Get default list of 'by time' quickseach items.
        """
        quicksearch_list = []
        for item in (
                ['14d', gettext('Search for last 14 days')],
                ['4w',  gettext('Search for last 4 weeks')],
                ['12w', gettext('Search for last 12 weeks')],
                ['td',  gettext('Search for today')],
                ['tw',  gettext('Search for this week')],
                ['tm',  gettext('Search for this month')],
                ['ty',  gettext('Search for this year')],
            ):
            try:
                dt_from = cls.get_datetime_window(
                    item[0],
                    'current'
                )
                dt_to = cls.get_datetime_window(
                    item[0],
                    'next',
                    dt_from
                )
                quicksearch_list.append(
                    {
                        'label': item[1],
                        'params': {
                            'dt_from': dt_from.isoformat(
                                sep = ' '
                            ),
                            'dt_to':   dt_to.isoformat(
                                sep = ' '
                            ),
                            'tiid':    item[0],
                            'submit':  gettext('Search')
                        }
                    }
                )
            except:  # pylint: disable=locally-disabled,bare-except
                pass

        return quicksearch_list

    @staticmethod
    def get_search_form(request_args):
        """
        *Hook method*. Must return instance of :py:mod:`flask_wtf.FlaskForm`
        appropriate for given search type.
        """
        raise NotImplementedError()

    @staticmethod
    def get_query_parameters(form, request_args):
        """
        Get query parameters by comparing contents of processed form data and
        original request arguments. Result of this method can be used for generating
        modified URLs back to current request. One of the use cases is the result
        pager/paginator.
        """
        params = {}
        for arg in request_args:
            if getattr(form, arg, None) and arg in request_args:
                # Handle multivalue request arguments separately
                # Resources:
                #   http://flask.pocoo.org/docs/1.0/api/#flask.Request.args
                #   http://werkzeug.pocoo.org/docs/0.14/datastructures/#werkzeug.datastructures.MultiDict
                try:
                    if form.is_multivalue(arg):
                        params[arg] = request_args.getlist(arg)
                    else:
                        params[arg] = request_args[arg]
                except AttributeError:
                    params[arg] = request_args[arg]
        return params

    def search(self, form_args):
        """
        Perform actual search with given query.
        """
        raise NotImplementedError()

    #---------------------------------------------------------------------------

    @classmethod
    def get_breadcrumbs_menu(cls):
        """
        Get breadcrumbs menu.
        """
        breadcrumbs_menu = hawat.menu.Menu()
        breadcrumbs_menu.add_entry(
            'endpoint',
            'home',
            endpoint = flask.current_app.config['HAWAT_ENDPOINT_HOME']
        )
        breadcrumbs_menu.add_entry(
            'endpoint',
            cls.get_view_name(),
            endpoint = '{}.{}'.format(cls.module_name, cls.get_view_name())
        )
        return breadcrumbs_menu

    @classmethod
    def get_action_menu(cls):
        """
        Get action menu for all items.
        """
        return None

    @classmethod
    def get_context_action_menu(cls):
        """*Implementation* of :py:func:`hawat.base.ItemListView.get_context_action_menu`."""
        context_action_menu = hawat.menu.Menu()
        context_action_menu.add_entry(
            'endpoint',
            'show',
            endpoint = '{}.show'.format(cls.module_name),
            hidetitle = True
        )
        return context_action_menu

    #---------------------------------------------------------------------------

    def do_before_search(self, form_data):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """
        This hook method will be called before search attempt.
        """

    def do_after_search(self, items):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """
        This hook method will be called after successfull search.
        """

    def dispatch_request(self):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.
        """
        form = self.get_search_form(flask.request.args)
        flask.g.search_form = form

        if hawat.const.HAWAT_FORM_ACTION_SUBMIT in flask.request.args:
            if form.validate():
                form_data = form.data

                self.mark_time(
                    'preprocess_begin',
                    tag = 'search',
                    label = 'Begin preprocessing for {}'.format(flask.request.full_path),
                    log = True
                )
                self.do_before_search(form_data)
                self.mark_time(
                    'preprocess_end',
                    tag = 'search',
                    label = 'Done preprocessing for {}'.format(flask.request.full_path),
                    log = True
                )

                try:
                    self.mark_time(
                        'search_begin',
                        tag = 'search',
                        label = 'Begin searching for {}'.format(flask.request.full_path),
                        log = True
                    )
                    items = self.search(form_data)
                    self.mark_time(
                        'search_end',
                        tag = 'search',
                        label = 'Done searching for {}, found: {}'.format(flask.request.full_path, len(items)),
                        log = True
                    )
                except Exception as err:  # pylint: disable=locally-disabled,broad-except
                    match = re.match('invalid IP4R value: "([^"]+)"', str(err))
                    if match:
                        self.flash(
                            flask.Markup(
                                gettext(
                                    'Invalid address value <strong>%(address)s</strong> in search form.',
                                    address = flask.escape(str(match.group(1)))
                                )
                            ),
                            hawat.const.HAWAT_FLASH_FAILURE
                        )
                    else:
                        raise

                self.response_context.update(
                    searched = True,
                    items = items,
                    items_count = len(items),
                    form_data = form_data
                )

                # Not all search forms support result paging.
                if 'page' in form_data:
                    self.response_context.update(
                        pager_index_low = ((form_data['page'] - 1) * form_data['limit']) + 1,
                        pager_index_high = ((form_data['page'] - 1) * form_data['limit']) + len(items),
                        pager_index_limit = ((form_data['page'] - 1) * form_data['limit']) + form_data['limit']
                    )

                self.mark_time(
                    'postprocess_begin',
                    tag = 'search',
                    label = 'Begin postprocessing for {}'.format(flask.request.full_path),
                    log = True
                )
                self.do_after_search(items)
                self.mark_time(
                    'postprocess_end',
                    tag = 'search',
                    label = 'Done postprocessing for {}'.format(flask.request.full_path),
                    log = True
                )
            else:
                self.response_context.update(
                    form_errors = [(field_name, err) for field_name, error_messages in form.errors.items() for err in error_messages]
                )

        self.response_context.update(
            query_params = self.get_query_parameters(form, flask.request.args),
            search_widget_item_limit = 3
        )
        self.do_before_response()
        return self.generate_response()


class ItemListView(RenderableView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item *list* views. These views provide quick and simple access
    to lists of all objects.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'list'

    @classmethod
    def get_breadcrumbs_menu(cls):
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
            endpoint = '{}.list'.format(cls.module_name)
        )
        return action_menu

    @classmethod
    def get_action_menu(cls):
        """
        Get action menu for all items.
        """
        return None

    @classmethod
    def get_context_action_menu(cls):
        """
        Get context action menu for particular item.
        """
        return None

    def search(self, form_args):
        """
        Perform actual search with given query.
        """
        raise NotImplementedError()

    def dispatch_request(self):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        List of all items will be retrieved from database and injected into template
        to be displayed to the user.
        """
        items = self.search({})

        self.response_context.update(
            items = items
        )

        self.do_before_response()
        return self.generate_response()


class ItemShowView(RenderableView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item *show* views. These views expect unique item identifier
    as parameter and are supposed to display specific information about single
    item.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'show'

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'action-show'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return gettext('Show')

    @classmethod
    def get_view_url(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_url`."""
        return flask.url_for(
            cls.get_view_endpoint(),
            item_id = kwargs['item'].get_id()
        )

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return gettext('Show')

    @classmethod
    def authorize_item_action(cls, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        """
        Perform access authorization for current user to particular item.
        """
        return True

    @classmethod
    def get_action_menu(cls):  # pylint: disable=locally-disabled,unused-argument
        """
        Get action menu for particular item.
        """
        return None

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
            endpoint = '{}.list'.format(cls.module_name),
            paramlist = []
        )
        action_menu.add_entry(
            'endpoint',
            'show',
            endpoint = '{}.show'.format(cls.module_name)
        )
        return action_menu

    def fetch(self, item_id):
        """
        Perform actual search with given query.
        """
        raise NotImplementedError()

    def dispatch_request(self, item_id):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        Single item with given unique identifier will be retrieved from database
        and injected into template to be displayed to the user.
        """
        item = self.fetch(item_id)
        if not item:
            self.abort(404)

        if not self.authorize_item_action(item = item):
            self.abort(403)

        self.response_context.update(
            item_id = item_id,
            item = item,
            search_widget_item_limit = 100
        )

        self.do_before_response()
        return self.generate_response()


class ItemActionView(RenderableView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item action views. These views perform various actions
    (create/update/delete) with given item class.
    """
    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'action-{}'.format(
            cls.get_view_name().replace('_', '-')
        )

    @classmethod
    def get_view_url(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_url`."""
        return flask.url_for(
            cls.get_view_endpoint(),
            item_id = kwargs['item'].get_id()
        )

    @classmethod
    def get_view_template(cls):
        """*Implementation* of :py:func:`hawat.base.RenderableView.get_view_template`."""
        return 'form_{}.html'.format(
            cls.get_view_name().replace('-', '_')
        )

    @staticmethod
    def get_message_success(**kwargs):
        """
        *Hook method*. Must return text for flash message in case of action *success*.
        The text may contain HTML characters and will be passed to :py:class:`flask.Markup`
        before being used, so to certain extend you may emphasize and customize the output.
        """
        raise NotImplementedError()

    @staticmethod
    def get_message_failure(**kwargs):
        """
        *Hook method*. Must return text for flash message in case of action *failure*.
        The text may contain HTML characters and will be passed to :py:class:`flask.Markup`
        before being used, so to certain extend you may emphasize and customize the output.
        """
        raise NotImplementedError()

    @staticmethod
    def get_message_cancel(**kwargs):
        """
        *Hook method*. Must return text for flash message in case of action *cancel*.
        The text may contain HTML characters and will be passed to :py:class:`flask.Markup`
        before being used, so to certain extend you may emphasize and customize the output.
        """
        raise NotImplementedError()

    def get_url_next(self):
        """
        *Hook method*. Must return URL for redirection after action *success*. In
        most cases there should be call for :py:func:`flask.url_for` function
        somewhere in this method.
        """
        try:
            return flask.url_for(
                '{}.{}'.format(self.module_name, 'list')
            )
        except werkzeug.routing.BuildError:
            return flask.url_for(
                flask.current_app.config['HAWAT_ENDPOINT_HOME']
            )

    def check_action_cancel(self, form, **kwargs):
        """
        Check the form for *cancel* button press and cancel the action.
        """
        if getattr(form, hawat.const.HAWAT_FORM_ACTION_CANCEL).data:
            self.flash(
                flask.Markup(self.get_message_cancel(**kwargs)),
                hawat.const.HAWAT_FLASH_INFO
            )
            return self.redirect(default_url = self.get_url_next())

        return None

    def do_before_action(self, item):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """
        *Hook method*. Will be called before any action handling tasks.
        """
        return

    def do_after_action(self, item):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """
        *Hook method*. Will be called after successfull action handling tasks.
        """
        return

    @classmethod
    def authorize_item_action(cls, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        """
        Perform access authorization for current user to particular item.
        """
        return True

    @property
    def dbsession(self):
        """
        This property contains the reference to current *SQLAlchemy* database session.
        """
        raise NotImplementedError()

    @property
    def dbmodel(self):
        """
        This property must be implemented in each subclass to
        return reference to appropriate model class based on *SQLAlchemy* declarative
        base.
        """
        raise NotImplementedError()

    def fetch(self, item_id):
        """
        Perform actual search with given query.
        """
        raise NotImplementedError()

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
            author    = flask_login.current_user._get_current_object(),  # pylint: disable=locally-disabled,protected-access
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


class ItemCreateView(ItemActionView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item *create* action views. These views create new items in
    database.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'create'

    @classmethod
    def get_view_template(cls):
        """
        Return Jinja2 template file that should be used for rendering the view
        content. This default implementation works only in case the view class
        was properly registered into the parent blueprint/module with
        :py:func:`hawat.base.HawatBlueprint.register_view_class` method.

        :return: Title for the view.
        :rtype: str
        """
        if cls.module_name:
            return '{}/creatupdate.html'.format(cls.module_name)
        raise RuntimeError("Unable to guess default view template, because module name was not yet set.")

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return gettext('Create')

    @classmethod
    def get_view_url(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_url`."""
        return flask.url_for(cls.get_view_endpoint())

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return gettext('Create')

    @staticmethod
    def get_item_form():
        """
        *Hook method*. Must return instance of :py:mod:`flask_wtf.FlaskForm`
        appropriate for given item class.
        """
        raise NotImplementedError()

    def dispatch_request(self):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        This method will attempt to validate the submitted form and create new
        instance of appropriate item from form data and finally store the item
        into the database.
        """
        if not self.authorize_item_action():
            self.abort(403)

        item = self.dbmodel()

        form = self.get_item_form()

        cancel_response = self.check_action_cancel(form)
        if cancel_response:
            return cancel_response

        if form.validate_on_submit():
            form_data = form.data
            form.populate_obj(item)

            self.do_before_action(item)

            if form_data[hawat.const.HAWAT_FORM_ACTION_SUBMIT]:
                try:
                    self.dbsession.add(item)
                    self.dbsession.commit()
                    self.do_after_action(item)

                    # Log the item creation into changelog.
                    self.changelog_log(item, '', item.to_json())

                    self.flash(
                        flask.Markup(self.get_message_success(item = item)),
                        hawat.const.HAWAT_FLASH_SUCCESS
                    )
                    return self.redirect(default_url = self.get_url_next())

                except Exception:  # pylint: disable=locally-disabled,broad-except
                    self.dbsession.rollback()
                    self.flash(
                        flask.Markup(self.get_message_failure()),
                        hawat.const.HAWAT_FLASH_FAILURE
                    )
                    flask.current_app.log_exception_with_label(
                        traceback.TracebackException(*sys.exc_info()),
                        self.get_message_failure()
                    )
                    return self.redirect(default_url = self.get_url_next())

        self.response_context.update(
            action_name = gettext('Create'),
            form_url    = flask.url_for('{}.{}'.format(self.module_name, self.get_view_name())),
            form        = form,
            item_action = hawat.const.HAWAT_ITEM_ACTION_CREATE,
            item        = item
        )

        self.do_before_response()
        return self.generate_response()


class HawatItemCreateForView(ItemActionView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item *createfor* action views. These views differ a little bit
    from *create* action views. They are used to create new items within database,
    but only for particular defined parent item. One example use case is creating
    network records for particular abuse group.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'createfor'

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'module-{}'.format(cls.module_name)

    @classmethod
    def get_view_template(cls):
        """
        Return Jinja2 template file that should be used for rendering the view
        content. This default implementation works only in case the view class
        was properly registered into the parent blueprint/module with
        :py:func:`hawat.base.HawatBlueprint.register_view_class` method.

        :return: Title for the view.
        :rtype: str
        """
        if cls.module_name:
            return '{}/creatupdate.html'.format(cls.module_name)
        raise RuntimeError("Unable to guess default view template, because module name was not yet set.")

    @property
    def dbmodel_par(self):
        """
        *Hook property*. This property must be implemented in each subclass to
        return reference to appropriate model class for parent objects and that
        is based on *SQLAlchemy* declarative base.
        """
        raise NotImplementedError()

    @property
    def dbquery_par(self):
        """
        This property contains the reference to *SQLAlchemy* query object appropriate
        for particular ``dbmodel_par`` property.
        """
        return self.dbsession.query(self.dbmodel_par)

    @staticmethod
    def get_item_form():
        """
        *Hook method*. Must return instance of :py:mod:`flask_wtf.FlaskForm`
        appropriate for given item class.
        """
        raise NotImplementedError()

    @staticmethod
    def add_parent_to_item(item, parent):
        """
        *Hook method*. Use given parent object for given item object. The actual
        operation to realize this relationship is highly dependent on current
        circumstance. It is up to the developer to perform correct set of actions
        to implement parent - child relationship for particular object types.
        """
        raise NotImplementedError()

    def dispatch_request(self, parent_id):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        This method will attempt to validate the submitted form and create new
        instance of appropriate item from form data and finally store the item
        into the database.
        """
        parent = self.dbquery_par.filter(self.dbmodel_par.id == parent_id).first_or_404()

        if not self.authorize_item_action(item = parent):
            self.abort(403)

        self.response_context.update(
            parent_id = parent_id,
            parent = parent
        )

        item = self.dbmodel()
        form = self.get_item_form()

        cancel_response = self.check_action_cancel(form, parent = parent)
        if cancel_response:
            return cancel_response

        if form.validate_on_submit():
            form_data = form.data
            form.populate_obj(item)

            self.do_before_action(item)
            self.add_parent_to_item(item, parent)

            if form_data[hawat.const.HAWAT_FORM_ACTION_SUBMIT]:
                try:
                    self.dbsession.add(item)
                    self.dbsession.commit()
                    self.do_after_action(item)

                    # Log the item creation into changelog.
                    self.changelog_log(item, '', item.to_json())

                    self.flash(
                        flask.Markup(self.get_message_success(item = item, parent = parent)),
                        hawat.const.HAWAT_FLASH_SUCCESS
                    )
                    return self.redirect(default_url = self.get_url_next())

                except Exception:  # pylint: disable=locally-disabled,broad-except
                    self.dbsession.rollback()
                    self.flash(
                        flask.Markup(self.get_message_failure(parent = parent)),
                        hawat.const.HAWAT_FLASH_FAILURE
                    )
                    flask.current_app.log_exception_with_label(
                        traceback.TracebackException(*sys.exc_info()),
                        self.get_message_failure(parent = parent)
                    )
                    return self.redirect(default_url = self.get_url_next())

        self.response_context.update(
            action_name = gettext('Create'),
            form_url    = flask.url_for('{}.{}'.format(self.module_name, self.get_view_name()), parent_id = parent_id),
            form        = form,
            item_action = hawat.const.HAWAT_ITEM_ACTION_CREATEFOR,
            item        = item
        )

        self.do_before_response()
        return self.generate_response()


class ItemUpdateView(ItemActionView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item *update* action views. These views update existing items
    in database.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'update'

    @classmethod
    def get_view_template(cls):
        """
        Return Jinja2 template file that should be used for rendering the view
        content. This default implementation works only in case the view class
        was properly registered into the parent blueprint/module with
        :py:func:`hawat.base.HawatBlueprint.register_view_class` method.

        :return: Title for the view.
        :rtype: str
        """
        if cls.module_name:
            return '{}/creatupdate.html'.format(cls.module_name)
        raise RuntimeError("Unable to guess default view template, because module name was not yet set.")

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return gettext('Update')

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return gettext('Update')

    @staticmethod
    def get_item_form(item):
        """
        *Hook method*. Must return instance of :py:mod:`flask_wtf.FlaskForm`
        appropriate for given item class.
        """
        raise NotImplementedError()

    def dispatch_request(self, item_id):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        This method will attempt to validate the submitted form and update the
        instance of appropriate item from form data and finally store the item
        back into the database.
        """
        item = self.fetch(item_id)
        if not item:
            self.abort(404)

        if not self.authorize_item_action(item = item):
            self.abort(403)

        self.dbsession.add(item)

        form = self.get_item_form(item)

        cancel_response = self.check_action_cancel(form, item = item)
        if cancel_response:
            return cancel_response

        item_json_before = item.to_json()

        if form.validate_on_submit():
            form_data = form.data
            form.populate_obj(item)

            self.do_before_action(item)

            if form_data[hawat.const.HAWAT_FORM_ACTION_SUBMIT]:
                try:
                    if item not in self.dbsession.dirty:
                        self.flash(
                            gettext('No changes detected, no update needed.'),
                            hawat.const.HAWAT_FLASH_INFO
                        )
                        return self.redirect(default_url = self.get_url_next())

                    self.dbsession.commit()
                    self.do_after_action(item)

                    # Log the item update into changelog.
                    self.changelog_log(item, item_json_before, item.to_json())

                    self.flash(
                        flask.Markup(self.get_message_success(item = item)),
                        hawat.const.HAWAT_FLASH_SUCCESS
                    )
                    return self.redirect(default_url = self.get_url_next())

                except Exception:  # pylint: disable=locally-disabled,broad-except
                    self.dbsession.rollback()
                    self.flash(
                        flask.Markup(self.get_message_failure(item = item)),
                        hawat.const.HAWAT_FLASH_FAILURE
                    )
                    flask.current_app.log_exception_with_label(
                        traceback.TracebackException(*sys.exc_info()),
                        self.get_message_failure(item = item)
                    )
                    return self.redirect(default_url = self.get_url_next())

        self.response_context.update(
            action_name = gettext('Update'),
            form_url    = flask.url_for('{}.{}'.format(self.module_name, self.get_view_name()), item_id = item_id),
            form        = form,
            item_action = hawat.const.HAWAT_ITEM_ACTION_UPDATE,
            item_id     = item_id,
            item        = item
        )

        self.do_before_response()
        return self.generate_response()


class ItemDeleteView(ItemActionView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item *delete* action views. These views delete existing items
    from database.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'delete'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return gettext('Delete')

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return gettext('Delete')

    def dispatch_request(self, item_id):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        This method will attempt to validate the submitted form and delete the
        instance of appropriate item from database in case user agreed to the
        item removal action.
        """
        item = self.fetch(item_id)
        if not item:
            self.abort(404)

        if not self.authorize_item_action(item = item):
            self.abort(403)

        form = ItemActionConfirmForm()

        cancel_response = self.check_action_cancel(form, item = item)
        if cancel_response:
            return cancel_response

        item_json_before = item.to_json()

        if form.validate_on_submit():
            form_data = form.data

            self.do_before_action(item)

            if form_data[hawat.const.HAWAT_FORM_ACTION_SUBMIT]:
                try:
                    self.dbsession.delete(item)
                    self.dbsession.commit()
                    self.do_after_action(item)

                    # Log the item deletion into changelog.
                    self.changelog_log(item, item_json_before, '')

                    self.flash(
                        flask.Markup(self.get_message_success(item = item)),
                        hawat.const.HAWAT_FLASH_SUCCESS
                    )
                    return self.redirect(
                        default_url = self.get_url_next(),
                        exclude_url = flask.url_for('{}.{}'.format(self.module_name, 'show'), item_id = item.id)
                    )

                except Exception:  # pylint: disable=locally-disabled,broad-except
                    self.dbsession.rollback()
                    self.flash(
                        flask.Markup(self.get_message_failure(item = item)),
                        hawat.const.HAWAT_FLASH_FAILURE
                    )
                    flask.current_app.log_exception_with_label(
                        traceback.TracebackException(*sys.exc_info()),
                        self.get_message_failure(item = item)
                    )
                    return self.redirect(default_url = self.get_url_next())

        self.response_context.update(
            confirm_form = form,
            confirm_url  = flask.url_for('{}.{}'.format(self.module_name, self.get_view_name()), item_id = item_id),
            item_name    = str(item),
            item_id      = item_id,
            item         = item
        )

        self.do_before_response()
        return self.generate_response()


class ItemChangeView(ItemActionView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for single item change views, that are doing some simple modification
    of item attribute, like enable/disable item, etc.
    """

    @classmethod
    def validate_item_change(cls, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        """
        Perform validation of particular change to given item.
        """
        return True

    @classmethod
    def change_item(cls, **kwargs):
        """
        *Hook method*: Change given item in any desired way.

        :param item: Item to be changed/modified.
        """
        raise NotImplementedError()

    def dispatch_request(self, item_id):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        This method will attempt to validate the submitted form, then perform
        arbitrary mangling action with the item and submit the changes to the
        database.
        """
        item = self.fetch(item_id)
        if not item:
            self.abort(404)

        if not self.authorize_item_action(item = item):
            self.abort(403)

        if not self.validate_item_change(item = item):
            self.abort(400)

        form = ItemActionConfirmForm()

        cancel_response = self.check_action_cancel(form, item = item)
        if cancel_response:
            return cancel_response

        item_json_before = item.to_json()

        if form.validate_on_submit():
            form_data = form.data

            self.do_before_action(item)

            if form_data[hawat.const.HAWAT_FORM_ACTION_SUBMIT]:
                try:
                    self.change_item(item = item)
                    if item not in self.dbsession.dirty:
                        self.flash(
                            gettext('No changes detected, no update needed.'),
                            hawat.const.HAWAT_FLASH_INFO
                        )
                        return self.redirect(default_url = self.get_url_next())

                    self.dbsession.commit()
                    self.do_after_action(item)

                    # Log the item change into changelog.
                    self.changelog_log(item, item_json_before, item.to_json())

                    self.flash(
                        flask.Markup(self.get_message_success(item = item)),
                        hawat.const.HAWAT_FLASH_SUCCESS
                    )
                    try:
                        exclude_url = flask.url_for('{}.{}'.format(self.module_name, 'show'), item_id = item.id)
                    except werkzeug.routing.BuildError:
                        exclude_url = None
                    return self.redirect(
                        default_url = self.get_url_next(),
                        exclude_url = exclude_url
                    )

                except Exception:  # pylint: disable=locally-disabled,broad-except
                    self.dbsession.rollback()
                    self.flash(
                        flask.Markup(self.get_message_failure(item = item)),
                        hawat.const.HAWAT_FLASH_FAILURE
                    )
                    flask.current_app.log_exception_with_label(
                        traceback.TracebackException(*sys.exc_info()),
                        self.get_message_failure(item = item)
                    )
                    return self.redirect(default_url = self.get_url_next())

        self.response_context.update(
            confirm_form = form,
            confirm_url  = flask.url_for('{}.{}'.format(self.module_name, self.get_view_name()), item_id = item_id),
            item_name    = str(item),
            item_id      = item_id,
            item         = item
        )

        self.do_before_response()
        return self.generate_response()


class ItemDisableView(ItemChangeView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item disabling views.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'disable'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return gettext('Disable')

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return gettext('Disable')

    @classmethod
    def validate_item_change(cls, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        """
        Perform validation of particular change to given item.
        """
        # Reject item change in case given item is already disabled.
        if not kwargs['item'].enabled:
            return False
        return True

    @classmethod
    def change_item(cls, **kwargs):
        """
        *Interface implementation* of :py:func:`hawat.base.ItemChangeView.change_item`.
        """
        kwargs['item'].enabled = False


class ItemEnableView(ItemChangeView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item enabling views.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'enable'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return gettext('Enable')

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return gettext('Enable')

    @classmethod
    def validate_item_change(cls, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        """
        Perform validation of particular change to given item.
        """
        # Reject item change in case given item is already enabled.
        if kwargs['item'].enabled:
            return False
        return True

    @classmethod
    def change_item(cls, **kwargs):
        """
        *Interface implementation* of :py:func:`hawat.base.ItemChangeView.change_item`.
        """
        kwargs['item'].enabled = True


class ItemObjectRelationView(ItemChangeView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item object relation action views.
    """
    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'module-{}'.format(cls.module_name)

    @classmethod
    def get_view_template(cls):
        """
        Return Jinja2 template file that should be used for rendering the view
        content. This default implementation works only in case the view class
        was properly registered into the parent blueprint/module with
        :py:func:`hawat.base.HawatBlueprint.register_view_class` method.

        :return: Title for the view.
        :rtype: str
        """
        if cls.module_name:
            return '{}/{}.html'.format(cls.module_name, cls.get_view_name())
        raise RuntimeError("Unable to guess default view template, because module name was not yet set.")

    @classmethod
    def get_view_url(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_url`."""
        return flask.url_for(
            cls.get_view_endpoint(),
            item_id  = kwargs['item'].get_id(),
            other_id = kwargs['other'].get_id()
        )

    @property
    def dbmodel_other(self):
        """
        *Hook property*. This property must be implemented in each subclass to
        return reference to appropriate model class for other objects and that
        is based on *SQLAlchemy* declarative base.
        """
        raise NotImplementedError()

    @property
    def dbquery_other(self):
        """
        This property contains the reference to *SQLAlchemy* query object appropriate
        for particular ``dbmodel_other`` property.
        """
        return self.dbsession.query(self.dbmodel_other)

    def dispatch_request(self, item_id, other_id):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        This method will attempt to validate the submitted form and create new
        instance of appropriate item from form data and finally store the item
        into the database.
        """
        item = self.fetch(item_id)
        if not item:
            self.abort(404)
        other = self.dbquery_other.filter(self.dbmodel_other.id == other_id).first()
        if not other:
            self.abort(404)

        if not self.authorize_item_action(item = item, other = other):
            self.abort(403)

        if not self.validate_item_change(item = item, other = other):
            self.abort(400)

        form = ItemActionConfirmForm()

        cancel_response = self.check_action_cancel(form, item = item, other = other)
        if cancel_response:
            return cancel_response

        item_json_before = item.to_json()

        if form.validate_on_submit():
            form_data = form.data

            self.do_before_action(item)

            if form_data[hawat.const.HAWAT_FORM_ACTION_SUBMIT]:
                try:
                    self.change_item(item = item, other = other)
                    if item not in self.dbsession.dirty:
                        self.flash(
                            gettext('No changes detected, no update needed.'),
                            hawat.const.HAWAT_FLASH_INFO
                        )
                        return self.redirect(default_url = self.get_url_next())

                    self.dbsession.commit()
                    self.do_after_action(item)

                    # Log the item change into changelog.
                    self.changelog_log(item, item_json_before, item.to_json())

                    self.flash(
                        flask.Markup(
                            self.get_message_success(
                                item = item,
                                other = other
                            )
                        ),
                        hawat.const.HAWAT_FLASH_SUCCESS
                    )
                    try:
                        exclude_url = flask.url_for(
                            '{}.{}'.format(self.module_name, 'show'),
                            item_id = item.id
                        )
                    except werkzeug.routing.BuildError:
                        exclude_url = None
                    return self.redirect(
                        default_url = self.get_url_next(),
                        exclude_url = exclude_url
                    )

                except Exception:  # pylint: disable=locally-disabled,broad-except
                    self.dbsession.rollback()
                    self.flash(
                        flask.Markup(
                            self.get_message_failure(item = item, other = other)
                        ),
                        hawat.const.HAWAT_FLASH_FAILURE
                    )
                    flask.current_app.log_exception_with_label(
                        traceback.TracebackException(*sys.exc_info()),
                        self.get_message_failure(item = item, other = other)
                    )
                    return self.redirect(default_url = self.get_url_next())

        self.response_context.update(
            confirm_form = form,
            confirm_url  = flask.url_for(
                '{}.{}'.format(
                    self.module_name,
                    self.get_view_name()
                ),
                item_id  = item_id,
                other_id = other_id
            ),
            item_name    = str(item),
            item_id      = item_id,
            item         = item,
            other_name   = str(other),
            other_id     = other_id,
            other        = other
        )

        self.do_before_response()
        return self.generate_response()
