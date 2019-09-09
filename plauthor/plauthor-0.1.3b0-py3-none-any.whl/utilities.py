__author__ = 'Shayan Fazeli'
__email__ = 'shayan@cs.ucla.edu'

import os
from typing import Tuple


def separate_path_and_file(filepath: str) -> Tuple[str]:
    """
    This method simply separates the path and filename.
    Parameters
    ----------
    filepath: `str`, required
        The filepath ending in file name and file format
    Returns
    ---------
    (directory, filename): `Tuple[str]`
        It contains the absolute path to the directory, and the filename.
    """
    filepath = os.path.abspath(filepath)
    filename = filepath.split('/')[-1]
    directory = filepath[:-len(filename)]
    return directory, filename


def make_sure_the_folder_exists(folder_path: str):
    """
    This method simply makes sure that the path provided to it represents a legit folder.

    Parameters
    ----------
    folder_path: `str`, required
        The path to the requested folder.

    Returns
    ----------
    It returns the `str` absolute path to the requested folder that is now ensured to exist.
    """
    folder_path = os.path.abspath(folder_path)
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)

    return folder_path