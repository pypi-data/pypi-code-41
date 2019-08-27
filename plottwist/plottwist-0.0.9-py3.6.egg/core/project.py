#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementation for Plot Twist Artella project
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import webbrowser
try:
    from urllib.parse import quote
except ImportError:
    from urllib2 import quote

from artellapipe.core import project as artella_project

import plottwist
from plottwist.core import asset, assetsviewer, shelf
from plottwist.launcher import tray
from plottwist.pipeline.kitsu import kitsulib, kitsuclasses


class PlotTwist(artella_project.ArtellaProject):

    PROJECT_PATH = plottwist.get_project_path()
    TRAY_CLASS = tray.PlotTwistTray
    SHELF_CLASS = shelf.PlotTwistShelf
    ASSET_CLASS = asset.PlotTwistAsset
    ASSETS_VIEWER_CLASS = assetsviewer.PlotTwistAssetsViewer
    PROJECT_CONFIG_PATH = plottwist.get_project_config_path()
    PROJECT_CHANGELOG_PATH = plottwist.get_project_changelog_path()
    PROJECT_SHELF_FILE_PATH = plottwist.get_project_shelf_path()
    PROJECT_MENU_FILE_PATH = plottwist.get_project_menu_path()
    PROJECT_VERSION_FILE_PATH = plottwist.get_project_version_path()

    def __init__(self, resource, naming_file):

        self._documentation_url = None
        self._kitsu_id = None
        self._kitsu_url = None
        self._drive_url = None
        self._gazu_api = None

        self._kitsu_user_data = None
        self._kitsu_is_logged = False

        self._entity_types = list()

        super(PlotTwist, self).__init__(resource=resource, naming_file=naming_file)

        self._init_kitsu()

    def init_config(self):
        """
        Overrides base ArtellaProject init_config function to load extra attributes from configuration file
        """

        super(PlotTwist, self).init_config()

        project_config_data = self.get_config_data()
        if not project_config_data:
            return

        self._documentation_url = project_config_data.get('PROJECT_DOCUMENTATION_URL', None)
        self._kitsu_id = project_config_data.get('PROJECT_KITSU_ID', None)
        self._kitsu_url = project_config_data.get('PROJECT_KITSU_URL', None)
        self._drive_url = project_config_data.get('PROJECT_DRIVE_URL', None)
        self._gazu_api = project_config_data.get('GAZU_API', None)

    def find_all_assets(self, asset_name=None):
        """
        Overrides base ArtellaProject find_all_assets function
        :param asset_name: str, If given, a list with the given item will be returned instead
        :return: variant, ArtellaAsset or list(ArtellaAsset)
        """

        if not self.is_logged_in_kitsu():
            self.logger.warning('Impossible to retrieve assets because user is not logged into Kitsu!')
            return

        assets_path = self.get_assets_path()
        if not self.is_valid_assets_path():
            self.logger.warning('Impossible to retrieve assets from invalid path: {}'.format(assets_path))
            return

        if not self._kitsu_is_logged:
            return

        kitsu_assets = kitsulib.all_assets_for_project(self._kitsu_id)
        asset_types = self.update_entity_types_from_kitsu(force=False)
        category_names = [asset_type.name for asset_type in asset_types]

        found_assets = list()
        for kitsu_asset in kitsu_assets:
            entity_type = self.get_entity_type_by_id(kitsu_asset.entity_type_id)
            if not entity_type:
                self.logger.warning('Entity Type {} for Asset {} is not valid! Skipping ...'.format(entity_type, kitsu_asset.name))
                continue
            asset_category = entity_type.name
            if asset_category in category_names:
                new_asset = self.create_asset(asset_data=kitsu_asset, category=asset_category)
            else:
                new_asset = self.create_asset(asset_data=kitsu_asset)
            found_assets.append(new_asset)

        return found_assets
        # return [self.ASSET_CLASS(project=self, asset_data=asset_data) for asset_data in kitsu_assets]

    @property
    def documentation_url(self):
        """
        Returns URL where Plot Twist documentation is stored
        :return: str
        """

        return self._documentation_url

    @property
    def kitsu_url(self):
        """
        Returns URL that links to Kitsu production tracker
        """

        return self._kitsu_url

    @property
    def gazu_api(self):
        """
        Returns URL that defines the Gizu API of the project
        :return: str
        """

        return self._gazu_api

    @property
    def drive_url(self):
        """
        Returns URL that links to Drive
        :return: str
        """

        return self._drive_url

    @property
    def kitsu_user(self):
        """
        Returns current Kitsu user logged
        :return: str
        """

        return self._kitsu_user

    @kitsu_user.setter
    def kitsu_user(self, user):
        """
        Sets current Kitsu user logged
        :param user: str
        """

        self._kitsu_user = user

    @property
    def kitsu_password(self):
        """
        Returns current Kitsu password logged
        :return: str
        """

        return self._kitsu_pass

    @kitsu_password.setter
    def kitsu_password(self, password):
        """
        Sets current Kitsu password logged
        :param password: str
        """

        self._kitsu_pass = password

    @property
    def kitsu_store_credentials(self):
        """
        Returns Kitsu stored credentials should be stored or not
        :return: bool
        """

        return self._kitsu_store_credentials

    @kitsu_store_credentials.setter
    def kitsu_store_credentials(self, store):
        """
        Sets whether Kitsu credentials should be stored or not
        :param store: bool
        """

        self._kitsu_store_credentials = store

    def open_webpage(self):
        """
        Opens Plot Twist official web page in browser
        """

        if not self._url:
            return

        webbrowser.open(self._url)

    def open_documentation(self):
        """
        Opens Plot Twist documentation web page in browser
        """

        if not self._documentation_url:
            return

        webbrowser.open(self._documentation_url)

    def open_kitsu(self):
        """
        Opens Plot Twist Kitsu web page in browser
        """

        if not self._kitsu_url:
            return

        webbrowser.open(self.get_kitsu_assets_url())

    def open_drive(self):
        """
        Opens Plot Twist Drive web page in browser
        """

        if not self._drive_url:
            return

        webbrowser.open(self._drive_url)

    def login_kitsu(self, email=None, password=None, store_credentials=False):
        """
        Login current project user into Kitsu with given info
        :param email: str
        :param password: str
        :param store_credentials: bool
        :return: bool
        """

        if not email:
            email = self._kitsu_user
        if not password:
            password = self._kitsu_pass
        if not store_credentials:
            store_credentials = self._kitsu_store_credentials

        if not email or not password:
            self.logger.warning('Impossible to login into Kitsu because username or password are not valid!')
            return False

        if not self.gazu_api:
            self.logger.warning('Impossible to login into Kitsu because Gazu API is not available!')
            return False

        kitsulib.set_host(self.gazu_api)
        if not kitsulib.host_is_up():
            self.logger.warning('Impossible to login into Kitsu because Gazu API is not valid: {}!'.format(self.gazu_api))
            return

        try:
            kitsulib.log_in(email, password)
            self._kitsu_is_logged = True
            self._kitsu_user_data = kitsulib.get_current_user()
            self.settings.set('kitsu_store_credentials', store_credentials)
            if store_credentials:
                self.settings.set('kitsu_email', email)
                self.settings.set('kitsu_password', password)
            return True
        except Exception:
            self._kitsu_user = None
            self._kitsu_pass = None
            self._kitsu_store_credentials = False
            self._kitsu_is_logged = False
            self._kitsu_user_data = None
            return False

    def logout_kitsu(self, remove_credentials=False):
        """
        Logout current project user from Kitsu
        """

        if not self.is_logged_in_kitsu():
            self.logger.warning('Impossible to logout from Kitsu because you are not currently logged')
            return False

        kitsulib.set_host(None)
        self._kitsu_user = None
        self._kitsu_pass = None
        self._kitsu_store_credentials = False
        self._kitsu_is_logged = False
        self._kitsu_user_data = None

        if remove_credentials:
            self.settings.set('kitsu_email', '')
            self.settings.set('kitsu_password', '')
            self.settings.set('kitsu_store_credentials', False)

        # Reinit Kitsu data
        self._init_kitsu()

        return True

    def is_logged_in_kitsu(self):
        """
        Returns whether current project user is logged into Kitsu server or not
        :return: bool
        """

        return self._kitsu_is_logged

    def open_in_kitsu(self):
        """
        Opens project Kitsu web page in user web browser
        """

        if self.kitsu_url:
            webbrowser.open(self.kitsu_url)

    def kitsu_user_data(self):
        """
        Returns current Kitsu logged user data
        :param as_dict: bool, Whether to return data as object or as dict
        :return: variant, dict or
        """

        return self._kitsu_user_data

    def update_types_from_kitsu(self, force=False):
        """
        Updates project asset types from Kitsu project
        :param force: bool, Whether to return force the update if assets types are already retrieved
        :return: list(KitsuAssetType)
        """

        if not self._kitsu_is_logged or not self._kitsu_id:
            return list()

        if self._asset_types and not force:
            return self._asset_types

        self._asset_types = kitsulib.all_asset_types_for_project(self._kitsu_id)

        return self._asset_types

    def update_entity_types_from_kitsu(self, force=False):
        """
        Updates entity types from Kitsu project
        :param force: bool, Whether to return force the update if entity types are already retrieved
        :return: list(KitsuEntityType)
        """

        if not self._kitsu_is_logged or not self._kitsu_id:
            return list()

        if self._entity_types and not force:
            return self._entity_types

        entity_types_list = kitsulib.get_project_entity_types()
        entity_types = [kitsuclasses.KitsuEntityType(entity_type) for entity_type in entity_types_list]
        self._entity_types = entity_types

        return self._entity_types

    def get_entity_type_by_id(self, entity_type_id, force_update=False):
        """
        Returns entity type name by the given project
        :param entity_type_id: str
        :param force_update: bool, Whether to force entity types sync if they are not already snced
        :return: str
        """

        if force_update or not self._entity_types:
            self.update_entity_types_from_kitsu(force=True)

        for entity_type in self._entity_types:
            if entity_type.id == entity_type_id:
                return entity_type

        return ''

    def get_kitsu_assets_url(self):
        """
        Returns URL path to Kitsu project assets
        :return: str
        """

        return self._kitsu_url + '/assets'

    def get_kitsu_shots_url(self):
        """
        Returns URL path to Kitsu project shots
        :return: str
        """

        return self._kitsu_url + '/shots'

    def get_kitsu_sequences_url(self):
        """
        Returns URL path to Kitsu project sequences
        :return: str
        """

        return self._kitsu_url + '/sequences'

    def get_kitsu_asset_types_url(self):
        """
        Returns URL path to Kitsu project asset types
        :return: str
        """

        return self._kitsu_url + '/asset-types'

    def get_kitsu_breakdown_url(self):
        """
        Returns URL path to Kitsu project breakdown
        :return: str
        """

        return self._kitsu_url + '/breakdown'

    def get_kitsu_playlists_url(self):
        """
        Returns URL path to Kitsu project playlists
        :return: str
        """

        return self._kitsu_url + '/playlists'

    def get_kitsu_team_url(self):
        """
        Returns URL path to Kitsu project team
        :return: str
        """

        return self._kitsu_url + '/team'

    def get_kitsu_news_feed_url(self):
        """
        Returns URL path to Kitsu project news-feed
        :return: str
        """

        return self._kitsu_url + '/news-feed'

    def get_kitsu_schedule_url(self):
        """
        Returns URL path to Kitsu project schedule
        :return: str
        """

        return self._kitsu_url + '/schedule'

    def _register_asset_classes(self):
        """
        Overrides base ArtellaProject _register_asset_classes function
        Internal function that can be override to register specific project asset classes
        """

        from plottwist.pipeline.tools.assetsmanager.assets import propasset, characterasset

        self.register_asset_class(propasset.PlotTwistPropAsset)
        self.register_asset_class(characterasset.PlotTwistCharacterAsset)

        super(PlotTwist, self)._register_asset_classes()

    def _register_asset_file_types(self):
        """
        Overrides base ArtellaProject _register_asset_file_types function
        Internal function that can be override to register specific project file type classes
        """

        from plottwist.core import assetfile

        self.register_asset_file_type(assetfile.TexturesAssetFile)
        self.register_asset_file_type(assetfile.ModelAssetFile)
        self.register_asset_file_type(assetfile.ShadingAssetFile)
        self.register_asset_file_type(assetfile.RigAssetFile)
        self.register_asset_file_type(assetfile.GroomAssetFile)
        self.register_asset_file_type(assetfile.AlembicAssetFile)

        super(PlotTwist, self)._register_asset_file_types()

    def _init_kitsu(self):
        """
        Initializes Kitsu data
        """

        self._kitsu_user = self.settings.get('kitsu_email') if self.settings.has_setting('kitsu_email') else None
        self._kitsu_pass = self.settings.get('kitsu_password') if self.settings.has_setting('kitsu_password') else None
        self._kitsu_store_credentials = self.settings.get('kitsu_store_credentials') if self.settings.has_setting('kitsu_store_credentials') else False