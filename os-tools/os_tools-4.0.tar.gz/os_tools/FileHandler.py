###########################################################################
#
# this module meant to provide file handling functions
#
###########################################################################

import os
import shutil


# will return the content of a directory (full paths)
def get_dir_content(dir_path, ignored_files_arr=['.DS_Store']):
    f = []
    for path, dirs, files in os.walk(dir_path):
        for filename in files:
            f.append(os.path.join(path, filename))
            break

    f = list(filter(lambda x: get_file_name_from_path(x) not in ignored_files_arr, f))
    return f

# will return the dirs of a directory (full paths)
def get_dirs_from_dir(dir_path):
    for path, dirs, files in os.walk(dir_path):
        return dirs


# will return the name of the last dir name from a path
def get_dir_name(dir_path):
    return os.path.basename(os.path.normpath(dir_path))


# will split path to arr of dirs
def split_path(path):
    path = os.path.normpath(path)
    return path.split(os.sep)


# will return the extension of a file from a file path
def get_extension_from_file(file):
    _, file_extension = os.path.splitext(file)
    return file_extension


# will return the file name from a file path
def get_file_name_from_path(file):
    import ntpath
    return ntpath.basename(file)


# will remove a directory
def remove_dir(path):
    if (os.path.isdir(path)):
        shutil.rmtree(path)


# will copy a directory
def copy_dir(src, dst):
    from distutils.dir_util import copy_tree
    copy_tree(src, dst)


# will copy a file to a dest
def copy_file(src, dst):
    shutil.copy(src, dst)


# will duplicate a file to the same dir with _temp at the end of it's name
def copy_to_temp_file(src):
    file_full_name = get_file_name_from_path(src)
    temp_name = file_full_name[0: file_full_name.rfind('.')] + '_temp'
    extension = get_extension_from_file(file_full_name)
    temp_dest = get_parent_path(src) + '/' + temp_name + extension
    copy_file(src, temp_dest)
    return temp_dest


# will return the parent path of a file
def get_parent_path(file):
    from pathlib import Path
    return str(Path(file).parent)


# will copy a list of files to a dir
def copy_list_of_files(files_list, dst):
    for file in files_list:
        copy_file(file, dst)


# will search for a file in a path
def search_file(path_to_search, file_name):
    from pathlib import Path
    files = []
    for filename in Path(path_to_search).glob('**/' + file_name):
        files.append(filename)
    return files


def replace_line_for_line(file, line_for_line_dict):
    """
    Will replace a line for a line in a file.
    Notice: this function use contains() and not ==.

    Args:
        param file:
        param line_for_line_dict:
    """
    lines = []
    with open(file, "r") as f:
        for line in f:
            appended = False
            for key, val in line_for_line_dict.items():
                if key in line:
                    lines.append(val + '\n')
                    appended = True
            if not appended:
                lines.append(line)

    with open(file, "w") as f:
        f.writelines(lines)


# is write permission granted
def is_file_write_permission_granted(file_path):
    return os.access(file_path, os.W_OK)


# is read permission granted
def is_file_read_permission_granted(file_path):
    return os.access(file_path, os.R_OK)


# is file exists
def is_file_exists(file_path):
    return os.path.exists(file_path)


# is directory exists
def is_dir_exists(dir_path):
    return os.path.isdir(dir_path)


# will copy the content of a directory to another directory
def copy_dir_content(dir_src, dir_dest):
    from distutils.dir_util import copy_tree
    copy_tree(dir_src, dir_dest)


# will clear the content of a directory
def clear_dir_content(dir_path):
    shutil.rmtree(dir_path)
    create_dir(dir_path)


# will create a directory. If dir exists, do nothing
def create_dir(dir_path):
    if not is_dir_exists(dir_path):
        os.makedirs(dir_path)


# will remove all of the files with a given extension
def remove_all_files_with_extension(path, ext):
    import glob
    if ext[0] == '.':
        ext = ext[1:]
    for f in glob.glob(path + "/*." + ext):
        os.remove(f)


# will check if line exists in a file
def is_line_exists_in_file(file, line_to_find):
    with open(file) as f:
        content = f.readlines()
        for line in content:
            if line_to_find in line:
                return True
    return False


# will read a file and look for a string. If the string exists, will return the whole line which comprise it
def get_line_from_file(file, str_to_find):
    with open(file) as read_file:
        for line in read_file:
            if str_to_find in line:
                return line
    return None


# will turn a json file to a dictionary
def json_file_to_dict(json_file):
    import json

    with open(json_file) as f:
        data = json.load(f)
    return data


def remove_lines_from_file(file_path, lines_arr_to_remove=None, remove_from=None, remove_until=None):
    """
    Will remove lines from a file if the lines contains certain strings
    Args:
        param file_path: the path to your file
        param lines_arr_to_remove: (optional) an array of lines to search for (this function calls contains() and not == )
        param remove_from: (optional) if you want to remove a range of lines, set here the first line in which to start the removal)
        param remove_until: (optional) if you want to remove a range of lines, set here the last line in which to end the removal)
    """
    if lines_arr_to_remove is None:
        lines_arr_to_remove = []
    import fileinput
    import sys
    on_remove_sequence = False
    for line in fileinput.input(file_path, inplace=1):
        line_to_remove_found = False
        if remove_from is not None and remove_from in line:
            on_remove_sequence = True

        if remove_until is not None and remove_until in line:
            on_remove_sequence = False
            continue

        if on_remove_sequence:
            continue

        if lines_arr_to_remove is not None:
            for line_to_remove in lines_arr_to_remove:
                if line_to_remove in line:
                    line_to_remove_found = True
                    break

        if line_to_remove_found:
            continue

        sys.stdout.write(line)
