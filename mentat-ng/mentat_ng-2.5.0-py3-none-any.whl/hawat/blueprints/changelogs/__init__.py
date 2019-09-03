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

This pluggable module provides access to item changelogs.
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
from mentat.datatype.sqldb import ItemChangeLogModel

import hawat.acl
from hawat.base import HTMLMixin, SQLAlchemyMixin, BaseSearchView,\
    ItemShowView, HawatBlueprint
from hawat.blueprints.changelogs.forms import ItemChangeLogSearchForm


BLUEPRINT_NAME = 'changelogs'
"""Name of the blueprint as module global constant."""


class SearchView(HTMLMixin, SQLAlchemyMixin, BaseSearchView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    General item changelog record listing.
    """
    methods = ['GET']

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Changelogs')

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Search item changelogs')

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return ItemChangeLogModel

    @staticmethod
    def get_search_form(request_args):
        """
        *Interface implementation* of :py:func:`hawat.base.SearchView.get_search_form`.
        """
        return ItemChangeLogSearchForm(request_args, meta = {'csrf': False})

    @staticmethod
    def build_query(query, model, form_args):
        """
        *Interface implementation* of :py:func:`hawat.base.SearchView.build_query`.
        """
        # Adjust query based on lower time boudary selection.
        if 'dt_from' in form_args and form_args['dt_from']:
            query = query.filter(model.createtime >= form_args['dt_from'])
        # Adjust query based on upper time boudary selection.
        if 'dt_to' in form_args and form_args['dt_to']:
            query = query.filter(model.createtime <= form_args['dt_to'])
        # Adjust query based on changelog author selection.
        if 'authors' in form_args and form_args['authors']:
            query = query.filter(model.author_id.in_([x.id for x in form_args['authors']]))
        # Adjust query based on changelog operation selection.
        if 'operations' in form_args and form_args['operations']:
            query = query.filter(model.operation.in_(form_args['operations']))
        # Adjust query based on changelog model selection.
        if 'imodel' in form_args and form_args['imodel']:
            # Adjust query based on changelog model ID selection.
            if 'imodel_id' in form_args and form_args['imodel_id']:
                query = query.filter(model.model == form_args['imodel'], model.imodel_id == form_args['imodel_id'])
            else:
                query = query.filter(model.model == form_args['imodel'])

        # Return the result sorted by creation time in descending order.
        return query.order_by(model.createtime.desc())

    @classmethod
    def get_context_action_menu(cls):
        """*Implementation* of :py:func:`hawat.base.ItemListView.get_context_action_menu`."""
        context_action_menu = super().get_context_action_menu()
        context_action_menu.add_entry(
            'submenu',
            'more',
            align_right = True,
            legend = lazy_gettext('More actions')
        )
        context_action_menu.add_entry(
            'endpoint',
            'more.searchauthor',
            endpoint = 'changelogs.search',
            title = lazy_gettext('Other changes by the same author'),
            link = lambda x: flask.url_for('changelogs.search', authors = x.author_id, dt_from = '', submit = 'Search'),
            icon = 'action-search',
            hidelegend = True
        )
        context_action_menu.add_entry(
            'endpoint',
            'more.searchmodel',
            endpoint = 'changelogs.search',
            title = lazy_gettext('Other changes of the same item'),
            link = lambda x: flask.url_for('changelogs.search', model = x.model, model_id = x.model_id, dt_from = '', submit = 'Search'),
            icon = 'action-search',
            hidelegend = True
        )
        context_action_menu.add_entry(
            'endpoint',
            'more.searchboth',
            endpoint = 'changelogs.search',
            title = lazy_gettext('Other changes of the same item by the same author'),
            link = lambda x: flask.url_for('changelogs.search', authors = x.author_id, model = x.model, model_id = x.model_id, dt_from = '', submit = 'Search'),
            icon = 'action-search',
            hidelegend = True
        )
        return context_action_menu


class ShowView(HTMLMixin, SQLAlchemyMixin, ItemShowView):
    """
    Detailed network record view.
    """
    methods = ['GET']

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_menu_title`."""
        return lazy_gettext('Show item changelog record')

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """
        *Interface implementation* of :py:func:`hawat.base.BaseView.get_menu_legend`.
        """
        return lazy_gettext('View details of item changelog record &quot;%(item)s&quot;', item = str(kwargs['item']))

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Show item changelog record details')

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return ItemChangeLogModel

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
            'search',
            endpoint = '{}.search'.format(cls.module_name)
        )
        action_menu.add_entry(
            'endpoint',
            'show',
            endpoint = '{}.show'.format(cls.module_name)
        )
        return action_menu


#-------------------------------------------------------------------------------


class ItemChangeLogsBlueprint(HawatBlueprint):
    """
    Hawat pluggable module - changelogs.
    """

    @classmethod
    def get_module_title(cls):
        """*Implementation* of :py:func:`hawat.base.HawatBlueprint.get_module_title`."""
        return lazy_gettext('Item changelog record pluggable module')

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
            position = 80,
            view = SearchView
        )


#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`hawat.base.HawatBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = ItemChangeLogsBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates',
        url_prefix = '/{}'.format(BLUEPRINT_NAME)
    )

    hbp.register_view_class(SearchView, '/search')
    hbp.register_view_class(ShowView, '/<int:item_id>/show')

    return hbp
