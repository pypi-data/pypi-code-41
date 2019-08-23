# coding=utf-8
from os import access, getenv, pathsep, X_OK
from os.path import isfile, join
from platform import system
from typing import Union


def find_executable(command):
    # type: (str) -> Union[str, None]
    path = getenv('PATH')
    entries = path.split(pathsep)

    if system() == 'Windows':
        runnable_extensions = [extension.lower() for extension in getenv('PATHEXT').split(pathsep)]
    else:
        runnable_extensions = list()

    for entry in entries:
        test_paths = [join(entry, command + extension) for extension in runnable_extensions]
        test_paths.append(join(entry, command))

        test_path = next((test_path for test_path in test_paths if isfile(test_path)), None)
        if not test_path or not access(test_path, X_OK):
            continue

        return test_path

    return None
