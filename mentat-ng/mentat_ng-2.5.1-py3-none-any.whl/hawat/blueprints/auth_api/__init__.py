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

This pluggable module provides API key based authentication service. When this
module is enabled, users may generate and use API keys to authenticate themselves
when accessing various API application endpoints.

Currently the API key may be provided via one of the following methods:

* The ``Authorization`` HTTP header.

  You may provide your API key by adding ``Authorization`` HTTP header to your
  requests. Following forms are accepted::

    Authorization: abcd1234
    Authorization: key abcd1234
    Authorization: token abcd1234

* The ``api_key`` or ``api_token`` parameter of the HTTP ``POST`` request.

  You may provide your API key as additional HTTP parameter ``api_key`` or
  ``api_token`` of your ``POST`` request to particular application endpoint.
  Using ``GET`` requests is forbidden due to the fact that request URLs are getting
  logged on various places and your keys could thus be easily compromised.


Provided endpoints
--------------------------------------------------------------------------------

``/auth_api/<user_id>/key-generate``
    Page enabling generation of new API key.

    * *Authentication:* login required
    * *Authorization:* ``admin``
    * *Methods:* ``GET``, ``POST``

``/auth_api/<user_id>/key-delete``
    Page enabling deletion of existing API key.

    * *Authentication:* login required
    * *Authorization:* ``admin``
    * *Methods:* ``GET``, ``POST``
"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import itsdangerous

#
# Flask related modules.
#
import flask
import flask_login
import flask_principal
from flask_babel import gettext, lazy_gettext

#
# Custom modules.
#
from mentat.datatype.sqldb import UserModel
import hawat.const
import hawat.db
import hawat.forms
from hawat.base import HTMLMixin, SQLAlchemyMixin, ItemChangeView, HawatBlueprint


BLUEPRINT_NAME = 'auth_api'
"""Name of the blueprint as module global constant."""


