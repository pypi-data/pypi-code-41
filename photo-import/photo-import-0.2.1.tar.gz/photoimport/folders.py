"""All the functionality to do with the filesystem

:copyright: Copyright 2019 Edward Armitage.
:license: MIT, see LICENSE for details.
"""
import os
import shutil
from pathlib import Path


class FolderCreator:
    """Class for creating date-organised hierarchies of folders of files within a directory"""

    def __init__(self, base_path, month_only=False):
        """

        :param base_path: The directory to build the date-organised hierarchy within
        :param month_only: Whether to store all files for a given month in the same folder, rather
                than separating by day (default is False)
        """
        self._base_path = Path(base_path)
        self._month_only = month_only

    def create_folder(self, date):
        """Create a folder within the hierarchy for the given date

        If the required folder already exists, no action will be taken. If a top-level folder already
        exists (e.g. the year or month folder), the lower level (e.g. month or date) folders will be
        created alongside any existing files.

        :param date: The date to create a folder hierarchy for
        """
        path = self._build_path(date)
        os.makedirs(path, exist_ok=True)

    def move_file(self, file, date):
        """Moves a file into an appropriate directory for the given date

        :param file: The file to be moved
        :param date: The date to move the file into the directory for
        """
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
