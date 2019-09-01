from ._get_change_values import get_change_values
from ._get_executed_functions import get_executed_functions
from ._render_executed_functions import render_executed_functions

def html_for_print_output(print_output):
    '''
    Takes a string print output and returns a formated string of variable changes.

    params:
        Print string, e.g:
            """
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
            """
    returns:
        Variable changes, e.g:
            {
                'src/main.py': {
                    'test': {
                        'starting_line_number': 4,
                        'calls': {
                            'A': `function HTML`,
                            '5': `function HTML`
                        }
                    }
                }
            }
    '''
    values = get_change_values(print_output)
    executed_functions = get_executed_functions(values)
    return render_executed_functions(executed_functions)
