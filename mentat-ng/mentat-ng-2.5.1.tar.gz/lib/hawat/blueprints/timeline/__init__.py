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

This pluggable module provides access to `IDEA <https://idea.cesnet.cz/en/index>`__
event timeline based visualisations.


.. _section-hawat-plugin-timeline-endpoints:

Provided endpoints
--------------------------------------------------------------------------------

``/timeline/search``
    Endpoint providing search form for timeline visualisations.

    * *Authentication:* login required
    * *Authorization:* any role
    * *Methods:* ``GET``

``/api/timeline/search``
    Endpoint providing API search form for for timeline visualisations. See appropriate
    :ref:`section <section-hawat-plugin-timeline-webapi-search>` below for the
    description of API interface.

    * *Authentication:* login required
    * *Authorization:* any role
    * *Methods:* ``GET``, ``POST``


.. _section-hawat-plugin-timeline-webapi:

Web API
--------------------------------------------------------------------------------

The API interface must be accessed by authenticated user. For web client side scripts
and applications it should be sufficient to use standard cookie-based authentication.
If you need to access the API from outside of the web browser, it might be usefull
to generate yourself an API access token and use the token based authentication.
For security reasons you have to use ``POST`` method for sending the token, otherwise
it might get logged on many different and insecure places (like web server logs).


.. _section-hawat-plugin-timeline-webapi-search:

API endpoint: **search**
````````````````````````````````````````````````````````````````````````````````

Endpoint URL: ``/api/timeline/search``

The URL for web API interface is available as normal endpoint to the user of the web
interface. This fact can be used to debug the queries interactively and then simply
copy them to another application. One might for example start with filling in the
search form in the ``/timeline/search`` endpoint. Once you are satisfied with the
result, you can simply switch the base URL to the ``/api/timeline/search`` endpoint
and you are all set.


**Available query parameters**:

Following parameters may be specified as standard HTTP query parameters:

*Time related query parameters*

``dt_from``
    * *Description:* Lower event detection time boundary
    * *Datatype:* Datetime in the format ``YYYY-MM-DD HH:MM:SS``, for example ``2018-01-01 00:00:00``
``dt_to``
    * *Description:* Upper event detection time boundary
    * *Datatype:* Datetime in the format ``YYYY-MM-DD HH:MM:SS``, for example ``2018-01-01 00:00:00``

*Origin related query parameters*

``host_addrs``
    * *Description:* List of required event sources or targets
    * *Datatype:* ``list of IP(4|6) addressess|networks|ranges as strings``
    * *Logical operation:* All given values are *OR*ed

*Common query parameters*

``submit``
    * *Description:* Search trigger button
    * *Datatype:* ``boolean`` or ``string`` (``True`` or ``"Search"``)
    * *Note:* This query parameter must be present to trigger the search


**Search examples**

* Default search query::

    /api/timeline/search?submit=Search

* Search without default lower detect time boundary::

    /api/timeline/search?dt_from=&submit=Search


**Response format**

JSON document, that will be received as a response for the search, can contain
following keys:

``form_data``
    * *Description:* This subkey is present in case search operation was triggered.
      It contains a dictionary with all query parameters described above and their
      appropriate processed values.
    * *Datatype:* ``dictionary``
``form_errors``
    * *Description:* This subkey is present in case there were any errors in the
      submitted search form and the search operation could not be triggered. So
      in another words the presence of this subkey is an indication of search failure.
      This subkey contains list of all form errors as pairs of strings: name of
      the form field and error description. The error description is localized
      according to the user`s preferences.
    * *Datatype:* ``list of tuples of strings``
    * *Example:* ``[["dt_from", "Not a valid datetime value"]]``
``items``
    * *Description:* This subkey is present in case search operation was triggered.
      It contains a list of IDEA messages that matched the query parameters. The
      messages are formated according to the `IDEA specification <https://idea.cesnet.cz/en/index>`__.
    * *Datatype:* ``list of IDEA messages as dictionaries``
``items_count``
    * *Description:* This subkey is present in case search operation was triggered.
      It contains the number of messages in the result set ``items``. By comparing
      this number with the value of ``pager_index_limit`` it is possible to determine,
      if the current result set/page is the last, or whether there are any more
      results.
    * *Datatype:* ``integer``
``query_params``
    * *Description:* This subkey is always present in the response. It contains
      processed search query parameters that the user actually explicitly specified.
    * *Datatype:* ``dictionary``
    * *Example:* ``{"dt_from": "", "submit": "Search"}``
``search_widget_item_limit``
    * *Description:* This subkey is always present in the response. It is intended
      for internal purposes.
    * *Datatype:* ``integer``
``searched``
    * *Description:* This subkey is present in case search operation was triggered.
      It is a simple indication of the successfull search operation.
    * *Datatype:* ``boolean`` always set to ``True``
``sqlquery``
    * *Description:* This subkey is present in case search operation was triggered.
      It contains the actual SQL query, that was issued to the database backend.
    * *Datatype:* ``string``
    * *Example:* ``"b'SELECT * FROM events ORDER BY \"detecttime\" DESC LIMIT 100'"``

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
from hawat.blueprints.timeline.forms import SimpleTimelineSearchForm


BLUEPRINT_NAME = 'timeline'
"""Name of the blueprint as module global constant."""


class AbstractSearchView(PsycopgMixin, BaseSearchView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for view responsible for searching `IDEA <https://idea.cesnet.cz/en/index>`__
    event database and presenting the results in timeline-based manner.
    """
    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Timeline')

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Search IDEA event timeline')

    @staticmethod
    def get_search_form(request_args):
        """
        *Interface implementation* of :py:func:`hawat.base.SearchView.get_search_form`.
        """
        # Get lists of available options for various event search form select fields.

        return SimpleTimelineSearchForm(
            request_args,
            meta = {'csrf': False}
        )

    def do_after_search(self, items):
        """
        *Interface implementation* of :py:func:`hawat.base.SearchView.do_after_search`.
        """
        self.logger.debug(
            "Calculating IDEA event timeline from %d records.",
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
                statistics = mentat.stats.idea.evaluate_timeline_events(
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


class TimelineBlueprint(HawatBlueprint):
    """
    Hawat pluggable module - IDEA event timelines.
    """

    @classmethod
    def get_module_title(cls):
        """*Implementation* of :py:func:`hawat.base.HawatBlueprint.get_module_title`."""
        return lazy_gettext('IDEA event timelines pluggable module')

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
            'dashboards.{}'.format(BLUEPRINT_NAME),
            position = 30,
            view = SearchView,
            resptitle = True
        )

        # Register context actions provided by this module.
        app.set_csag(
            hawat.const.HAWAT_CSAG_ADDRESS,
            tr_('Search for source <strong>%(name)s</strong> on IDEA event timeline'),
            SearchView,
            URLParamsBuilder({'submit': tr_('Search')}).add_rule('source_addrs', True).add_kwrule('dt_from', False, True).add_kwrule('dt_to', False, True)
        )

#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`hawat.base.HawatBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = TimelineBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates'
    )

    hbp.register_view_class(SearchView,       '/{}/search'.format(BLUEPRINT_NAME))
    hbp.register_view_class(APISearchView,    '/api/{}/search'.format(BLUEPRINT_NAME))

    return hbp
