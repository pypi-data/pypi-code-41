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

This pluggable module provides access Mentat system status information. The
following information is provided:

* current status of all configured real-time message processing modules
* current status of all configured cronjob message post-processing modules


Provided endpoints
------------------

``/status/view``
    Page providing read-only access various Mentat system status characteristics.

    *Authentication:* login required
    *Methods:* ``GET``

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
import pyzenkit.jsonconf
import mentat.system
import hawat.acl
from hawat.base import HTMLMixin, SimpleView, HawatBlueprint


BLUEPRINT_NAME = 'status'
"""Name of the blueprint as module global constant."""


class ViewView(HTMLMixin, SimpleView):
    """
    Application view providing access Mentat system status information.
    """
    authentication = True

    authorization = [hawat.acl.PERMISSION_ADMIN]

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
        return lazy_gettext('System status')

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('System status')

    def do_before_response(self, **kwargs):
        """*Implementation* of :py:func:`hawat.base.RenderableView.do_before_response`."""
        controller_cfg = pyzenkit.jsonconf.json_load(
            flask.current_app.config['MENTAT_CONTROLLER_CFG'],
        )

        self.response_context['mentat_modules'] = mentat.system.make_module_list(
            controller_cfg.get('modules', {})
        )
        self.response_context['mentat_cronjobs'] = mentat.system.make_cronjob_list(
            controller_cfg.get('cronjobs', {})
        )

        self.response_context['mentat_runlogs'] = mentat.system.analyze_runlog_files(
            flask.current_app.config['MENTAT_PATHS']['path_run'],
            limit = 20
        )

        self.response_context['mentat_status'] = mentat.system.system_status(
            self.response_context['mentat_modules'],
            self.response_context['mentat_cronjobs'],
            flask.current_app.config['MENTAT_PATHS']['path_cfg'],
            flask.current_app.config['MENTAT_PATHS']['path_crn'],
            flask.current_app.config['MENTAT_PATHS']['path_log'],
            flask.current_app.config['MENTAT_PATHS']['path_run']
        )


#-------------------------------------------------------------------------------


class StatusBlueprint(HawatBlueprint):
    """
    Hawat pluggable module - Mentat system status.
    """

    @classmethod
    def get_module_title(cls):
        """*Implementation* of :py:func:`hawat.base.HawatBlueprint.get_module_title`."""
        return lazy_gettext('System status pluggable module')

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
            position = 20,
            group = lazy_gettext('Status overview'),
            view = ViewView
        )


#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`hawat.base.HawatBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = StatusBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates',
        url_prefix = '/{}'.format(BLUEPRINT_NAME)
    )

    hbp.register_view_class(ViewView, '/view')

    return hbp
