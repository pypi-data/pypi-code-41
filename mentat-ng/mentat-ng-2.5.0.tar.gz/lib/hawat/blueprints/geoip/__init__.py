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

This pluggable module provides access to local IP geolocation service. It is
implemented upon custom :py:mod:`mentat.services.geoip` module, which in turn uses
the geolocation service `GeoLite2 <https://dev.maxmind.com/geoip/geoip2/geolite2/>`__
created by `MaxMind <http://www.maxmind.com/>`__.


Provided endpoints
------------------

``/geoip/search``
    Endpoint providing search form for querying local IP geolocation service and
    formating result as HTML page.

    * *Authentication:* login required
    * *Methods:* ``GET``

``/api/geoip/search``
    Endpoint providing API search form for querying local IP geolocation service
    and formating result as JSON document.

    * *Authentication:* login required
    * *Authorization:* any role
    * *Methods:* ``GET``, ``POST``

``/snippet/geoip/search``
    Endpoint providing API search form for querying local IP geolocation service
    and formating result as JSON document containing HTML snippets.

    * *Authentication:* login required
    * *Authorization:* any role
    * *Methods:* ``GET``, ``POST``
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


#
# Flask related modules.
#
import flask
from flask_babel import lazy_gettext

#
# Custom modules.
#
import mentat.services.geoip
from mentat.const import tr_

import hawat.const
import hawat.db
import hawat.acl
from hawat.base import HTMLMixin, AJAXMixin, SnippetMixin, RenderableView, HawatBlueprint, URLParamsBuilder
from hawat.blueprints.geoip.forms import GeoipSearchForm


BLUEPRINT_NAME = 'geoip'
"""Name of the blueprint as module global constant."""


class AbstractSearchView(RenderableView):  # pylint: disable=locally-disabled,abstract-method
    """
    Application view providing base search capabilities for local IP geolocation
    service.

    The geolocation is implemented using :py:mod:`mentat.services.geoip` module.
    """
    authentication = True

    authorization = [hawat.acl.PERMISSION_ANY]

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Search GeoIP')

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Search GeoIP')

    #---------------------------------------------------------------------------

    def dispatch_request(self):
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the *Flask* framework to service the request.
        """
        form = GeoipSearchForm(flask.request.args, meta = {'csrf': False})
        if hawat.const.HAWAT_FORM_ACTION_SUBMIT in flask.request.args:
            if form.validate():
                form_data = form.data
                geoip_service = mentat.services.geoip.service()
                self.response_context.update(
                    search_item = form.search.data,
                    form_data   = form_data
                )

                try:
                    self.response_context.update(
                        search_result = geoip_service.lookup(
                            form.search.data
                        )
                    )
                except Exception as exc:
                    self.flash(str(exc), category = 'error')

        self.response_context.update(
            search_form  = form,
            request_args = flask.request.args,
        )
        return self.generate_response()


class SearchView(HTMLMixin, AbstractSearchView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View responsible for searching IP geolocation service and presenting the
    results in the form of HTML page.
    """
    methods = ['GET']

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'search'


class APISearchView(AJAXMixin, AbstractSearchView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View responsible for searching IP geolocation service and presenting the
    results in the form of JSON document.
    """
    methods = ['GET','POST']

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'apisearch'


class SnippetSearchView(SnippetMixin, AbstractSearchView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View responsible for searching IP geolocation service and presenting the
    results in the form of JSON document containing ready to use HTML page snippets.
    """
    methods  = ['GET', 'POST']
    renders  = ['label', 'full']
    snippets = ['city', 'asn']

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'sptsearch'

    def process_response_context(self):
        """*Implementation* of :py:func:`hawat.base.SnippetMixin.process_response_context`."""
        super().process_response_context()

        res = self.response_context.get('search_result', False)
        if res:
            if res.get('city', False) and res['city'].get('ctr_code', False):
                self._render_snippet('city')
            if res.get('asn', False) and (res['asn'].get('asn', False) or res['asn'].get('org', False)):
                self._render_snippet('asn')
        return self.response_context


#-------------------------------------------------------------------------------


class GeoipBlueprint(HawatBlueprint):
    """
    Hawat pluggable module - IP geolocation service.
    """

    @classmethod
    def get_module_title(cls):
        """*Implementation* of :py:func:`hawat.base.HawatBlueprint.get_module_title`."""
        return lazy_gettext('IP geolocation service')

    def register_app(self, app):
        """
        *Callback method*. Will be called from :py:func:`hawat.base.HawatApp.register_blueprint`
        method and can be used to customize the Flask application object. Possible
        use cases:

        * application menu customization

        :param hawat.base.HawatApp app: Flask application to be customize.
        """
        mentat.services.geoip.init(app.mconfig)

        app.menu_main.add_entry(
            'view',
            'more.{}'.format(BLUEPRINT_NAME),
            position = 20,
            view = SearchView
        )

        # Register context actions provided by this module.
        app.set_csag(
            hawat.const.HAWAT_CSAG_ADDRESS,
            tr_('Search for address <strong>%(name)s</strong> in IP geolocation service'),
            SearchView,
            URLParamsBuilder({'submit': tr_('Search')}).add_rule('search')
        )

        # Register object additional data services provided by this module.
        app.set_oads(
            hawat.const.HAWAT_AODS_IP4,
            SnippetSearchView,
            URLParamsBuilder({'submit': tr_('Search')}).add_rule('search').add_kwrule('render', False, True)
        )
        app.set_oads(
            hawat.const.HAWAT_AODS_IP6,
            SnippetSearchView,
            URLParamsBuilder({'submit': tr_('Search')}).add_rule('search').add_kwrule('render', False, True)
        )


#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`hawat.base.HawatBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = GeoipBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates'
    )

    hbp.register_view_class(SearchView,        '/{}/search'.format(BLUEPRINT_NAME))
    hbp.register_view_class(APISearchView,     '/api/{}/search'.format(BLUEPRINT_NAME))
    hbp.register_view_class(SnippetSearchView, '/snippet/{}/search'.format(BLUEPRINT_NAME))

    return hbp
