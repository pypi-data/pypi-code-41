import json

from ._get_change_lines import get_change_lines
from ._un_nest_functions import UnNestExecutedFunctions
from ._string_tools import (
    _remove_prefix,
    _remove_suffix
)
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
    LOOP_BREAK_TEMPLATE
)

def _parse_change_line(change_line):
    change_line = _remove_prefix(change_line, '{0} '.format(SPLIT_KEY))
    change_line = _remove_suffix(change_line, ' {0}'.format(SPLIT_KEY))
    words = change_line.split(' {0} '.format(SPLIT_KEY))
    attributes = json.loads(words[0])
    values = words[1:]
    return attributes, values


def _lines_for_each_iteration(lines, loop_id):
    loop_break = LOOP_BREAK_TEMPLATE.format(loop_id)
    iterations = []
    last_iter_i = -1
    i = -1
    for i, line in enumerate(lines):
        if line == loop_break:
            iterations.append(lines[ last_iter_i + 1 :i ])
            last_iter_i = i
    if last_iter_i == -1:
        # No loop break found.
        iterations.append(lines)
    elif last_iter_i != i:
        # No ending loop break.
        iterations.append(lines[ last_iter_i + 1: ])
    return iterations


def _loop_change_block_from_lines(change_lines, loop_id):
    iteration_lines = _lines_for_each_iteration(change_lines, loop_id)
    iteration_change_blocks = []
    for lines in iteration_lines:
        iteration_change_blocks.append(
            _change_blocks_from_lines(lines)
        )
    return iteration_change_blocks


def _get_function_change_lines(change_lines, start, end):
    function_change_lines = change_lines[start+1:end+1]
    end_attributes, _ = _parse_change_line(function_change_lines[-1])
    if end_attributes['type'] == 'function_end':
        return function_change_lines[:-1]
    return function_change_lines

class NoLoopEnd(Exception):
    pass

def _find_loop_end(start_attributes, change_lines, start_i):
    for i in range(start_i, len(change_lines)):
        if 'loop_end' in change_lines[i]:
            end_attributes, _ = _parse_change_line(change_lines[i])
            if end_attributes['type'] == 'loop_end' and end_attributes['id'] == start_attributes['id']:
                return i
    if 'return' in  change_lines[i]:
        end_attributes, _ = _parse_change_line(change_lines[i])
        if end_attributes['type'] == 'variable' and end_attributes['label'] == 'return':
            return i + 1
    raise NoLoopEnd()


class NoFunctionEnd(Exception):
    pass

def _find_function_end(attributes, change_lines, current_i):
    function_depth = 1
    i = current_i
    while function_depth > 0 and i < len(change_lines)-1:
        i += 1
        line = change_lines[i]
        if 'function_call' in line:
            start_attributes, _ = _parse_change_line(line)
            if start_attributes['type'] == 'function_call':
                function_depth += 1
        if 'function_end' in line or 'return' in line:
            end_attributes, _ = _parse_change_line(line)
            if end_attributes['type'] == 'function_end' or end_attributes['type'] == 'variable' and end_attributes['label'] == 'return':
                function_depth -= 1
    if function_depth != 0:
        raise NoFunctionEnd()
    return i


def _basic_change_block_from_line(attributes, values):
    if attributes['type'] == 'variable':
        if len(values) > 1:
            raise Exception('Many values for a single variable.')
        return Variable(
            attributes['label'],
            values[0],
            attributes['line_number'],
            attributes.get('is_arg', False),
            attributes.get('must_print', False),
            attributes.get('is_self', False)
        )
    elif attributes['type'] == 'print':
        return Print(values, attributes['line_number'])
    elif attributes['type'] == 'function':
        return Function(attributes['name'], values, attributes['line_number'])
    elif attributes['type'] == 'if':
        if 'True' in values:
            for i in range(len(attributes['conditions'])):
                if values[i] == 'True':
                    break
            passed_condition = attributes['conditions'][i]
            if 'line_number' in passed_condition:
                line_number = passed_condition['line_number']
            else:
                line_number = attributes['line_number']
            return IfStatement(passed_condition['label'], line_number)
        return None
    else:
        raise Exception('Unkown line type.')


def _change_block_from_line(change_lines, current_i):
    attributes, values = _parse_change_line(change_lines[current_i])
    if attributes['type'] == 'function_call':
        try:
            end_i = _find_function_end(attributes, change_lines, current_i)
            function_change_lines = _get_function_change_lines(change_lines, current_i, end_i)
            function_change_blocks = _change_blocks_from_lines(function_change_lines)
        except NoFunctionEnd:
            end_i = len(change_lines) - 1
            function_change_lines = change_lines[current_i+1:end_i+1]
            function_change_blocks = _change_blocks_from_lines(function_change_lines)
            if type(function_change_blocks[-1]) is not Loop:
                function_change_blocks.append(Error())
        return end_i + 1, ExecutedFunction(attributes['name'], attributes['file_path'], attributes['line_number'], function_change_blocks)
    elif attributes['type'] == 'loop_start':
        try:
            end_i = _find_loop_end(attributes, change_lines, current_i)
            loop_change_blocks = _loop_change_block_from_lines(change_lines[current_i+1:end_i], attributes['id'])
        except NoLoopEnd:
            end_i = len(change_lines)
            loop_change_blocks = _loop_change_block_from_lines(change_lines[current_i+1:end_i], attributes['id'])
            loop_change_blocks[-1].append(Error())
        return end_i + 1, Loop(attributes['id'], attributes['line_number'], loop_change_blocks)
    else:
        current_i += 1
        return current_i, _basic_change_block_from_line(attributes, values)


def _change_blocks_from_lines(change_block_lines):
    change_blocks = []
    i = 0
    while i < len(change_block_lines):
        i, change_value = _change_block_from_line(change_block_lines, i)
        if change_value:
            change_blocks.append(change_value)
    return change_blocks


def get_change_objects(output_string):
    '''
    Form `change blocks` given printed outputs.

    params:
        Print string, e.g:
            {"is_arg": true, "type": "variable", "label": "s"} _split AAAA
            _break
            {"type": "variable", "label": "deletion_count"} _split 0
            _break
            {"type": "if", "id": 5, "conditions": [{"label": "if (char == last_char):"}, {"label": "else:"}]} _split False _split True
            _break
            {"type": "variable", "label": "last_char"} _split A
            {"type": "variable", "label": "char"} _split A
    returns:
        ExecutedFunction
            .name = 'myfunc'
            .file_path = 'src/main.py'
            .line_number = 13
            .changes = [
                Variable
                    .name = 'b'
                    .value = 120
                    .is_arg = True
                    .line_number = 14
                Function
                    .name = '_test'
                    .arguments = [1]
                    .line_number = 15
                IfStatement
                    .code = 'if z:',
                    .line_number = 17
                Loop
                    .id = 1
                    .line_number = 20
                    .changes = [
                        [
                            Function
                                .name = '_test_test'
                                .arguments = [2, 1]
                                .line_number = 21
                        ],,,
                    ]
            ],,,
    '''
    change_lines = get_change_lines(output_string)
    nested_change_blocks = _change_blocks_from_lines(change_lines)
    if len(nested_change_blocks) > 1 or type(nested_change_blocks[0]) is not ExecutedFunction:
        raise RuntimeError('Unexpected un-nested change objects format.')
    un_nested_functions = UnNestExecutedFunctions().run(nested_change_blocks[0])
    return un_nested_functions
