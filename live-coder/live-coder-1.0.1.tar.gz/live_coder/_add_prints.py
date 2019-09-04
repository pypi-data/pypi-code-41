import os

from ._update_print_references import update_print_file_references
from ._add_execution_prints import add_execution_prints
from ._constants import (
    PRINT_PREFIX
)


def _new_print_file_name(path):
    terms = path.split('/')
    terms[-1] = PRINT_PREFIX + terms[-1]
    return '/'.join(terms)


def add_prints_from_file_paths(project_path, file_paths):
    '''
        Add prints to each file in file_paths.
    '''
    new_print_files = []
    for path in file_paths:
        code = open(path, 'r').read()
        code_ast_root, imported_print_modules = update_print_file_references(project_path, path, code)
        relative_path = path[len(project_path):]
        code = add_execution_prints(relative_path, imported_print_modules, code_ast_root)
        print_path = _new_print_file_name(path)
        open(print_path, 'w').write(code)
        new_print_files.append(print_path)
    return new_print_files


def delete_print_files(file_paths):
    for path in file_paths:
        if PRINT_PREFIX not in path:
            raise Exception('Trying to delete non print file!')
        if os.path.isfile(path):
            os.remove(path)
