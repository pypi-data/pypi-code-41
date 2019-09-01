import string

def get_tab_length(line):
    if not line:
        return 0
    number_of_spaces = next(
        i for i, j in enumerate(line) if j not in string.whitespace
    )
    return number_of_spaces

def remove_tab(tab_length, lines):
    '''
        Remove tab of `tab_length` from `lines`.
        Be sure to leave comments not removing their tab.
    '''
    new_lines = []
    for line in lines:
        if line.strip().startswith('#'):
            new_lines.append(line)
        else:
            new_lines.append(
                line[tab_length:]
            )
    return new_lines

def add_tab(tab_length, lines):
    tab = ' '*tab_length
    new_lines = []
    for line in lines:
        new_lines.append(
            tab + line
        )
    return new_lines

def get_line_tab(line):
    return ' ' * get_tab_length(line)


def _remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def _remove_suffix(text, prefix):
    if text.endswith(prefix):
        return text[:-len(prefix)]
    return text
