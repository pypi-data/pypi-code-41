from ._un_nest_functions import UnNestExecutedFunctions
from ._change_classes import (
    ExecutedFunction,
    Loop,
    Variable,
    Print,
    Function,
    IfStatement,
    Error,
    Try
)

def _variable_change_object(props, values):
    if len(values) > 1:
        raise Exception('Many values for a single variable.')
    return Variable(
        props['label'],
        values[0],
        props['line_number'],
        props.get('is_arg', False),
        props.get('must_print', False),
        props.get('is_self', False)
    )

def _if_change_object(props, values):
    if 'True' in values:
        passed_condition = props['conditions'][values.index('True')]
        line_number = passed_condition.get('line_number', props['line_number'])
        return IfStatement(passed_condition['label'], line_number)
    return None

def _try_change_object(try_type, try_id):
    if try_type == 'try_start':
        return Try(try_id)
    return None

def _basic_change_object(props, values):
    if props['type'] == 'variable':
        return _variable_change_object(props, values)
    elif props['type'] == 'print':
        return Print(values, props['line_number'])
    elif props['type'] == 'function':
        return Function(props['name'], values, props['line_number'])
    elif props['type'] == 'if':
        return _if_change_object(props, values)
    elif props['type'] in ['except', 'try_start', 'try_end']:
        return _try_change_object(props['type'], props['id'])
    elif props['type'] == 'loop_break':
        return None
    else:
        raise Exception('Unkown line type.')

def _is_function_end(props):
    return props['type'] == 'function_end' or props['type'] == 'variable' and props['label'] == 'return'

def _function_changes(try_ids, in_same_loop, props):
    if props['type'] == 'function_call':
        try_ids.append([])
        if in_same_loop:
            in_same_loop.append(False)
    elif _is_function_end(props):
        try_ids.pop()
        if in_same_loop:
            in_same_loop.pop()
    return try_ids, in_same_loop

class CutByCaughtException(Exception):
    def __init__(self, message, try_id):
        super(CutByCaughtException, self).__init__(message)
        self.try_id = try_id

def _last_func_with_try_id(func_try_ids, target_try_id):
    for i, try_ids in reversed(list(enumerate(func_try_ids))):
        if target_try_id in try_ids:
            return i, try_ids.index(target_try_id)
    raise CutByCaughtException('found except for unseen try id', target_try_id)

def _clear_after_i(l, i):
    return l[:i+1]

def _try_changes(try_ids, in_same_loop, props):
    if props['type'] == 'try_start':
        try_ids[-1].append(props['id'])
    elif props['type'] == 'try_end':
        if try_ids[-1][-1] != props['id']:
            raise RuntimeError('Non matching try ids for try end.')
        try_ids[-1].pop()
    elif props['type'] == 'except':
        func_i, try_i = _last_func_with_try_id(try_ids, props['id'])
        try_ids = _clear_after_i(try_ids, func_i)
        try_ids[-1] = _clear_after_i(try_ids[-1], try_i-1)
        if in_same_loop:
            in_same_loop = _clear_after_i(in_same_loop, func_i)
    return try_ids, in_same_loop

def _update_function_try_ids(func_try_ids, line, in_same_loop=None):
    props = line[0]
    func_try_ids, in_same_loop = _function_changes(func_try_ids, in_same_loop, props)
    func_try_ids, in_same_loop = _try_changes(func_try_ids, in_same_loop, props)
    if in_same_loop is not None:
        return func_try_ids, in_same_loop
    return func_try_ids

class FunctionCut(Exception):
    def __init__(self, message, end_i, try_id=None):
        super(FunctionCut, self).__init__(message)
        self.end_i = end_i
        self.try_id = try_id

def _find_function_end(lines, i):
    function_try_ids = [[]]
    while len(function_try_ids) > 0 and i < len(lines)-1:
        i += 1
        try:
            function_try_ids = _update_function_try_ids(function_try_ids, lines[i])
        except CutByCaughtException as error:
            raise FunctionCut('caught exception', i, error.try_id)
    if len(function_try_ids) != 0:
        raise FunctionCut('execution ended', len(lines) - 1)
    return i

def _get_function_change_lines(lines, start, end):
    function_change_lines = lines[start+1:end+1]
    end_attributes = function_change_lines[-1][0]
    if end_attributes['type'] == 'function_end':
        return function_change_lines[:-1]
    return function_change_lines

def _regular_executed_function(lines, i):
    end_i = _find_function_end(lines, i)
    change_lines = _get_function_change_lines(lines, i, end_i)
    change_objects = change_objects_from_lines(change_lines)
    return end_i, change_objects

def _error_not_in_loop(change_objects):
    if not change_objects:
        return True
    return type(change_objects[-1]) is not Loop

def _non_ending_executed_function(lines, i, end_i, try_id):
    change_lines = lines[i+1:end_i+1]
    change_objects = change_objects_from_lines(change_lines)
    if _error_not_in_loop(change_objects):
        change_objects.append(Error(try_id))
    return change_objects

def _executed_function_from_lines(lines, i, name, file_path, line_number):
    try:
        end_i, change_objects = _regular_executed_function(lines, i)
    except FunctionCut as error:
        end_i = error.end_i
        change_objects = _non_ending_executed_function(lines, i, end_i, error.try_id)
    return end_i + 1, ExecutedFunction(name, file_path, line_number, change_objects)

def _no_loop_break_found(last_iteration_end):
    return last_iteration_end == -1

def _no_ending_loop_break(last_iteration_end, lines_end):
    return last_iteration_end != lines_end

def _add_iteration(iterations, lines, last_end, new_end):
    iteration_lines = lines[ last_end + 1 : new_end ]
    iterations.append(iteration_lines)
    return iterations

