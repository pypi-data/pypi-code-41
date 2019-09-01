import ast
import astor
import copy
import json

from ._get_variables import variables_in_commands, functions_in_commands
from ._string_tools import get_tab_length, get_line_tab, remove_tab, add_tab

from ._constants import (
    LOOP_TYPE,
    IF_TYPE,
    BODY_KEY,
    LOOP_KEY,
    IF_KEY_TEMPLATE,
    BREAK_KEY,
    SPLIT_KEY,
    SUBSPLIT_KEY,
    LABEL_TEMPLATE,
    VARIABLE_KEY,
    FUNCTION_KEY
)
QUOTED_PRINT_TEMPLATE = "print('{0}')"
SINGLE_TAB = ' '*4
SUPER_COMMANDS = [ast.For, ast.While, ast.If, ast.With, ast.Try]

class PrintAdder:

    def __init__(self, file_path, imported_print_modules, function_def_root, top_level_commands, class_name=None):
        '''
            Adds print statements to a function.
            @params:
                file_path: path of the file holding the function
                imported_print_modules: imported print modules, used to find function attribute calls
                function_def_root: ast.FunctionDef node of the functions AST
                top_level_commands: top level commands for the function's script
                class_name: name of the class holding the function, None => no class

            @returns:
                ast.FunctionDef with added print statements in it's body
        '''
        self.file_path = file_path
        self.imported_print_modules = imported_print_modules
        self.function_def_root = function_def_root
        self.top_level_commands = top_level_commands
        self.class_name = class_name

        self.referenced_variabels = set()
        self.loop_count = 0
        self.try_count = 0

        self.function_name = self._get_function_name()
        self.defined_functions = self._get_defined_functions()


    def _get_function_name(self):
        name = self.function_def_root.name
        if self.class_name:
            name = self.class_name + '.' + name
        return name

    def _get_defined_functions(self):
        '''
            Get set of defined function names and imported names.
        '''
        all_functions = set()
        for command in self.top_level_commands:
            if type(command) is ast.FunctionDef:
                all_functions.add(command.name)
            elif type(command) in [ast.Import, ast.ImportFrom]:
                imports = [] if type(command) is ast.Import else [command.module]
                for alias in command.names:
                    imports.append(alias.name)
                all_functions.update(set(imports))
        return all_functions

    @staticmethod
    def _new_print(obj, code=''):
        json_str = json.dumps(obj)
        formatted_json = json_str.replace('"', '\\"')
        if type(code) is list:
            joiner = ', "{0}", '.format(SPLIT_KEY)
            code = joiner.join(['repr({0})'.format(snippet) for snippet in code])
        elif code:
            code = 'repr({0})'.format(code)
        return ast.parse(
            'print("{0}", "{1}", {2})'.format(formatted_json, SPLIT_KEY, code)
        ).body[0]

    @staticmethod
    def _hide_self_var(attributes, var):
        return 'show_self' not in attributes and var == 'self'

    def _new_var_print(self, line_number, var, **attributes):
        attributes['type'] = 'variable'
        attributes['line_number'] = line_number
        attributes['label'] = attributes.get('label', var)
        if self._hide_self_var(attributes, var):
            return None
        return self._new_print(attributes, code=attributes.get('value', var))

    @staticmethod
    def _new_break_print(break_key):
        return ast.parse(
            QUOTED_PRINT_TEMPLATE.format(break_key)
        ).body[0]

    def _new_function_print(self, line_number, function_name, arguments_code_snippets):
        attributes = {
            'type': 'function',
            'name': function_name,
            'line_number': line_number
        }
        return self._new_print(attributes, code=arguments_code_snippets)

    def _print_functions(self, line_number, functions):
        print_statements = []
        for func in functions:
            print_statements.append(
                self._new_function_print(line_number, func['name'], func['arguments'])
            )
        return print_statements

    def _print_vars(self, line_number, variables, **shared_attributes):
        self.referenced_variabels.update(variables)
        print_statements = []
        for var in variables:
            a_print = self._new_var_print(line_number, var, **shared_attributes)
            if a_print:
                print_statements.append(a_print)
        return print_statements

    def _get_args(self):
        args = []
        for arg in self.function_def_root.args.args:
            args.append(arg.arg)
        return args

    def _print_args(self):
        commands = []
        args = self._get_args()
        if args:
            if args[0] == 'self':
                commands.append(
                    self._new_var_print(None, None, is_arg=True, show_self=True)
                )
                del args[0]
            commands += self._print_vars(None, args, is_arg=True)
        return commands

    def _print_def_call(self):
        return self._new_print({
            'type': 'function_call', 'name': self.function_name,
            'file_path': self.file_path, 'line_number': self.function_def_root.lineno
        })

    def _print_def(self):
        commands = []
        commands.append(self._print_def_call())
        commands += self._print_args()
        commands.append(self._new_break_print(BREAK_KEY))
        return commands

    @staticmethod
    def _command_to_source(command):
        source_lines = astor.to_source(command)[:-1].split('\n')
        return add_tab(
            4 + command.col_offset,
            source_lines
        )

    def _print_return(self, a_command):
        returning_value_ast = a_command.value
        returning_value_code = astor.to_source(returning_value_ast)[:-1]
        return_print = self._new_var_print(
            a_command.lineno,
            returning_value_code,
            label='return'
        )
        commands = []
        if return_print:
            commands.append(return_print)
        commands.append(a_command)
        return commands

    @staticmethod
    def _is_a_print_command(command):
        return (
            type(command) is ast.Expr
            and type(command.value) is ast.Call
            and type(command.value.func) is ast.Name
            and command.value.func.id == 'print'
        )

    def _print_a_print(self, command):
        arg_strings = []
        for arg in command.value.args:
            arg_strings.append(
                astor.to_source(arg)[:-1]
            )
        attributes = {'type': 'print', 'line_number': command.lineno}
        return [self._new_print(attributes, code=arg_strings)]

    def _print_command(self, a_command):
        commands = []
        functions = functions_in_commands(self.defined_functions, self.imported_print_modules, [a_command])
        commands += self._print_functions(a_command.lineno, functions)
        commands.append(a_command)
        variables = variables_in_commands(self.defined_functions, [a_command])
        commands += self._print_vars(a_command.lineno, variables)
        return commands

    def _print_what_for_is_iterating(self, target):
        if type(target) is ast.Name:
            variable_name = target.id
            a_print = self._new_var_print(target.lineno, variable_name, must_print=True)
            if a_print:
                return [a_print]
            return []
        if type(target) is ast.Tuple:
            print_commands = []
            for name_command in target.elts:
                name = name_command.id
                a_print = self._new_var_print(name_command.lineno, name, must_print=True)
                if a_print:
                    print_commands.append(a_print)
            return print_commands
        raise RuntimeError('Unknown type in for loop.')

    def _print_loop_body(self, loop_command, loop_id):
        new_body = []
        if type(loop_command) is ast.For:
            new_body += self._print_what_for_is_iterating(loop_command.target)
        new_body += self._add_prints_to_commands(loop_command.body)
        new_body.append(self._new_print({'type': 'loop_break', 'id': loop_id}))
        return new_body

    def _new_loop_id(self):
        self.loop_count += 1
        return '{0}_loop_{1}'.format(self.function_name, self.loop_count)

    def _print_loop(self, loop_command):
        loop_id = self._new_loop_id()
        attributes = {'type': 'loop_start', 'line_number': loop_command.lineno, 'id': loop_id}
        commands = [self._new_print(attributes)]
        loop_command.body = self._print_loop_body(loop_command, loop_id)
        commands.append(loop_command)
        commands.append(self._new_print({'type': 'loop_end', 'id': loop_id}))
        return commands


    def _find_conditions(self, if_command):
        conditions = [
            {
                'condition': astor.to_source(if_command.test)[:-1],
                'line_number': if_command.lineno
            }
        ]
        if len(if_command.orelse) == 0:
            return conditions
        or_else = if_command.orelse[0]
        if type(or_else) is ast.If:
            conditions += self._find_conditions(or_else)
        else:
            conditions.append({'condition': 'else'})
        return conditions


    def _print_if_checks(self, starting_lineno, if_command):
        attributes = {
            'type': 'if',
            'id': starting_lineno,
            'line_number': starting_lineno,
            'conditions': []
        }
        code_snippets = []
        conditions = self._find_conditions(if_command)
        passed_if = False
        for condition_info in conditions:
            if condition_info['condition'] == 'else':
                attributes['conditions'].append({'label': 'else:'})
                code_snippets.append(True)
            else:
                if passed_if is False:
                    if_type = 'if'
                    passed_if = True
                else:
                    if_type = 'elif'
                label = '{0} {1}:'.format(if_type, condition_info['condition'])
                attributes['conditions'].append({'label': label, 'line_number': condition_info['line_number']})
                code_snippets.append(condition_info['condition'])
        return self._new_print(attributes, code=code_snippets)

    def _print_if(self, if_command):
        '''
        ast.If
            .body = list of commands
            .test = if statement
            .orelse = (in a len 1 list) elif statement OR else list of commands
        '''
        if_checks = self._print_if_checks(if_command.lineno, if_command)
        root_if_command = if_command
        while if_command:
            if_command.body = self._add_prints_to_commands(if_command.body)
            or_else = if_command.orelse
            if len(or_else) == 0:
                break
            elif type(or_else[0]) is ast.If:
                if_command = or_else[0]
            elif len(or_else) > 0:
                if_command.orelse = self._add_prints_to_commands(or_else)
                break
        return [if_checks, root_if_command]


    def _get_with_var(self, with_command):
        for with_item in with_command.items:
            var = with_item.optional_vars
            if type(var) is ast.Name:
                return var.id
        return None

    def _print_with(self, with_command):
        '''
        ast.With
            .items = holds x in 'with a() as x:'
            .body = list of commands
        '''
        with_command.body = self._add_prints_to_commands(with_command.body)
        with_var = self._get_with_var(with_command)
        if with_var:
            print_list = self._print_vars(with_command.lineno, [with_var])
            with_command.body = print_list + with_command.body
        return [with_command]

    def _get_except_var(self, except_command):
        if except_command.name:
            return self._print_vars(except_command.lineno, [except_command.name])
        return []

    def _print_except(self, except_command, try_id):
        '''
        ast.ExceptHandler
            .name = name of exception holding variable (can be None)
            .body = list of commands
        '''
        except_print = self._new_print({'type': 'except', 'id': try_id})
        except_command.body = [except_print] + self._get_except_var(except_command) + self._add_prints_to_commands(except_command.body)
        return except_command

    def _new_try_id(self):
        self.try_count += 1
        return '{0}_try_{1}'.format(self.function_name, self.try_count)

    def _add_prints_to_try_command_lists(self, try_command):
        if try_command.finalbody:
            try_command.finalbody = self._add_prints_to_commands(try_command.finalbody)
        if try_command.orelse:
            try_command.orelse = self._add_prints_to_commands(try_command.orelse)
        return try_command

    def _print_try(self, try_command):
        '''
        ast.Try
            .body = list of commands
            .handlers = list of handlers (each with list of commands in .body)
            .orelse = list of commands in 'else:' section
            .finalbody = list of commands in 'finally:' section
        '''
        try_id = self._new_try_id()
        print_start = self._new_print({
            'type': 'try_start', 'id': try_id
        })
        print_end = self._new_print({
            'type': 'try_end', 'id': try_id
        })
        try_command.body = [print_start] + self._add_prints_to_commands(try_command.body) + [print_end]
        for i, except_command in enumerate(try_command.handlers):
            try_command.handlers[i] = self._print_except(except_command, try_id)
        try_command = self._add_prints_to_try_command_lists(try_command)
        return [try_command]

    def _add_prints_to_super_command(self, command):
        if type(command) in [ast.For, ast.While]:
            return self._print_loop(command)
        if type(command) is ast.If:
            return self._print_if(command)
        if type(command) is ast.With:
            return self._print_with(command)
        if type(command) is ast.Try:
            return self._print_try(command)


    def _add_prints(self, command):
        if type(command) in SUPER_COMMANDS:
            return self._add_prints_to_super_command(command)
        if self._is_a_print_command(command):
            return self._print_a_print(command)
        return self._print_command(command)


    def _prints_with_breaks_with_command(self, command):
        break_command = self._new_break_print(BREAK_KEY)
        if type(command) is ast.Return:
            return [break_command] + self._print_return(command)
        commands_with_prints = self._add_prints(command)
        return [break_command] + commands_with_prints + [break_command]


    @staticmethod
    def _next_command_lineno(commands, i, command_after_last_lineno):
        if i+1 >= len(commands):
            return command_after_last_lineno
        return commands[i + 1].lineno

    def _add_prints_to_commands(self, commands):
        commands_with_prints = []
        for command in commands:
            commands_with_prints += self._prints_with_breaks_with_command(command)
        return commands_with_prints

    def run(self):
        new_body = []
        new_body += self._print_def()
        new_body += self._add_prints_to_commands(
            self.function_def_root.body
        )
        if type(self.function_def_root.body[-1]) is not ast.Return:
            new_body.append(self._new_print({'type': 'function_end'}))
        self.function_def_root.body = new_body
        return self.function_def_root

