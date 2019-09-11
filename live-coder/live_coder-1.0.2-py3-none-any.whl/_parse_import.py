import astor
import ast
import os

from ._constants import (
    PRINT_PREFIX
)

def _parse_ImportFrom(importFrom):
    paths = []
    base = importFrom.module
    for alias in importFrom.names:
        paths.append(
            base + '.' + alias.name
        )
    return paths

def _parse_Import(an_import):
    paths = []
    for alias in an_import.names:
        paths.append(alias.name)
    return paths

def _parse_import(command):
    if type(command) is ast.ImportFrom:
        return _parse_ImportFrom(command)
    if type(command) is ast.Import:
        return _parse_Import(command)
    return None

def _find_imported_paths(code):
    root = ast.parse(code)
    paths = []
    for i, command in enumerate(root.body):
        result = _parse_import(command)
        if result:
            paths.append({'command_i': i, 'paths': result})
    return paths

def _get_command_paths_terms(command):
    paths = _parse_import(command)
    return [path.split('.') for path in paths]

def _update_import_command(import_command, alias_i, new_term_i, new_term):
    if type(import_command) is ast.ImportFrom:
        terms = import_command.module.split('.')
        if new_term_i < len(terms):
            terms[new_term_i] = new_term
            import_command.module = '.'.join(terms)
            return import_command        
        new_term_i  -= len(terms)
    for i, alias in enumerate(import_command.names):
        if i == alias_i:
            terms = alias.name.split('.')
            terms[new_term_i] = new_term
            import_command.names[i].name = '.'.join(terms)
    return import_command


def _find_reference_paths(project_path, references, command_i):
    paths = []
    for ref in references:
        if ref['command_i'] == command_i:
            paths.append(ref['path'][len(project_path):])
    if not paths:
        raise RuntimeError('Cant find reference!')
    return paths

def _get_replace_paths(project_path, references, command_i):
    replace_paths = _find_reference_paths(project_path, references, command_i)
    return [path[:-3].split('/') for path in replace_paths]

def _get_slices(lists_of_terms):
    slices = []
    max_len = max([len(terms) for terms in lists_of_terms])
    for i in range(max_len):
        a_slice = []
        for terms in lists_of_terms:
            if i < len(terms):
                a_slice.append(terms[i])
        slices.append(a_slice)
    return slices

def _more_than_one_item_after_i(arr, i):
    return len(arr) - i+1 > 1

def _new_path_term_with_i(terms, replace_slices):
    i, term = None, None
    for i, term in enumerate(terms):
        if i+1 > len(replace_slices) or term not in replace_slices[i]:
            if i == 0 or not _more_than_one_item_after_i(terms, i):
                return None, None
            return i-1, PRINT_PREFIX + terms[i-1]
    if i < len(replace_slices) and term in replace_slices[i]:
        return i, PRINT_PREFIX + term
    return None, None

def _update_imports_in_ast(project_path, root, replace_paths_with_references):
    updated_commands_indices = list(set([ref['command_i'] for ref in replace_paths_with_references]))
    for i in updated_commands_indices:
        command = root.body[i]
        replace_terms = _get_replace_paths(project_path, replace_paths_with_references, i)
        replace_terms_slices = _get_slices(replace_terms)
        all_terms = _get_command_paths_terms(command)
        for alias_i, terms in enumerate(all_terms):
            path_i, new_term = _new_path_term_with_i(terms, replace_terms_slices)
            if new_term:
                root.body[i] = _update_import_command(root.body[i], alias_i, path_i, new_term)
    return root


def _file_path_from_import_path(project_root, found_paths, path):
    path_terms = path.split('.')
    for i in range(len(path_terms)):
        file_path = project_root + '/'.join(path_terms[:len(path_terms) - i]) + '.py'
        # TODO add project root here
        if os.path.isfile(file_path) and file_path not in found_paths:
            return file_path
    return None


def _files_from_import_paths(project_root, paths_with_references):
    files_with_references = []
    for paths_reference in paths_with_references:
        found_paths = set()
        for path in paths_reference['paths']:
            a_file_path = _file_path_from_import_path(project_root, found_paths, path)
            if a_file_path:
                files_with_references.append({'command_i': paths_reference['command_i'], 'path': a_file_path})
                found_paths.add(a_file_path)
    return files_with_references

def _paths_from_references(references):
    paths = []
    for ref in references:
        if 'path' in ref:
            paths.append(ref['path'])
        if 'paths' in ref:
            paths += ref['paths']
    return paths

def find_imports(project_path, code, keep_references=False):
    '''
        Return filepaths of imported project scripts.
    '''
    # TODO check for __init__.py files?
    paths_with_references = _find_imported_paths(code)
    files_with_references = _files_from_import_paths(project_path, paths_with_references)
    if keep_references:
        return files_with_references
    return _paths_from_references(files_with_references)

def add_print_imports(project_path, code):
    files_with_references = find_imports(project_path, code, keep_references=True)
    if not files_with_references:
        return ast.parse(code)
    for i, ref in enumerate(files_with_references):
        files_with_references[i]['path'] = ref['path']
    root = ast.parse(code)
    print_root = _update_imports_in_ast(project_path, root, files_with_references)
    return print_root

