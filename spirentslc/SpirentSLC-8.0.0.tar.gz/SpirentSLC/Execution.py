# ****************       BEGIN-STANDARD-COPYRIGHT      ***************
#
# Copyright (c) 2018, Spirent Communications.
#
# All rights reserved. Proprietary and confidential information of Spirent Communications.
#
#  ***************        END-STANDARD-COPYRIGHT       ***************
"""SLC API that facilitates client code organization"""

import re
import sys
import json

from .exception import SLCError


class Status:
    """A class to represent status of a test case being executed.

    Test status could be in one of the following states:
    Status.PASSED - test case passed
    Status.FAIL - test failed (e.g. because certain assertion criteria was not meet)
    Status.ABORTED - test case was aborted
    Status.CANCELED - test case was canceled
    Status.INDETERMINATE - test result is indeterminate

    Example:
        from SpirentSLC.Execution import Status
        status = Status()
        status.passTestIfNotAlreadyFailed()
        if status.get() == Status.PASSED:
            print "test passed!"
    """

    PASSED = 'PASSED'
    FAILED = 'FAILED'
    ABORTED = 'ABORTED'
    CANCELLED = 'CANCELLED'
    INDETERMINATE = 'INDETERMINATE'

    def __init__(self, state=INDETERMINATE):
        self._state = state

    def pass_test(self, log=None):
        """Pass test whatever current status is"""
        self._state = Status.PASSED
        if log:
            log.info("Test case has passed.")

    def fail_test(self, log=None):
        """Fail test whatever current status is"""
        self._state = Status.FAILED
        if log:
            log.error("Test case has failed.")

    def fail_test_if_passing(self, log=None):
        """
            Fail test if current status is not already FAILED or ABORTED.
            Otherwise status will remain unchanged.
        """
        if self._state != Status.FAILED and self._state != Status.ABORTED:
            self._state = Status.FAILED
            if log:
                log.error("Test case has failed.")

    def pass_test_if_not_already_failed(self, log=None):
        """
            Pass test if current state is either INDETERMINATE or PASSED.
            Otherwise status will remain unchanged.
        """
        if self._state == Status.INDETERMINATE or self._state == Status.PASSED:
            self._state = Status.PASSED
            if log:
                log.info("Test case has passed.")

    def abort_test(self, log=None):
        """Change test status to ABORTED"""
        self._state = Status.ABORTED
        if log:
            log.error("Test case has aborted.")

    def cancel_test(self, log=None):
        """Change test status to CANCELLED"""
        self._state = Status.CANCELLED
        if log:
            log.error("Test case has been cancelled.")

    def get(self):
        """Get current status (could be Status.FAILED, Status.PASSED, etc.)"""
        return self._state


class TestTermination(Exception):
    """Exception indicating test case was terminated abruptly"""
    pass


def _get_json_paths(paths):
    """
    Transform json delete paths string into paths list.

    Arguments:
        paths - string of the form '{"some/path", "other/path", ... }'
    """
    as_json_list = '[' + paths.strip()[1:-1] + ']'
    return json.loads(as_json_list)


def add_json_nodes(target, path_value):
    """
    Extend target by value at the given path.

    Arguments:
        target - json strings
        path_value - string with the same format as in 'json' step of iTest.

    Example:
        target = '{"x": [{"y":42}]}'
        add_json_node(target, '{ "x/[0]/" : {"z":true} }')
        The result will be '{"x": [{"y":42, "z":true}]}'

    See iTest Help for details on 'json' step format.
    """
    target = json.loads(target)
    for path, value in json.loads(path_value).items():
        path = path.strip()
        if path == "/":
            target.update(value)
            return json.dumps(target)
        node, last_key = _locate(target, path)
        if isinstance(node, list):
            if path.endswith("/"):
                node[last_key].update(value)
            elif isinstance(value, list):
                node[last_key:last_key] = value
            else:
                last_key = min(last_key, len(node))
                node[last_key] = value
        elif isinstance(node, dict):
            node.setdefault(last_key, {}).update(value)
    return json.dumps(target)