class GenerateKeyView(HTMLMixin, SQLAlchemyMixin, ItemChangeView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for generating API keys for user accounts.
    """
    methods = ['GET','POST']

    authentication = True

    authorization = [hawat.acl.PERMISSION_ADMIN]

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'key-generate'

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'action-genkey'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Generate API key')

    @classmethod
    def get_view_template(cls):
        """*Implementation* of :py:func:`hawat.base.RenderableView.get_view_template`."""
        return 'auth_api/key-generate.html'

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_success`."""
        return gettext(
            'API key for user account <strong>%(item_id)s</strong> was successfully generated.',
            item_id = str(kwargs['item'])
        )

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext(
            'Unable to generate API key for user account <strong>%(item_id)s</strong>.',
            item_id = str(kwargs['item'])
        )

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext(
            'Canceled generating API key for user account <strong>%(item_id)s</strong>.',
            item_id = str(kwargs['item'])
        )

    @classmethod
    def change_item(cls, item):
        """
        *Interface implementation* of :py:func:`hawat.base.ItemChangeView.change_item`.
        """
        serializer = itsdangerous.URLSafeTimedSerializer(
            flask.current_app.config['SECRET_KEY'],
            salt = 'apikey-user'
        )
        item.apikey = serializer.dumps(item.id)


class DeleteKeyView(HTMLMixin, SQLAlchemyMixin, ItemChangeView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for deleting API keys from user accounts.
    """
    methods = ['GET','POST']

    authentication = True

    authorization = [hawat.acl.PERMISSION_ADMIN]

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_name`."""
        return 'key-delete'

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_icon`."""
        return 'action-delete'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.base.BaseView.get_view_title`."""
        return lazy_gettext('Delete API key')

    @classmethod
    def get_view_template(cls):
        """*Implementation* of :py:func:`hawat.base.RenderableView.get_view_template`."""
        return 'auth_api/key-delete.html'

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`hawat.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_success`."""
        return gettext(
            'API key for user account <strong>%(item_id)s</strong> was successfully deleted.',
            item_id = str(kwargs['item'])
        )

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_failure`."""
        return gettext(
            'Unable to delete API key for user account <strong>%(item_id)s</strong>.',
            item_id = str(kwargs['item'])
        )

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`hawat.base.ItemActionView.get_message_cancel`."""
        return gettext(
            'Canceled deleting API key for user account <strong>%(item_id)s</strong>.',
            item_id = str(kwargs['item'])
        )

    @classmethod
    def change_item(cls, item):
        """
        *Interface implementation* of :py:func:`hawat.base.ItemChangeView.change_item`.
        """
        item.apikey = None


#-------------------------------------------------------------------------------


class APIAuthBlueprint(HawatBlueprint):
    """
    Hawat pluggable module - API key based authentication (*auth_api*).
    """

    @classmethod
    def get_module_title(cls):
        """*Implementation* of :py:func:`hawat.base.HawatBlueprint.get_module_title`."""
        return gettext('API key authentication service')

    def register_app(self, app):
        """
        *Callback method*. Will be called from :py:func:`hawat.base.HawatApp.register_blueprint`
        method and can be used to customize the Flask application object. Possible
        use cases:

        * application menu customization

        :param hawat.base.HawatApp app: Flask application to be customize.
        """
        login_manager = app.get_resource(hawat.const.RESOURCE_LOGIN_MANAGER)
        principal = app.get_resource(hawat.const.RESOURCE_PRINCIPAL)

        @login_manager.request_loader
        def load_user_from_request(request):  # pylint: disable=locally-disabled,unused-variable
            """
            Custom login callback for login via request object.

            https://flask-login.readthedocs.io/en/latest/#custom-login-using-request-loader
            """

            # Attempt to extract token from Authorization header. Following formats
            # may be used:
            #   Authorization: abcd1234
            #   Authorization: key abcd1234
            #   Authorization: token abcd1234
            api_key = request.headers.get("Authorization")
            if api_key:
                vals = api_key.split()
                if len(vals) == 1:
                    api_key = vals[0]
                elif len(vals) == 2 and vals[0] in ("token", "key"):
                    api_key = vals[1]
                else:
                    api_key = None
            # API key may also be received via POST method, parameters 'api_key'
            # or 'api_token'. The GET method is forbidden due to the lack
            # of security, there is a possiblity for it to be stored in various
            # insecure places like web server logs.
            if not api_key:
                api_key = request.form.get('api_key')
            if not api_key:
                api_key = request.form.get('api_token')

            # Now login the user with provided API key.
            if api_key:
                dbsess = hawat.db.db_get().session
                try:
                    user = dbsess.query(UserModel).filter(UserModel.apikey == api_key).one()
                    if user:
                        if user.enabled:
                            flask.current_app.logger.info(
                                "User '{}' used API key to access the resource '{}'.".format(user.login, request.url)
                            )
                            return user
                        flask.current_app.logger.error(
                            "The API key for user account '{}' was rejected, the account is disabled.".format(user.login)
                        )
                except:  # pylint: disable=locally-disabled,bare-except
                    pass

            # Return ``None`` if API key method did not login the user.
            return None

        @flask_login.user_loaded_from_request.connect_via(app)
        def on_user_loaded_from_request(sender, user):  # pylint: disable=locally-disabled,unused-variable, unused-argument
            """
            Without whis intermediate step the flask_principal.on_identity_loaded
            callback is never called and the user identity does not have the correct
            permissions set.

            Solution resource:
                https://github.com/mattupstate/flask-principal/issues/22#issuecomment-145897838
            """
            principal.set_identity(
                flask_principal.Identity(user.id)
            )


#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`hawat.base.HawatBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = APIAuthBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates',
        url_prefix = '/{}'.format(BLUEPRINT_NAME)
    )

    hbp.register_view_class(GenerateKeyView, '/<int:item_id>/key-generate')
    hbp.register_view_class(DeleteKeyView,   '/<int:item_id>/key-delete')

    return hbp
