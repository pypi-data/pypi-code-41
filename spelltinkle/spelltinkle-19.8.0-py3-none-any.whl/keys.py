from typing import Dict

keynames = {
    '^a': 'home',
    '^c': 'copy',
    '^d': 'delete',
    '^e': 'end',
    '^f': 'search_forward',
    '^g': 'code_analysis',
    '^h': 'help',
    '^i': 'tab',
    '^k': 'delete_to_end_of_line',
    '^m': 'enter',
    '^n': 'down1',
    '^o': 'open',
    '^p': 'paste',
    '^q': 'quit',
    '^r': 'search_backward',
    '^s': 'write',
    '^u': 'undo',
    '^v': 'view_files',
    '^w': 'mark_word',
    '^x': 'command',
    '^z': 'stop',
    '^ ': 'normalize_space'}

doubles: Dict[str, Dict[str, str]] = {
    '^t': {'^d': 'diff',
           '^r': 'resolve_conflict',
           '^s': 'write_as',
           '^u': 'undo',
           '+': 'upper',
           '-': 'lower'},
    '^b': {'^d': 'rectangle_delete',
           '^p': 'rectangle_insert',
           '<': 'dedent',
           '>': 'indent'},
    '^y': {'^f': 'format',
           '^g': 'jedi',  # goto def
           '^s': 'spell_check',
           '^y': 'complete',  # old complete
           '^u': 'usages',
           '8': 'yapf'}}

again = {'delete_to_end_of_line'}

repeat = {'home', 'end'}

typos = {'imoprt': 'import'}

aliases = {'np': 'import numpy as np',
           'plt': 'import matplotlib.pyplot as plt',
           'path': 'from pathlib import Path',
           'dd': 'from collections import defaultdict',
           'main': "if __name__ == '__main__':",
           'init': 'def __init__(self):'}