def set_json_nodes(target, path_value):
    """
    Set value of target at the given path.

    Arguments:
        target - json string
        path_value - string with the same format as in 'json' step of iTest.

    Example:
        target = '{"x": [0, 1, 2]}'
        set_json_node(target, '{ "x/[1]" : {"y":true} }')
        The result will be '{"x": [0, {"y":true}, 2]}'

    See iTest Help for details on 'json' step format.
    """
    target = json.loads(target)
    for path, value in json.loads(path_value).items():
        node, last_key = _locate(target, path)
        node[last_key] = value
    return json.dumps(target)


def delete_json_nodes(target, paths):
    """
    Extend target by value at the given path.

    Arguments:
        target - json string
        paths - string with the same format as in 'json' step of iTest.

    Example:
        target = '{"x": [5, 6, 7]}'
        delete_json_node(target, '{"x/[1]"}')
        The result will be '{"x": [5, 7]}'

    See iTest Help for details on 'json' step format.
    """
    target = json.loads(target)
    for path in _get_json_paths(paths):
        node, last_key = _locate(target, path)
        del node[last_key]
    return json.dumps(target)


def get_json_nodes(target, paths):
    """
    Query json object fields.

    Arguments:
        target - json string from which fields will be extracted
        paths - string with the same format as in 'json' step of iTest.
    """
    target = json.loads(target)
    for path in _get_json_paths(paths):
        path = path.strip()
        keys = list(map(_to_key, path.split("/")))
        value = _find_child(target, keys)
        last_object_key = _find_last_object_key(target, keys)
        return json.dumps({last_object_key: value})


def _find_last_object_key(target, keys):
    node = target
    result = None
    for key in keys:
        if isinstance(node, dict):
            result = key
        node = node[key]
    return result


def _locate(target, path):
    path = path.strip()
    keys = list(map(_to_key, path.split("/")))
    last_key = keys.pop() or keys.pop()
    node = _find_child(target, keys)
    return (node, last_key)


def _to_key(path_element):
    if path_element.startswith("[") and path_element.endswith("]"):
        return int(path_element[1:-1])
    return path_element


def _find_child(node, keys):
    for key in keys:
        node = node[key]
    return node


class Params:
    """Provide API to access test case parameters"""

    def __init__(self, params=None, read_command_line=True):
        self._params = params or dict()
        if read_command_line:
            self._read_command_line_params()

    def __call__(self, path):
        key = path.replace("/", ".")
        return self._params.get(key)

    def _read_command_line_params(self):
        command_line_params = self._parse_command_line_params()
        for key, value in command_line_params.items():
            self._params[key] = value  # override

    def _parse_command_line_params(self):
        result = {}
        remain = list(reversed(sys.argv[1:]))
        while remain:
            name = remain.pop()
            if name.startswith("-") and remain:
                name = name[1:]
                value = self._parse_value(remain.pop())
                if name in result and type(result[name]) is list:
                    result[name].append(value)
                elif name in result:
                    result[name] = [result[name], value]
                else:
                    result[name] = value
        return result

    def _parse_value(self, command_line_value):
        return command_line_value


def gget(name, default_value=None):
    return globals().get(name, default_value)


def gset(name, value):
    globals()[name] = value


def info(*args, **kwargs):
    raise SLCError('Info commands not implemented')


def _action_type(action):
    if action.action != "action":
        return None
    return action.description.split(' ')[0]


_EXECUTION_ISSUE_PATTERN = re.compile(r'DeclareExecutionIssue\s(\w+)\s*:(.*)')


def _handle_execution_issue(action, status, logger):
    matched = _EXECUTION_ISSUE_PATTERN.match(action.description)
    if not matched:
        # unexpected execution issue format
        return
    severity = matched.group(1)
    message = matched.group(2)
    if severity == "OK" or severity == "Information":
        logger.info(message)
    elif severity == "Error":
        logger.error(message)
    elif severity == "Warning":
        logger.warn(message)


def _handle_action(action, status, logger):
    action_type = _action_type(action)
    if action_type == "DeclareExecutionIssue":
        _handle_execution_issue(action, status, logger)
    elif action_type == "FailTest":
        status.fail_test(logger)

    for child_action in action.actions:
        _handle_action(child_action, status, logger)


def handle_step_results(response, status, logger):
    """
    Handle actions affecting test output (exeuction issues) or its status.
    """
    for action in response.message.details.postProcessing:
        _handle_action(action, status, logger)
