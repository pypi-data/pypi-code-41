import ast
import astor

from ._built_in_methods import BUILTIN_METHODS
from ._constants import PRINT_PREFIX

LEAF_TYPES = (
    ast.UnaryOp,
    ast.List,
    ast.Dict,
    ast.Tuple,
    ast.Set,
    ast.Str,
    ast.Num,
    ast.Load
)


def functions_in_commands(present_functions, imported_print_modules, commands):
    '''
        Get a list of functions mentioned list of ASTs `commands`.

        params:
            commands: list of ASTs of code
        returns:
            list of functions with the form:
                [{
                    'name': {function name},
                    'arguments':
                        [{code for arg1}, {code for arg2},,,]
                },,,]
    '''
    functions = []
    for command in commands:
        functions += _get_functions(present_functions, imported_print_modules, command)
    return functions


def _get_functions(present_functions, imported_print_modules, command):
    functions = []
    leaf_nodes = _leaf_nodes(command, stop_at=(ast.Call, ast.ListComp))
    for node in leaf_nodes:
        if type(node) is ast.ListComp:
            if (hasattr(node.elt, 'func') is False):
                continue
            func = node.elt.func
            arguments = []
        else:
            func = node.func
            arguments = node.args
        if hasattr(func, 'id'):
            if func.id in BUILTIN_METHODS or func.id in present_functions:
                functions.append(
                    _new_function(func.id, arguments)
                )
        elif type(func.value) is ast.Name and func.value.id in imported_print_modules:
            print_file = func.value.id
            non_print = print_file[len(PRINT_PREFIX):]
            functions.append(
                _new_function(non_print + '.' + func.attr, arguments)
            )
        if type(node) is ast.ListComp:
            break
    return functions


def _all_nodes_are_names(nodes):
    for n in nodes:
        if type(n) is not ast.Name:
            return False
    return True


def _command_code(command):
    return astor.to_source(command)[:-1]


def _new_function(name, arguments):
    return {
        'name': name,
        'arguments': [
            _command_code(arg) for arg in arguments
        ]
    }


def variables_in_commands(present_functions, commands):
    '''
        Get a list of variables mentioned list of ASTs `commands`.

        params:
            functions: list of functions in the code
            commands: list of ASTs of code
        returns:
            list of variable names
    '''
    variables = set()
    for command in commands:
        variables.update(_get_variables(present_functions, command))
    return list(variables)


def _get_variables(present_functions, command):
    variables = set()
    leaf_nodes = _leaf_nodes(command, stop_at=(ast.Name, ast.ListComp))
    for node in leaf_nodes:
        if type(node) is ast.ListComp:
            break
        if type(node) is ast.Name:
            if not isinstance(node.ctx, (ast.Load)) or (node.id not in BUILTIN_METHODS and node.id not in present_functions):
                variables.add(node.id)
    return variables


def _leaf_nodes(node, stop_at=ast.Name):
    leaves = []
    if isinstance(node, stop_at):
        if type(node) is ast.Name:
            return [node]
        leaves = [node]
    children = list(ast.iter_child_nodes(node))
    for child in children:
        leaves += _leaf_nodes(child, stop_at=stop_at)
    return leaves


