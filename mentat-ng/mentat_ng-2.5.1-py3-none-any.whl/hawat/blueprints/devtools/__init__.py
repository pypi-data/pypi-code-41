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

This pluggable module provides various utility and development tools.

"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


#
# Flask related modules.
#
import flask
import flask_debugtoolbar
from flask_babel import lazy_gettext

#
# Custom modules.
#
import hawat.acl
from hawat.base import HTMLMixin, SimpleView, HawatBlueprint


BLUEPRINT_NAME = 'devtools'
"""Name of the blueprint as module global constant."""


class ConfigView(HTMLMixin, SimpleView):
    """
    View for displaying current Hawat configuration and environment.
    """

    authentication = True

    authorization = [hawat.acl.PERMISSION_DEVELOPER]

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'config'

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'module-{}'.format(BLUEPRINT_NAME)

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('System configuration')

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('View system configuration')


#-------------------------------------------------------------------------------


class DevtoolsBlueprint(HawatBlueprint):
    """
    Hawat pluggable module - development tools.
    """

    @classmethod
    def get_module_title(cls):
        """*Implementation* of :py:func:`hawat.base.HawatBlueprint.get_module_title`."""
        return lazy_gettext('Development tools pluggable module')

    def register_app(self, app):
        """
        *Callback method*. Will be called from :py:func:`hawat.base.HawatApp.register_blueprint`
        method and can be used to customize the Flask application object. Possible
        use cases:

        * application menu customization

        :param hawat.base.HawatApp app: Flask application to be customize.
        """
        self.developer_toolbar.init_app(app)

        app.menu_main.add_entry(
            'view',
            'developer.devconfig',
            position = 10,
            view = ConfigView
        )


#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`hawat.base.HawatBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = DevtoolsBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates',
        url_prefix = '/{}'.format(BLUEPRINT_NAME)
    )

    @hbp.route('/admin')
    @hawat.acl.PERMISSION_ADMIN.require(403)
    def admin():  # pylint: disable=locally-disabled,unused-variable
        """
        Simple utility view for testing 'admin' permissions.
        """
        return flask.render_template('devtools/permission_test.html', hawat_acl_policy = str(hawat.acl.PERMISSION_ADMIN))

    @hbp.route('/maintainer')
    @hawat.acl.PERMISSION_MAINTAINER.require(403)
    def maintainer():  # pylint: disable=locally-disabled,unused-variable
        """
        Simple utility view for testing 'maintainer' permissions.
        """
        return flask.render_template('devtools/permission_test.html', hawat_acl_policy = str(hawat.acl.PERMISSION_MAINTAINER))

    @hbp.route('/developer')
    @hawat.acl.PERMISSION_DEVELOPER.require(403)
    def developer():  # pylint: disable=locally-disabled,unused-variable
        """
        Simple utility view for testing 'developer' permissions.
        """
        return flask.render_template('devtools/permission_test.html', hawat_acl_policy = str(hawat.acl.PERMISSION_DEVELOPER))

    @hbp.route('/power')
    @hawat.acl.PERMISSION_POWER.require(403)
    def power():  # pylint: disable=locally-disabled,unused-variable
        """
        Simple utility view for testing 'power' permissions (admin or maintainer).
        """
        return flask.render_template('devtools/permission_test.html', hawat_acl_policy = str(hawat.acl.PERMISSION_POWER))

    hbp.developer_toolbar = flask_debugtoolbar.DebugToolbarExtension()  # pylint: disable=locally-disabled,attribute-defined-outside-init

    hbp.register_view_class(ConfigView, '/config')

    return hbp
