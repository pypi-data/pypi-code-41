import tokenize as tk
from yapf.yapflib.yapf_api import FormatCode

BOM_UTF8 = b'\xef\xbb\xbf'


def _new_fake_lines_iterable(string):
    bytes_string = bytes(string, 'utf-8')
    return iter([BOM_UTF8, bytes_string])


def _tokenize(snippet):
    tokens = []
    fake_iter = _new_fake_lines_iterable(snippet)
    for token_object in tk.tokenize(fake_iter.__next__):
        tokens.append(token_object.string)
    return tokens[1:-1]


def replace_py_token(snippet, current, new):
    tokens = _tokenize(snippet)
    for i in range(len(tokens)):
        if tokens[i] == current:
            tokens[i] = new
    formatted_code = FormatCode(' '.join(tokens))[0][:-1]
    return formatted_code
