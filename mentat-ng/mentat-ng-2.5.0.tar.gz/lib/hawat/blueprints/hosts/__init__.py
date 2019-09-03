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

This pluggable module provides access to ...


.. _section-hawat-plugin-hosts-endpoints:

Provided endpoints
--------------------------------------------------------------------------------

``/hosts/search``
    Endpoint providing search form for ...

    * *Authentication:* login required
    * *Authorization:* any role
    * *Methods:* ``GET``
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime
import pytz

#
# Flask related modules.
#
import flask
from flask_babel import lazy_gettext

#
# Custom modules.
#
import mentat.stats.idea
import mentat.services.eventstorage
from mentat.const import tr_

import hawat.const
import hawat.events
import hawat.acl
from hawat.base import HTMLMixin, PsycopgMixin, AJAXMixin,\
    BaseSearchView, HawatBlueprint, URLParamsBuilder
from hawat.blueprints.hosts.forms import SimpleHostSearchForm


BLUEPRINT_NAME = 'hosts'
"""Name of the blueprint as module global constant."""


class AbstractSearchView(PsycopgMixin, BaseSearchView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for view responsible for searching...
    """
    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Hosts')

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Search hosts')

    @staticmethod
    def get_search_form(request_args):
        """
        *Interface implementation* of :py:func:`hawat.base.SearchView.get_search_form`.
        """
        # Get lists of available options for various event search form select fields.

        return SimpleHostSearchForm(
            request_args,
            meta = {'csrf': False}
        )

    def do_after_search(self, items):
        """
        *Interface implementation* of :py:func:`hawat.base.SearchView.do_after_search`.
        """
        self.logger.debug(
            "Calculating host statistics from %d records.",
            len(items)
        )
        if items:
            dt_from = self.response_context['form_data'].get('dt_from', None)
            if dt_from:
                dt_from = dt_from.astimezone(pytz.utc)
                dt_from = dt_from.replace(tzinfo = None)
            dt_to   = self.response_context['form_data'].get('dt_to', None)
            if dt_to:
                dt_to = dt_to.astimezone(pytz.utc)
                dt_to = dt_to.replace(tzinfo = None)

            if not dt_from and items:
                dt_from = self.get_db().search_column_with('detecttime')
            if not dt_to and items:
                dt_to = datetime.datetime.utcnow()

            self.response_context.update(
                statistics = mentat.stats.idea.evaluate_singlehost_events(
                    self.response_context['form_data'].get('host_addr'),
                    items,
                    dt_from = dt_from,
                    dt_to = dt_to,
                    max_count = flask.current_app.config['HAWAT_CHART_TIMELINE_MAXSTEPS']
                )
            )
            self.response_context.pop('items', None)

    def do_before_response(self, **kwargs):
        """*Implementation* of :py:func:`hawat.base.RenderableView.do_before_response`."""
        self.response_context.update(
            quicksearch_list = self.get_quicksearch_by_time()
        )

    @staticmethod
    def get_event_factory():
        return mentat.services.eventstorage.record_to_idea_ghost

    @staticmethod
    def get_event_columns():
        columns = list(mentat.services.eventstorage.EVENT_COLUMNS)
        columns.remove('event')
        return columns


class SearchView(HTMLMixin, AbstractSearchView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View responsible for querying `IDEA <https://idea.cesnet.cz/en/index>`__
    event database and presenting the results in the form of HTML page.
    """
    methods = ['GET']

    @classmethod
    def get_breadcrumbs_menu(cls):
        """
        *Interface implementation* of :py:func:`hawat.base.SearchView.get_breadcrumbs_menu`.
        """
        breadcrumbs_menu = hawat.menu.Menu()
        breadcrumbs_menu.add_entry(
            'endpoint',
            'home',
            endpoint = flask.current_app.config['HAWAT_ENDPOINT_HOME']
        )
        breadcrumbs_menu.add_entry(
            'endpoint',
            'search',
            endpoint = '{}.search'.format(cls.module_name)
        )
        return breadcrumbs_menu


class APISearchView(AJAXMixin, AbstractSearchView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View responsible for querying `IDEA <https://idea.cesnet.cz/en/index>`__
    event database and presenting the results in the form of JSON document.
    """
    methods = ['GET','POST']

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'apisearch'


#-------------------------------------------------------------------------------


class HostsBlueprint(HawatBlueprint):
    """
    Hawat pluggable module - Host overview.
    """

    @classmethod
    def get_module_title(cls):
        """*Implementation* of :py:func:`hawat.base.HawatBlueprint.get_module_title`."""
        return lazy_gettext('Host overview pluggable module')

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
            BLUEPRINT_NAME,
            position = 150,
            view = SearchView,
            resptitle = True
        )

        # Register context actions provided by this module.
        app.set_csag(
            hawat.const.HAWAT_CSAG_ADDRESS,
            tr_('Search for source <strong>%(name)s</strong> in host overview'),
            SearchView,
            URLParamsBuilder({'submit': tr_('Search')}).add_rule('host_addr').add_kwrule('dt_from', False, True).add_kwrule('dt_to', False, True)
        )

#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`hawat.base.HawatBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = HostsBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates'
    )

    hbp.register_view_class(SearchView,    '/{}/search'.format(BLUEPRINT_NAME))
    hbp.register_view_class(APISearchView, '/api/{}/search'.format(BLUEPRINT_NAME))

    return hbp
