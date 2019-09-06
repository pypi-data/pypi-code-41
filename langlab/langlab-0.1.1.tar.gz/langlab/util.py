# -*- coding: utf-8 -*-
"""utility module."""

import os
import shutil
import tempfile

def which(program):
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)
 
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
 
    return None


class tempdir(object):

    def __enter__(self):

        self.path = tempfile.mkdtemp()
        return self

    def __exit__(self, exc_type, exc_value, traceback):

        shutil.rmtree(self.path)


class workdir(object):

    def __init__(self, workdir):
        self._cwd = os.getcwd()
        self.path = workdir

    def __enter__(self):

        os.chdir(self.path)
        return self

    def __exit__(self, exc_type, exc_value, traceback):

        os.chdir(self._cwd)
