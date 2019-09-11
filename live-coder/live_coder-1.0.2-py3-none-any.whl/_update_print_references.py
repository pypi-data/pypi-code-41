import string
import astor
import ast
import os

from ._constants import (
    PRINT_PREFIX
)

def _from_prefix(code_relative_path, level):
    if level > 0:
        path_list = code_relative_path.split('/')
        file_depth = level - 1
        if file_depth > 0:
            path_list = path_list[: - file_depth]
        return path_list
    return []

def _add_prefix(code_relative_path, base, level):
    prefix = _from_prefix(code_relative_path, level)
    base_list = prefix + base.split('.')
    return '.'.join(base_list)

def _add_base(base, name):
    if base:
        return base + '.' + name
    return name

def _parse_ImportFrom(code_relative_path, importFrom):
    paths = []
    base = _add_prefix(code_relative_path, importFrom.module, importFrom.level)
    for alias in importFrom.names:
        name = _add_base(base, alias.name)
        paths.append(name)
    return paths

def _parse_Import(an_import):
    paths = []
    for alias in an_import.names:
        paths.append(alias.name)
    return paths

def _parse_import(code_relative_path, command):
    if type(command) is ast.ImportFrom:
        return _parse_ImportFrom(code_relative_path, command)
    if type(command) is ast.Import:
        return _parse_Import(command)
    return None

def _find_imported_paths(code_relative_path, code):
    root = ast.parse(code)
    paths = []
    for i, command in enumerate(root.body):
        result = _parse_import(code_relative_path, command)
        if result:
            paths.append({'command_i': i, 'paths': result})
    return paths

def _update_import_command_old(import_command, alias_i, new_term_i, new_term):
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

def _A_starts_with_B(list_a, list_b):
    return list_a[:len(list_b)] == list_b

def _get_from_terms(command):
    return command.module.split('.')

def _update_import_from(command, old_file_id):
    terms = _get_from_terms(command)
    terms[terms.index(old_file_id)] = PRINT_PREFIX + old_file_id
    command.module = '.'.join(terms)
    return command

def _get_import_paths(command):
    return [alias.name.split('.') for alias in command.names]

def _print_file_id(import_path, print_file_i):
    new_import_path = list(import_path)
    new_import_path[print_file_i] = PRINT_PREFIX + new_import_path[print_file_i]
    return '.'.join(new_import_path)

def _update_import_with_imported_print_file(command, file_id_after_from):
    var_switches = []
    import_paths = _get_import_paths(command)
    for i, path in enumerate(import_paths):
        if _A_starts_with_B(path, file_id_after_from):
            new_import_str = _print_file_id(path, len(file_id_after_from) - 1)
            command.names[i].name = new_import_str
            var_switches.append(['.'.join(path), new_import_str])
    return command, var_switches

def _file_referenced_in_from(from_terms, file_id, level):
    return _A_starts_with_B(from_terms, file_id[level:])

def _file_referenced_in_import(file_id, from_terms):
    return _A_starts_with_B(file_id, from_terms)

def _update_import_command(command, file_id):
    if type(command) is ast.ImportFrom:
        from_terms = _get_from_terms(command)
        if _file_referenced_in_from(from_terms, file_id, command.level):
            command = _update_import_from(command, file_id[-1])
            return command, []
        if _file_referenced_in_import(file_id, from_terms):
            return _update_import_with_imported_print_file(command, file_id[len(from_terms):])
        raise Exception("ImportFrom doesn't reference it's assigned file id.")
    elif type(command) is ast.Import:
        return _update_import_with_imported_print_file(command, file_id)

def _update_imports(root, command_i_s, file_ids):
    var_switches = []
    for i in range(len(command_i_s)):
        command_i = command_i_s[i]
        command = root.body[command_i]
        file_id = file_ids[i]
        updated_command, new_var_switches = _update_import_command(command, file_id)
        root.body[command_i] = updated_command
        var_switches += new_var_switches
    return root, var_switches

def _file_path_from_import_path(project_root, found_paths, path):
    path_terms = path.split('.')
    for i in range(len(path_terms)):
        file_id = path_terms[:len(path_terms) - i]
        file_path = project_root + '/'.join(file_id) + '.py'
        if os.path.isfile(file_path) and file_path not in found_paths:
            return file_path, file_id
    return None, None


def _files_from_import_paths(project_root, paths_with_references):
    files_with_references = []
    for paths_reference in paths_with_references:
        found_paths = set()
        for path in paths_reference['paths']:
            file_path, file_id = _file_path_from_import_path(project_root, found_paths, path)
            if file_path:
                files_with_references.append({
                    'command_i': paths_reference['command_i'],
                    'path': file_path,
                    'file_id': file_id
                })
                found_paths.add(file_path)
    return files_with_references

def _paths_from_references(references):
    paths = []
    for ref in references:
        if 'path' in ref:
            paths.append(ref['path'])
        if 'paths' in ref:
            paths += ref['paths']
    return list(set(paths))

def _relative_path(project_path, file_path):
    file_folder_path = file_path[:-3].split('/')[:-1]
    file_folder_path_str = '/'.join(file_folder_path)
    return file_folder_path_str[len(project_path):]

