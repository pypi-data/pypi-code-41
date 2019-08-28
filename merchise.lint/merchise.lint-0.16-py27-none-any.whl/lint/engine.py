# Forked from sentry
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from __future__ import absolute_import

import os
import sys
from subprocess import Popen

os.environ['PYFLAKES_NODOCTEST'] = '1'


def get_files(path):
    results = []
    for root, _, files in os.walk(path):
        for name in files:
            results.append(os.path.join(root, name))
    return results


def get_files_for_list(file_list):
    if file_list is None:
        files_to_check = get_files('.')
    else:
        files_to_check = []
        for path in file_list:
            if os.path.isdir(path):
                files_to_check.extend(get_files(path))
            else:
                files_to_check.append(path)
    return files_to_check


def py_lint(file_list, argv=None):
    from flake8.main import application
    app = application.Application()
    if not argv:
        argv = []
    argv.append('--enable-extensions=avoid-pdb')
    argv.append('--enable-extensions=break-or-continue')
    if sys.version_info < (3, 0):
        argv.append('--enable-extensions=absolute-import')
    argv.extend(f for f in file_list if f.endswith('.py'))
    app.run(argv)
    return app.result_count > 0 or app.catastrophic_failure


def check_tabs(file_list):
    # Don't use `any()` so that all files are checked.
    result = False
    for f in file_list:
        if is_textfile(f) and not ignore(f):
            result = file_has_tabs(f) or result
    return result


def ignore(f):
    return f.endswith('.js')


def file_has_tabs(f):
    with open(f, 'rb') as fh:
        if b'\t' in fh.read():
            print("X111 File {} has tabs".format(f))
            return True
    return False


TEXT_APP_FILES = (
    'application/javascript',
    'application/xml',
    'application/xslt+xml',
)


def is_textfile(f):
    import mimetypes
    type_, _ = mimetypes.guess_type(f, strict=False)
    return type_.startswith('text/') or type_ in TEXT_APP_FILES


def bootstrap_types():
    import mimetypes
    mimetypes.add_type('text/x-less', '.less', False)
    mimetypes.add_type('text/x-coffeescript', '.coffee', False)
    mimetypes.add_type('text/x-sass', '.sass', False)
    mimetypes.add_type('text/x-restructuredtext', '.rst', False)


def check_files(file_list=None):
    print('Running merchise lint...')
    bootstrap_types()
    failed = check_tabs(file_list)
    if failed:
        print('Files with tabs failed')
        return 1
    failed = py_lint(file_list)
    if failed:
        print('Flake8 failed')
        return 1
    return 0


def _has_mark(cdir, marks=('setup.py', '.gitlab-ci.yml')):
    return any(os.path.exists(os.path.join(cdir, mark)) for mark in marks)
