'''
Runs a test and returns the stdout from running it.
'''
import os
import sys
import ast
import subprocess
from yapf.yapflib.yapf_api import FormatCode

from ._tokenize_python import replace_py_token
from ._constants import(
    PRINT_PREFIX
)

RUN_COMMAND_TEMPLATE = '{python_path} -m unittest {folder}.{file}.{test_class}.{method}'


def _run_printing_test(python_path, project_root, test_id):
    folder, filename, test_class, test_method = test_id.split('.')
    run_command = RUN_COMMAND_TEMPLATE.format(
        python_path=python_path,
        folder=folder,
        file=PRINT_PREFIX + filename,
        test_class=test_class,
        method=test_method
    )
    process = subprocess.run(run_command.split(), cwd=project_root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.stdout, process.stderr


def run_test(python_path, project_root, test_id):
    '''
        Runs the print version of a test given a test id.
    '''
    return _run_printing_test(python_path, project_root, test_id)
