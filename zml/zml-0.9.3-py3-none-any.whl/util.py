import os
from pprint import pprint
from zml.exceptions import FileNotLoadedException, DocumentNotDefinedException


def load_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            return content
    except Exception:
        raise FileNotLoadedException


def find_file_in_dirs(filename, directories):
    for d in directories:
        abs_path = os.path.join(d, filename)
        if os.path.exists(abs_path):
            return abs_path
    raise DocumentNotDefinedException


def minimise(code):
    # return code.replace('\n', '')
    return code.strip()


def deb(obj):
    pprint(obj.asDict())


def set_base_path(base_path):
    os.chdir(base_path)
