import ast
import astor

from ._print_adder import PrintAdder
from ._string_tools import add_tab




def _parse_function(file_path, imported_print_modules, root, top_level_commands, class_name=None):
    print_adder = PrintAdder(file_path, imported_print_modules, root, top_level_commands, class_name=class_name)
    return print_adder.run()


def _parse_class(file_path, imported_print_modules, root, top_level_commands):
    class_name = root.name
    new_body = []
    for command in root.body:
        if type(command) is ast.ClassDef:
            new_body.append(_parse_class(file_path, imported_print_modules, command, top_level_commands))
        elif type(command) is ast.FunctionDef:
            new_body.append(_parse_function(file_path, imported_print_modules, command, top_level_commands, class_name=class_name))
        else:
            new_body.append(command)
    root.body = new_body
    return root


def add_execution_prints(file_path, imported_print_modules, root):
    '''
        Add prints to show the execution of every function in the code.
    '''
    new_body = []
    for command in root.body:
        if type(command) is ast.ClassDef:
            new_body.append(
                _parse_class(file_path, imported_print_modules, command, root.body)
            )
        elif type(command) is ast.FunctionDef:
            new_body.append(
                _parse_function(file_path, imported_print_modules, command, root.body)
            )
        else:
            new_body.append(command)
    root.body = new_body
    return astor.to_source(root)[:-1]


