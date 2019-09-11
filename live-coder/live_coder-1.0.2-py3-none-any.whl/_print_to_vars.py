import json
import html
import re

from ._get_change_objects import get_change_objects
from ._change_block_classes import (
    ExecutedFunction,
    Loop,
    Variable,
    Print,
    Function,
    IfStatement,
    Error
)
from ._constants import (
    SPLIT_KEY,
    MAX_IF_LENGTH
)
SPLIT = ' {0} '.format(SPLIT_KEY)
MAX_LOOP_WORD_LEN = 20

vars_for_func = {}
current_func = ''


def _is_new_variable(variable):
    return variable.name not in vars_for_func[current_func] or vars_for_func[current_func][variable.name] != variable.value


def _is_positive_num(num_str):
    return num_str.replace('.', '').isdigit()


def _format_value_str(value):
    value = html.escape(value)
    if value in ['None', 'True', 'False']:
        return '<bool>{0}</bool>'.format(value)
    if value.startswith('-') and _is_positive_num(value[1:]) or _is_positive_num(value):
        return '<number>{0}</number>'.format(value)
    return value


def _format_if_statement(statement):
    if len(statement) > MAX_IF_LENGTH:
        statement = statement[:MAX_IF_LENGTH] + '&hellip;'
    return '<keyword>passed</keyword> <gray>{0}</gray>'.format(statement)


def _lines_for_basic_change_object(obj):
    lines = []
    if type(obj) is Variable:
        if obj.is_self or obj.is_arg:
            return None
        if obj.name == 'return':
            value_str = _format_value_str(obj.value)
            return '<keyword>return</keyword> {0}'.format(value_str)
        elif _is_new_variable(obj) or obj.must_print:
            vars_for_func[current_func][obj.name] = obj.value
            name_str = html.escape(obj.name)
            value_str = _format_value_str(obj.value)
            return '{0} = {1}'.format(name_str, value_str)
        else:
            return None
    if type(obj) is Print:
        return '<gray>print</gray> ' + ', '.join(
            [html.escape(v) for v in obj.values]
        )
    if type(obj) is Function:
        arguments_str = ', '.join(obj.arguments)
        if obj.reference_id:
            return '<gray>{0}({1}) *{2}*</gray>'.format(obj.name, arguments_str, obj.reference_id)
        return '<gray>{0}({1})</gray>'.format(obj.name, arguments_str)
    if type(obj) is IfStatement:
        return _format_if_statement(obj.code)
    if type(obj) is Error:
        return '<red>ERROR</red> see Test Output for details'
    raise Exception('Unknown basic object.')


def _align_height(iterations_lines):
    target_height = max([len(lines) for lines in iterations_lines])
    new_iter_lines = []
    for lines in iterations_lines:
        new_lines = []
        for line in lines:
            new_lines.append('<gray>|</gray> {0}'.format(line))
        new_lines += ['<gray>|</gray> '] * (target_height - len(new_lines))
        new_iter_lines.append(new_lines)
    return new_iter_lines


def _remove_tags(raw_html):
    cleaner = re.compile('<.*?>')
    clean_text = re.sub(cleaner, '', raw_html)
    return html.unescape(clean_text)

def _line_len(line):
    return len(_remove_tags(line))


def _align_width(lines):
    target_width = 1 + max([_line_len(line) for line in lines])
    new_lines = []
    for line in lines:
        new_lines.append(
            line + '&nbsp;' * (target_width - _line_len(line))
        )
    return new_lines


def _combine_iterations(iterations):
    lines = []
    for i in range(len(iterations[0])):
        line = ''
        for iter_lines in iterations:
            line += iter_lines[i]
        lines.append(line)
    return lines


def _lines_for_loop(loop, lineno_offset):
    iteration_lines = []
    for iteration_changes in loop.changes:
        iteration_lines.append(
            _function_changes_lines(lineno_offset, iteration_changes)
        )
    vertically_aligned_iterations = _align_height(iteration_lines)
    aligned_iterations = [_align_width(lines) for lines in vertically_aligned_iterations]
    return _combine_iterations(aligned_iterations)


def _func_args(changes):
    arg_values = []
    for change in changes:
        if type(change) is not Variable or change.is_arg == False:
            break
        if change.is_self:
            arg_values.append('self')
        else:
            vars_for_func[current_func][change.name] = change.value
            arg_value_str = _format_value_str(change.value)
            value = '{0} = {1}'.format(
                html.escape(change.name), arg_value_str
            )
            arg_values.append(value)
    return arg_values


def _function_def_line(executed_function):
    name_str = html.escape(executed_function.name)
    arg_values = _func_args(executed_function.changes)
    arg_str = ', '.join(arg_values)
    if executed_function.reference_id:
        ref_str = '*{0}*'.format(executed_function.reference_id)
        return '{name}({args}) <gray>{ref}</gray>'.format(name=name_str, args=arg_str, ref=ref_str)
    return '{name}({args})'.format(name=name_str, args=arg_str)