def _iterations_error_cases(iterations, lines, last_end, i):
    if _no_loop_break_found(last_end):
        iterations.append(lines)
    elif _no_ending_loop_break(last_end, i):
        iterations.append(lines[ last_end + 1: ])
    return iterations

def _lines_for_each_iteration(lines, loop_id):
    iterations = []
    last_iteration_end, i = [-1, -1]
    function_try_ids = [[]]
    in_same_loop = [True]
    for i, line in enumerate(lines):
        props, _ = line
        function_try_ids, in_same_loop = _loop_update_func_try_ids(function_try_ids, in_same_loop, lines, i)
        if in_same_loop:
            in_same_loop[-1] = _update_in_same_loop_status(in_same_loop[-1], props, loop_id)
        if props['type'] == 'loop_break' and props['id'] == loop_id and in_same_loop == [True]:
            iterations = _add_iteration(iterations, lines, last_iteration_end, i)
            last_iteration_end = i
    iterations = _iterations_error_cases(iterations, lines, last_iteration_end, i)
    return iterations

def _iterations_from_lines(lines, loop_id):
    iteration_lines = _lines_for_each_iteration(lines, loop_id)
    iterations = []
    for lines in iteration_lines:
        iterations.append(
            change_objects_from_lines(lines)
        )
    return iterations

class NoLoopEnd(Exception):
    def __init__(self, message, end_i, try_id=None):
        super(NoLoopEnd, self).__init__(message)
        self.end_i = end_i
        self.try_id = try_id

def _update_loop_depth(props, loop_id):
    if _is_loop_start(props, loop_id):
        return 1
    elif _is_loop_end(props, loop_id):
        return -1
    return 0

def _is_loop_start(props, loop_id):
    return props['type'] == 'loop_start' and props['id'] == loop_id

def _is_loop_end(props, loop_id):
    return props['type'] == 'loop_end' and props['id'] == loop_id

def _update_in_same_loop_status(in_same_loop_status, props, loop_id):
    if _is_loop_start(props, loop_id):
        return True
    elif _is_loop_end(props, loop_id):
        return False
    return in_same_loop_status

def _is_return(props):
    return props['type'] == 'variable' and props['label'] == 'return'

def _loop_update_func_try_ids(try_ids, in_same_loop, lines, i):
    try:
        return _update_function_try_ids(try_ids, lines[i], in_same_loop=in_same_loop)
    except CutByCaughtException as error:
        raise NoLoopEnd('caught exception', i, error.try_id)

def _loops_function_ended(try_ids, lines, i):
    if len(try_ids) == 0:
        if _is_return(lines[i][0]):
            return True
        raise RuntimeError('function ended without the loop ending beforehand')
    return False

def _find_loop_end(loop_id, lines, start_i):
    function_try_ids = [[]]
    in_same_loop = [True]
    for i in range(start_i+1, len(lines)):
        function_try_ids, in_same_loop = _loop_update_func_try_ids(function_try_ids, in_same_loop, lines, i)
        if _loops_function_ended(function_try_ids, lines, i):
            return i + 1
        in_same_loop[-1] = _update_in_same_loop_status(in_same_loop[-1], lines[i][0], loop_id)
        if in_same_loop == [False]:
            return i
        if not in_same_loop:
            raise RuntimeError('Left loop context')
    raise NoLoopEnd('loop did not end', len(lines))

def _loop_changes_and_end(lines, i, loop_id, line_number):
    try:
        end_i = _find_loop_end(loop_id, lines, i)
        iterations = _iterations_from_lines(lines[i+1:end_i], loop_id)
    except NoLoopEnd as error:
        end_i = error.end_i
        iterations = _iterations_from_lines(lines[i+1:end_i], loop_id)
        iterations[-1].append(Error(error.try_id))
    return end_i, iterations

def _loop_from_lines(lines, i, loop_id, line_number):
    end_i, iterations = _loop_changes_and_end(lines, i, loop_id, line_number)
    if iterations != [[]]:
        return end_i + 1, Loop(loop_id, line_number, iterations)
    return end_i + 1, None



def _change_object_from_lines(lines, i):
    props, values = lines[i]
    if props['type'] == 'function_call':
        return _executed_function_from_lines(
            lines, i,
            props['name'], props['file_path'], props['line_number']
        )
    elif props['type'] == 'loop_start':
        return _loop_from_lines(lines, i, props['id'], props['line_number'])
    else:
        return i + 1, _basic_change_object(props, values)


def change_objects_from_lines(lines):
    change_objects = []
    i = 0
    while i < len(lines):
        i, change_value = _change_object_from_lines(lines, i)
        if change_value:
            change_objects.append(change_value)
    return change_objects


def get_executed_functions(parsed_lines):
    '''
    Return a list of ExecutedFunctions given the output string.

    params:
        change_values: list of parsed change lines, [
            [{"is_arg": true, "type": "variable", "label": "s"}, "AAAA"],
            [{"type": "variable", "label": "deletion_count"}, "0"],
            [{"type": "if", "id": 5, "conditions": [{"label": "if (char == last_char):"}, {"label": "else:"}]}, "False", "True"],
            '_loop_break_function_name_loop_1',
            [{"type": "variable", "label": "last_char"}, "A"],
            [{"type": "variable", "label": "char"}, "A"]
        ]
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
    nested_change_blocks = change_objects_from_lines(parsed_lines)
    if len(nested_change_blocks) > 1 or type(nested_change_blocks[0]) is not ExecutedFunction:
        raise RuntimeError('Unexpected un-nested change objects format.')
    un_nested_functions = UnNestExecutedFunctions().run(nested_change_blocks[0])
    return un_nested_functions
