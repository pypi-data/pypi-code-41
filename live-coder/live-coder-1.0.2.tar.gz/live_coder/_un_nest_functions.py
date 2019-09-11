
from ._change_classes import (
    ExecutedFunction,
    Loop,
    Error,
    Try,
    Variable,
    Function,
    IfStatement
)

ID_CHARS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
def _number_with_base_equal_to_ID_CHARS_len(num):
    numerals=ID_CHARS
    b=len(ID_CHARS)
    return ((num == 0) and numerals[0]) or (_number_with_base_equal_to_ID_CHARS_len(num // b).lstrip(numerals[0]) + numerals[num % b])

def _new_ref_id(num):
    return _number_with_base_equal_to_ID_CHARS_len(num)


class UnNestExecutedFunctions:

    def __init__(self):
        self.function_count = 0

    def _update_reference_ids(self, function_caller, called_function):
        ref_id = _new_ref_id(self.function_count)
        function_caller.reference_id = ref_id
        called_function.reference_id = ref_id
        self.function_count += 1
        return function_caller, called_function

    def _assign_function_references(self, parent, caller, called):
        caller, called = self._update_reference_ids(caller, called)
        called.parent = parent
        return caller, called

    def _loop(self, executed_function, loop):
        found_functions = []
        for i, changes in enumerate(loop.changes):
            new_changes, new_functions = self._un_nest_changes(executed_function, changes)
            loop.changes[i] = new_changes
            found_functions += new_functions
        return loop, found_functions

    @staticmethod
    def _has_matching_try(changes, try_id):
        for change in changes:
            if type(change) is Try and change.try_id == try_id:
                return True
        return False

    def _find_parent_function_with_try_id(self, parent_function, try_id):
        if self._has_matching_try(parent_function.changes, try_id):
            return parent_function
        if parent_function.parent:
            return self._find_parent_function_with_try_id(parent_function.parent, try_id)
        raise RuntimeError("Couldn't find Try() for caught exception.")

    def _un_nest_changes(self, parent_function, changes):
        found_functions = []
        new_changes = []
        for change in changes:
            if type(change) is ExecutedFunction:
                new_changes[-1], executed_function = self._assign_function_references(
                    parent_function, new_changes[-1], change
                )
                found_functions += self._unnest_executed_function(executed_function)
            else:
                if type(change) is Loop:
                    change, new_functions = self._loop(parent_function, change)
                    found_functions += new_functions
                elif type(change) is Error and change.try_id:
                    func_with_try = self._find_parent_function_with_try_id(parent_function, change.try_id)
                    change.function_call_id = func_with_try.reference_id
                    change.function_call_name = func_with_try.name
                new_changes.append(change)
        return new_changes, found_functions

    def _unnest_executed_function(self, executed_function):
        new_changes, found_functions = self._un_nest_changes(executed_function, executed_function.changes)
        executed_function.changes = new_changes
        return [executed_function] + found_functions

    def run(self, executed_function):
        '''
            Takes an ExecutedFunction with nested functions.
            Returns a list of the nested functions with function call references assigned.
        '''
        executed_function.reference_id = 'start'
        return self._unnest_executed_function(executed_function)