def find_imports(project_path, code_path, code, keep_references=False):
    '''
        Return filepaths of imported project scripts.
    '''
    code_relative_path = _relative_path(project_path, code_path)
    if not code_relative_path:
        return []
    path_ids_with_references = _find_imported_paths(code_relative_path, code)
    files_with_references = _files_from_import_paths(project_path, path_ids_with_references)
    if keep_references:
        return files_with_references
    return _paths_from_references(files_with_references)

def _col(l, k):
    return [d[k] for d in l]

VAR_TOKENS = string.ascii_letters + string.digits + '_'
def _char_is_part_of_var_name(char):
    return char in VAR_TOKENS

def _node_var_match(node, var_str):
    if type(node) in [ast.Load, ast.Store, ast.keyword, ast.Eq]:
        return False
    code = astor.to_source(node)
    if code[:len(var_str)] == var_str:
        if len(code) > len(var_str) and _char_is_part_of_var_name(code[len(var_str)]):
            return False
        return True
    return False

def _array_diff(a, b):
    for i, a_v in enumerate(a):
        if a_v != b[i]:
            return a_v, b[i]
    raise Exception("Arrays aren't different")

def _switch_matching_node_attr(node, switch_k, switch_v):
    for k, v in ast.iter_fields(node):
        if v == switch_k:
            setattr(node, k, switch_v)
            return node
    for child in ast.iter_child_nodes(node):
        _switch_matching_node_attr(child, switch_k, switch_v)
    return node

def _switch_node_var_attr(node, curr_var, new_var):
    # Find target str, the str being switched.
    switch_pair = _array_diff(curr_var.split('.'), new_var.split('.'))
    return _switch_matching_node_attr(node, switch_pair[0], switch_pair[1])

def _switch_var(root, curr_var, new_var):
    # switch all references to this variable (outside of imports)
    for node in ast.iter_child_nodes(root):
        if type(node) in [ast.Import, ast.ImportFrom]:
            continue
        elif _node_var_match(node, curr_var):
            node = _switch_node_var_attr(node, curr_var, new_var)
        else:
            node = _switch_var(node, curr_var, new_var)
    return root

def _switch_vars(root, switches):
    for switch in switches:
        root = _switch_var(root, switch[0], switch[1])
    return root

def _is_root_of_patch(path):
    patch_path = 'unittest.mock.patch'.split('.')
    for i, name in enumerate(patch_path):
        if i >= len(path):
            return True
        if name != path[i]:
            return False
    return path == patch_path

def _patch_refs_for_import(command, from_path=[]):
    refs = []
    for name in command.names:
        import_path = name.name.split('.')
        path = from_path + import_path
        if _is_root_of_patch(path):
            remaining = ['unittest', 'mock', 'patch'][len(path):]
            if name.asname:
                potential_ref = [name.asname] + remaining
            else:
                potential_ref = import_path + remaining
            refs.append(potential_ref)
    return refs

def _potential_patch_refs(root):
    '''
        Find all possible references of patch() in the ast.
    '''
    patch_potential_refs = []
    for command in root.body:
        if type(command) in [ast.Import, ast.ImportFrom]:
            if type(command) is ast.ImportFrom:
                from_path = command.module.split('.')
                if _A_starts_with_B(['unittest', 'mock'], from_path):
                    patch_potential_refs += _patch_refs_for_import(command, from_path)
            else:
                patch_potential_refs += _patch_refs_for_import(command)
    return patch_potential_refs


def _is_matching_call(node, func_name):
    code = astor.to_source(node)
    return code[:code.index('(')] == func_name

def _find_patch_references(root, patch_str):
    '''
        Find all ast.Call's with source code "{patch_str}(...arguments...)"
    '''
    refs = []
    for node in ast.iter_child_nodes(root):
        if type(node) is ast.Call and _is_matching_call(node, patch_str):
            refs.append(node)
        else:
            refs += _find_patch_references(node, patch_str)
    return refs

def _switch_patch_str(call_node, curr_str, new_str):
    for arg in call_node.args:
        if type(arg) is ast.Str and _A_starts_with_B(arg.s, curr_str):
            arg.s = new_str + arg.s[len(curr_str):]
    return call_node

def _switch_patches_using_path(root, patch_path, curr_str, new_str):
    patch_references = _find_patch_references(root, '.'.join(patch_path))
    for ref in patch_references:
        ref = _switch_patch_str(ref, curr_str, new_str)
    return root


def _switch_patches_single(root, potential_patch_refes, curr_str, new_str):
    for patch_ref in potential_patch_refes:
        root = _switch_patches_using_path(root, patch_ref, curr_str, new_str)
    return root


def _switch_patches(root, switches):
    potential_patch_refes = _potential_patch_refs(root)
    for switch in switches:
        root = _switch_patches_single(root, potential_patch_refes, switch[0], switch[1])
    return root

def update_print_file_references(project_path, code_path, code):
    '''
    Update import statements, pathces and variable references in code.
    '''
    root = ast.parse(code)
    print_imports = find_imports(project_path, code_path, code, keep_references=True)
    root, import_var_switches = _update_imports(root, _col(print_imports, 'command_i'), _col(print_imports, 'file_id'))
    root = _switch_vars(root, import_var_switches)
    root = _switch_patches(root, import_var_switches)
    imported_print_modules = [switch[1] for switch in import_var_switches]
    return root, imported_print_modules
