import re
import os
import shutil


def folder_size(path):
    """
    Calculates the size of a folder
    :param path: path to folder to analyze
    :return: size in MB of the folder
    """
    size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp) and not os.path.islink(fp):
                size += os.path.getsize(fp)
    return round(size / (1024.0 * 1024.0), 2)


def find_file(name, path):
    """
    Finds files with the given name on a certain path
    :param name: filename to lookup
    :param path: path where file will be searched
    :return: array of strings with absolute paths
    """
    arr = []
    path = os.path.abspath(path)
    for root, dirs, files in os.walk(path):
        if name in files:
            p = os.path.join(root, name)
            arr.append(p)
    return arr


def get_venv_path(path):
    """
    Goes through the 'activate' virtualenv script to find the
    VIRTUAL_ENV line and validate that the folder is actually a
    virtual environment
    :param path: path to the 'activate' script
    :return: boolean indicating virtualenv status
    """
    if not os.path.isfile(path):
        return None, None

    prefix = 'VIRTUAL_ENV='
    regex = '^' + prefix + '(.)+'
    pattern = re.compile(regex)

    r = None
    for i, line in enumerate(open(path)):
        for match in re.finditer(pattern, line):
            r = eval(match.group().split(prefix)[-1])
        if r:
            # RFE: r might be different from the given path, if a virtual
            # environment was copied of installed in some other way
            return path.split('bin/activate')[0]
    return r


def delete_folder(path):
    """
    Deletes the folder from the given path
    :param path: path to folder to delete
    :return: True if the directory was successfully deleted, False otherwise
    """
    if not os.path.isdir(path):
        return False
    shutil.rmtree(path)
    return os.path.isdir(path)


def list_packages(path):
    """
    TODO: list the packages from a given virtual env path
    :param path: string, path of a virtual environment
    :return: array of dicts with packages of the given virtual env
    """
    if not os.path.isdir(path):
        return []

    arr = []
    return arr


def find_virtualenvs(path='/'):
    """
    Looks up for virtual environments on a given path.
    :param path: path where to look virtual environments
    :return: list of dictionaries with virtualenv information
    """
    if not os.path.isdir(path):
        raise NotADirectoryError('Invalid path')

    possible_venvs = find_file('activate', path)
    venvs = []
    for e in possible_venvs :
        f = get_venv_path(e)
        if not f:
            continue
        v = {}
        v['location'] = f
        v['size'] = folder_size(f)
        v['packages'] = list_packages(v['location'])
        venvs.append(v)
    return venvs