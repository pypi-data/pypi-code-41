"""All the functionality to do with the filesystem

:copyright: Copyright 2019 Edward Armitage.
:license: MIT, see LICENSE for details.
"""
import os
import shutil
from pathlib import Path


class FolderCreator:
    def __init__(self, base_path, month_only):
        self._base_path = Path(base_path)
        self._month_only = month_only

    def create_folder(self, date):
        path = self._build_path(date)
        os.makedirs(path, exist_ok=True)

    def move_file(self, file, date):
        shutil.move(file, self._build_path(date))

    def _build_path(self, date):
        year = "{:04d}".format(date.year)
        month = "{:02d}".format(date.month)
        day = "{:02d}".format(date.day)

        if self._month_only:
            path = os.path.join(str(self._base_path), year, month)
        else:
            path = os.path.join(str(self._base_path), year, month, day)

        return path


def find_all_associated_files(file):
    """Finds the companion files alongside the provided the file in a given directory

    A companion file is a file within the same directory as the original file, with the same
    name (ignoring file extensions). For example photo-001.raw is a companion to photo-001.jpg,
    but photo-0011.jpg is not.

    :param file: The file to find companions for
    :return: a list of Paths containing the provided file and all companion files
    """
    return file.parent.glob("{}.*".format(file.stem))
