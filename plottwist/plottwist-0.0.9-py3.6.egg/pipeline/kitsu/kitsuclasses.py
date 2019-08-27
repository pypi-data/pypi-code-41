#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementation for Kitsu data objets to work with a more OO approach
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"


class KitsuUserInfo(object):
    def __init__(self, data):
        super(KitsuUserInfo, self).__init__()

        self._dict = data
        self._first_name = data.get('first_name', '')
        self._last_name = data.get('last_name', '')
        self._has_avatar = data.get('has_avatar', False)
        self._locale = data.get('locale', '')
        self._last_presence = data.get('last_presence', None)
        self._created_at = data.get('created_at', '')
        self._notifications_enabled = data.get('notifications_enabled', None)
        self._shotgun_id = data.get('shotgun_id', None)
        self._updated_at = data.get('updated_at', '')
        self._email = data.get('email', '')
        self._phone = data.get('phone', '')
        self._role = data.get('role', '')
        self._data = data.get('data', None)
        self._full_name = data.get('full_name', '')
        self._timezone = data.get('timezone', '')
        self._active = data.get('active', False)
        self._skills = data.get('skills', list())
        self._desktop_login = data.get('desktop_login', '')
        self._type = data.get('type', '')
        self._id = data.get('id', '')

    @property
    def first_name(self):
        """
        Returns first name of the user
        :return: str
        """

        return self._first_name

    @property
    def last_name(self):
        """
        Returns last name of the user
        :return: str
        """

        return self._last_name

    @property
    def locale(self):
        """
        Returns locale of the user
        :return: str
        """

        return self._locale

    @property
    def full_name(self):
        """
        Returns full name of the user
        :return: str
        """

        return self._full_name

    @property
    def email(self):
        """
        Returns the email of the user
        :return: str
        """

        return self._email

    @property
    def role(self):
        """
        Returns the role of the user
        :return: str
        """

        return self._role

    @property
    def timezone(self):
        """
        Returns time zone of the user
        :return: str
        """

        return self._timezone


class KitsuAsset(object):
    def __init__(self, data):
        super(KitsuAsset, self).__init__()

        self._dict = data

        self._name = data.get('name', '')
        self._id = data.get('id', '')
        self._type = data.get('type', None)
        self._entity_type_id = data.get('entity_type_id', '')
        self._code = data.get('code', None)
        self._description = data.get('description', '')
        self._canceled = data.get('canceled', False)
        self._preview_file_id = data.get('preview_file_id', None)
        self._created_at = data.get('created_at', '')
        self._instance_casting = data.get('instance_casting', list())
        self._shotgun_id = data.get('shotgun_id', None)
        self._updated_at = data.get('updated_at', '')
        self._data = data.get('data', dict())
        self._parent_id = data.get('parent_id', None)
        self._source_id = data.get('source_id', None)
        self._entities_in = data.get('entities_in', list())
        self._project_id = data.get('project_id', '')
        self._entities_out = data.get('entities_out', list())
        self._number_frames = data.get('nb_frames', None)

    @property
    def name(self):
        """
        Returns asset name
        :return: str
        """

        return self._name

    @property
    def id(self):
        """
        Returns asset id
        :return: str
        """

        return self._id

    @property
    def type(self):
        """
        Returns asset type
        :return: str
        """

        return self._type

    @property
    def entity_type_id(self):
        """
        Returns asset entity type id
        :return: str
        """

        return self._entity_type_id

    @property
    def preview_file_id(self):
        """
        Returns asset preview file id
        :return: str
        """

        return self._preview_file_id


class KitsuAssetType(object):
    def __init__(self, data):
        super(KitsuAssetType, self).__init__()

        self._dict = data

        self._name = data.get('name', '')
        self._id = data.get('id', '')
        self._type = data.get('type', '')
        self._created_at = data.get('created_at', '')
        self._updated_at = data.get('updated_at')

    @property
    def name(self):
        """
        Returns asset type name
        :return: str
        """

        return self._name

    @property
    def id(self):
        """
        Returns asset type id
        :return: str
        """

        return self._id

    @property
    def type(self):
        """
        Returns asset Kitsu type
        :return: str
        """

        return self._type

    @property
    def created_at(self):
        """
        Returns data where the asset type was created
        :return: str
        """

        return self._created_at

    @property
    def updated_at(self):
        """
        Returns last date when the asset type was updated
        :return: str
        """

        return self._updated_at


class KitsuEntityType(object):
    def __init__(self, data):
        super(KitsuEntityType, self).__init__()

        self._dict = data

        self._id = data.get('id', '')
        self._name = data.get('name', '')
        self._type = data.get('type', '')
        self._created_at = data.get('created_at', '')
        self._updated_at = data.get('updated_at', '')

    @property
    def id(self):
        """
        Returns entity type id
        :return: str
        """

        return self._id

    @property
    def name(self):
        """
        Returns entity type name
        :return: str
        """

        return self._name

    @property
    def type(self):
        """
        Returns entity type type
        :return: str
        """

        return self._type

    @property
    def created_at(self):
        """
        Returns created date of the entity type
        :return: str
        """

        return self._created_at

    @property
    def updated_at(self):
        """
        Returns last update date of the entity type
        :return: str
        """

        return self._updated_at
