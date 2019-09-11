
from ._string_tools import (
    _remove_prefix,
    _remove_suffix
)
from ._constants import BREAK_KEY


def _remove_double_break(output_string, break_key):
    double_break = '\n{0}\n{0}\n'.format(break_key)
    single_break = '\n{0}\n'.format(break_key)
    while double_break in output_string:
        output_string = output_string.replace(double_break, single_break)
    return output_string


def _break_string(a_string, breaker):
    a_string = a_string.strip()
    a_string = '\n' + a_string
    while '\n{0}\n{0}\n'.format(breaker) in a_string:
        a_string = _remove_double_break(a_string, breaker)
    a_string = _remove_prefix(a_string, '\n' + breaker + '\n')
    a_string = _remove_prefix(a_string, '\n')
    a_string = _remove_suffix(a_string, '\n' + breaker)
    a_string = _remove_suffix(a_string, '\n' + breaker)
    block_lines = a_string.split('\n{0}\n'.format(breaker))
    block_lines = list(filter(None, block_lines))
    return block_lines


def get_change_lines(output_string):
    '''
        From a raw test output string get a list of raw change lines.
    '''
    break_key_change_lines = _break_string(output_string, BREAK_KEY)
    change_lines = []
    for lines_str in break_key_change_lines:
        change_lines += lines_str.split('\n')
    return change_lines
