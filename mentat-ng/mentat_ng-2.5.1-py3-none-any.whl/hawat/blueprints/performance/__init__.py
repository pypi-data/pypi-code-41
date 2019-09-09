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

This pluggable module provides access to system performance statistics.
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import collections

from flask_babel import lazy_gettext

import mentat.stats.rrd
import hawat.acl
from hawat.base import HTMLMixin, SimpleView, FileNameView, HawatBlueprint

RRD_DB_DIR      = '/var/mentat/rrds'
RRD_REPORTS_DIR = '/var/mentat/reports/statistician'


BLUEPRINT_NAME = 'performance'
"""Name of the blueprint as module global constant."""


class ViewView(HTMLMixin, SimpleView):
    """
    View reponsible for presenting system performance in using RRD charts.
    """
    authentication = True

    authorization = [hawat.acl.PERMISSION_ANY]

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'view'

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'module-{}'.format(BLUEPRINT_NAME)

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('System performance')

    @classmethod
    def get_view_title(cls, **kwargs):

        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('System processing performance')

    def do_before_response(self, **kwargs):
        """*Implementation* of :py:func:`hawat.base.RenderableView.do_before_response`."""
        rrd_stats = mentat.stats.rrd.RrdStats(RRD_DB_DIR, RRD_REPORTS_DIR)
        charts    = rrd_stats.lookup()
        chartdict = collections.OrderedDict()

        # Convert list of all existing charts to a structure more apropriate
        # for display.
        for chrt in charts:
            key = chrt['ds_type']
            if chrt['totals']:
                key += '_t'
            if key not in chartdict:
                chartdict[key] = []
            chartdict[key].append(chrt)
        for key, val in chartdict.items():
            chartdict[key] = sorted(val, key=lambda x: x['size'])

        self.response_context['chartdict'] = chartdict


class DataView(FileNameView):
    """
    View reponsible for accessing raw performance data in RRD databases.
    """
    authentication = True

    authorization = [hawat.acl.PERMISSION_ANY]

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'data'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('System performance data')

    @classmethod
    def get_directory_path(cls):
        """
        *Interface implementation* of :py:func:`hawat.base.FileNameView.get_directory_path`.
        """
        return RRD_REPORTS_DIR


class RRDDBView(FileNameView):
    """
    View reponsible for accessing performance RRD databases.
    """
    authentication = True

    authorization = [hawat.acl.PERMISSION_ANY]

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'rrds'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('System performance databases')

    @classmethod
    def get_directory_path(cls):
        """
        *Interface implementation* of :py:func:`hawat.base.FileNameView.get_directory_path`.
        """
        return RRD_DB_DIR


#-------------------------------------------------------------------------------


class PerformanceBlueprint(HawatBlueprint):
    """
    Hawat pluggable module - system processing performance.
    """

    @classmethod
    def get_module_title(cls):
        """*Implementation* of :py:func:`hawat.base.HawatBlueprint.get_module_title`."""
        return lazy_gettext('System performance pluggable module')

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
            'more.{}'.format(BLUEPRINT_NAME),
            position = 100,
            group = lazy_gettext('Status overview'),
            view = ViewView
        )


#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`hawat.base.HawatBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = PerformanceBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates',
        static_folder = 'static',
        url_prefix = '/{}'.format(BLUEPRINT_NAME)
    )

    hbp.register_view_class(ViewView, '/view')
    hbp.register_view_class(DataView, '/data/<filename>')
    hbp.register_view_class(RRDDBView, '/rrds/<filename>')

    return hbp