def _get_insert_i(old_insert_i, starting_line_number_offset, output_lines, obj):
    if hasattr(obj, 'line_number'):
        return obj.line_number - starting_line_number_offset
    else:
        return old_insert_i + 1


def _add_at_i_overlap(lines, new_lines, insert_at):
    if len(new_lines) > 1:
        raise RuntimeError('Overlapping multiline statement.')
    lines[insert_at] = new_lines[0] + '<gray>,</gray> ' + lines[insert_at]
    return lines


def _pad_lines(lines, new_lines, insert_at):
    if insert_at + len(new_lines) > len(lines):
        lines += [''] * (insert_at + len(new_lines) - len(lines))
    return lines


def _add_at_i(lines, new_lines, insert_at):
    if insert_at < len(lines) and len(lines[insert_at]) > 0:
        return _add_at_i_overlap(lines, new_lines, insert_at)
    lines = _pad_lines(lines, new_lines, insert_at)
    for i, new_line in enumerate(new_lines):
        lines[insert_at + i] = new_line
    return lines


def _function_changes_lines(start_lineno, changes):
    insert_i = -1
    output_lines = []
    for obj in changes:
        if type(obj) is Variable and obj.is_arg:
            continue
        insert_i = _get_insert_i(insert_i, start_lineno, output_lines, obj)
        if type(obj) is Loop:
            loop_lines = _lines_for_loop(obj, insert_i + start_lineno)
            output_lines = _add_at_i(output_lines, loop_lines, insert_i)
        else:
            potential_line = _lines_for_basic_change_object(obj)
            if potential_line:
                output_lines = _add_at_i(output_lines, [potential_line], insert_i)
    return output_lines


def _new_context(executed_function):
    global vars_for_func
    global current_func
    current_func = executed_function.name
    vars_for_func[current_func] = {}


def _function_lines(executed_function, starting_line_number):
    _new_context(executed_function)
    lines = [_function_def_line(executed_function)]
    lines += _function_changes_lines(starting_line_number + 1, executed_function.changes)
    return lines


def _ouptput_lines_for_change_objects(executed_functions):
    '''
    Form explanation text as `block_lines` from change_bocks.

    params:
        executed function =
            ExecutedFunction
                .name = 'test'
                .file_path = 'src/main.py'
                .changes = [
                    Variable
                        .name = 'b'
                        .value = '120'
                    Function
                        .name = 'test'
                        .arguments = []
                        .reference_id = 1
                ]
                .reference_id = None

            ExecutedFunction
                .name = 'test'
                .file_path = 'src/main.py'
                .changes = [
                    Variable
                        .name = 'b'
                        .value = '0'
                ]
                .reference_id = 1
    returns:
        Variable changes, e.g:
            {
                'src/main.py': {
                    'test': {
                        'starting_line_number': 4,
                        'calls': [
                            [
                                'test()',
                                'b = 120',
                                'test() *1*',
                            ],
                            [
                                'test() *1*',
                                'b = 0'
                            ]
                        ]
                    }
                }
            }
    '''
    file_functions = {}
    for func in executed_functions:
        if func.file_path not in file_functions:
            file_functions[func.file_path] = {}
        if func.name not in file_functions[func.file_path]:
            file_functions[func.file_path][func.name] = {
                'starting_line_number': func.line_number,
                'calls': []
            }
        start = file_functions[func.file_path][func.name]['starting_line_number']
        lines = _function_lines(func, start)
        file_functions[func.file_path][func.name]['calls'].append(lines)
    return file_functions


def print_to_vars(output_string):
    '''
    Takes a string print output and returns a formated string of variable changes.

    params:
        Print string, e.g:
            {"is_arg": true, "type": "variable", "label": "s", "line_number": None} _split AAAA
            _break
            _break
            {"type": "variable", "label": "deletion_count", "line_number": 13} _split 0
            _break
            {"type": "variable", "label": "last_char"} _split None
            _break
            {"type": "loop_start", "id": 1, "code": "for char in s:"} _split
            _break
            {"type": "if", "id": 5, "conditions": [{"label": "if (char == last_char):"}, {"label": "else:"}]} _split False _split True
            _break
            {"type": "variable", "label": "last_char"} _split A
            {"type": "variable", "label": "char"} _split A
    returns:
        Variable changes as a list of lines by files and function calls e.g:
            {
                'src/main.py': {
                    'myfunc': {
                        'starting_line_number': 12,
                        'calls': [
                            [
                                'myfunc()'
                                'b = <number>120</number>',
                                'a = <number>4</number> <gray>_sum(<number>24.0</number>)</gray>',
                                '',
                                '<keyword>return</keyword> <string>'cats'</string>',
                            ]
                        ]
                    }
                }
            }

    '''
    global vars_for_func
    vars_for_func = {}
    change_objects = get_change_objects(output_string)
    return _ouptput_lines_for_change_objects(change_objects)
