# coding=utf-8
from os import makedirs
from os.path import dirname, exists


def ensure_directory_exists(directory):
    # type: (str) -> None
    if not exists(directory):
        makedirs(directory)


def ensure_file_directory_exists(file_path):
    # type: (str) -> None
    directory = dirname(file_path)

    ensure_directory_exists(directory)
