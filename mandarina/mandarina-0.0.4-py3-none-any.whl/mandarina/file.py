"""
This module provides functionality to work with files and folders.
"""

import os

def create_dir_if_doesnt_exist(folderpath):
    """
    Creates a folder if it doesn't exist.

    :param folderpath:
    :return: True if folder was created, else False

    """
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
        return True
    return False

def delete_file(filepath):
    """
    Deletes the specified file if the file exists.

    :param filepath: Path of the file to be deleted
    :return: True if the file was deleted, else False

    """
    if os.path.isfile(filepath):
        os.remove(filepath)
        return True
    else:
        print("Error: %s file not found" % filepath)
        return False

def delete_dir(dirpath):
    """
    Deletes the specified directory if it exists

    :param dirpath: Path to the directory
    :return: True if the directory was deleted, else False

    """
    if os.path.isdir(dirpath):
        os.rmdir(dirpath)
        return True
    else:
        print("Error: %s directory not found" % dirpath)
        return False

def count_files_in_dir(dirpath):
    """
    Counts the number of files contained in the specified
    directory.

    :param dirpath: Path to the directory
    :return: Number of files

    """
    return len([name for name in os.listdir(dirpath)
                       if os.path.isfile(os.path.join(dirpath, name))])
