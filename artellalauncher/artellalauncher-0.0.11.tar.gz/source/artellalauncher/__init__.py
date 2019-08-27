#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialization module for artellapipe
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import sys
import inspect

from tpPyUtils import importer, path as path_utils
from tpQtLib.core import resource as resource_utils

from artellalauncher.core import defines

# =================================================================================

logger = None
resource = None
project = None

# =================================================================================


class ArtellaLauncherResource(resource_utils.Resource, object):
    RESOURCES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')


class ArtellaLauncher(importer.Importer, object):
    def __init__(self):
        super(ArtellaLauncher, self).__init__(module_name='artellalauncher')

    def get_module_path(self):
        """
        Returns path where tpNameIt module is stored
        :return: str
        """

        try:
            mod_dir = os.path.dirname(inspect.getframeinfo(inspect.currentframe()).filename)
        except Exception:
            try:
                mod_dir = os.path.dirname(__file__)
            except Exception:
                try:
                    import tpDccLib
                    mod_dir = tpDccLib.__path__[0]
                except Exception:
                    return None

        return mod_dir


def init(do_reload=False):
    """
    Initializes module
    :param do_reload: bool, Whether to reload modules or not
    """

    update_paths()
    artella_importer = importer.init_importer(importer_class=ArtellaLauncher, do_reload=do_reload)

    global logger
    global resource

    logger = artella_importer.logger
    resource = ArtellaLauncherResource

    artella_importer.import_modules()


def update_paths():
    """
    Adds to sys.path necessary modules
    :return:
    """

    dccs_path = get_dccs_path()
    if dccs_path and os.path.isdir(dccs_path):
        sys.path.append(dccs_path)


def get_dccs_path():
    """
    Returns path where DCCs are located
    :return: str
    """

    return path_utils.clean_path(os.path.join(os.path.dirname(__file__), 'artelladccs'))


def get_launcher_config_path():
    """
    Returns path where default Artella launcher config is located
    :return: str
    """

    return path_utils.clean_path(os.path.join(os.path.dirname(__file__), defines.ARTELLA_LAUNCHER_CONFIG_FILE_NAME))


def get_updater_config_path():
    """
    Returns path where default Artella updater config is located
    :return: str
    """

    return path_utils.clean_path(os.path.join(os.path.dirname(__file__), defines.ARTELLA_UPDATER_CONFIG_FILE_NAME))
