#!/usr/bin/env python
from __future__ import absolute_import

import os
import sys
import tempfile
import shutil

from glob2 import glob
from .engine import check_files

# git usurbs your bin path for hooks and will always run system python
if 'VIRTUAL_ENV' in os.environ:
    site_packages = glob(
        '%s/lib/*/site-packages' % os.environ['VIRTUAL_ENV'])[0]
    sys.path.insert(0, site_packages)


def run(*popenargs, **kwargs):
    '''Combines `call` and `check_output`. Returns a tuple ``(returncode,
    output, err_output)``.

    '''
    from subprocess import PIPE, Popen
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = Popen(stdout=PIPE, *popenargs, **kwargs)
    output, err = process.communicate()
    retcode = process.poll()
    return (retcode, output, err)


def pre_commit():
    tmpd = tempfile.mkdtemp()
    try:
        gitcmd = [
            'git',
            'checkout-index',
            '--prefix={tmpd}/'.format(tmpd=tmpd),
            '-a'
        ]
        rcode, _, __ = run(gitcmd)
        if rcode != 0:
            raise RuntimeError('Could not run git checkout-index')
        cdir = os.getcwd()
        os.chdir(tmpd)
        try:
            main()
        finally:
            os.chdir(cdir)
    finally:
        shutil.rmtree(tmpd)


def main():
    print('merchise-lint on Python %s' % sys.version)
    files = glob('**/*.py') + glob('**/*.xml') + glob('**/*.js')
    files = filter(lambda x: os.path.exists(x), files)
    sys.exit(check_files(files))
