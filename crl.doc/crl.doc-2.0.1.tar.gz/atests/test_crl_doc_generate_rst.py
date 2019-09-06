import logging
import os
import re
import shutil
from contextlib import contextmanager
from collections import namedtuple
# pylint: disable=import-error
import pytest
from virtualenvrunner.runner import Runner
# pylint: enable=import-error


__copyright__ = 'Copyright (C) 2019, Nokia'

THISDIR = os.path.dirname(__file__)
TOXINIDIR = os.path.join(THISDIR, os.pardir)
EXPECTED_CRLDOC = os.path.join(THISDIR, 'expected_crldoc')
EXPECTED_BUILTIN = os.path.join(THISDIR, 'expected_builtin')
THISLOCAL = os.path.join(THISDIR, 'local')
LOGGER = logging.getLogger(__name__)


class DocRunnerBase():

    spec_arg = ''
    requirements = ['configobj',
                    'crl.examplelib==1.1.3',
                    'robotframework==3.1.2']
    expected_relative_dir = ''
    sphinxdocs = 'sphinxdocs'

    def __init__(self, tmpdir):
        self.tmpdir = tmpdir
        self._runner = None
        self._setup_runner()

    @property
    def expected_dir(self):
        return os.path.join(THISDIR, self.expected_relative_dir)

    def _setup_runner(self):
        reqs = self.tmpdir.join('requirements.txt')
        reqs.write('\n'.join(self.requirements))
        reqs_path = os.path.join(reqs.dirname, reqs.basename)
        self._runner = Runner(virtualenv_reqs=reqs_path,
                              virtualenv_dir=os.path.join(self.tmpdir.dirname,
                                                          self.tmpdir.basename,
                                                          '.venv'))

    @contextmanager
    def runner(self):
        with self._runner as r:
            with in_dir(TOXINIDIR):
                r.run('python setup.py install')
            with self.tmpdir.as_cwd():
                yield r

    def run(self):
        self._runner.run('crl_doc_generate_rst{}'.format(self.spec_arg))
        assert_dirs_are_same_modulo_generated(
            self.sphinxdocs, os.path.join(self.expected_dir, self.sphinxdocs))


@contextmanager
def in_dir(dirpath):
    currd = os.getcwd()
    os.chdir(dirpath)
    try:
        yield None
    finally:
        os.chdir(currd)


def assert_dirs_are_same_modulo_generated(adir, bdir):
    abs_a = os.path.abspath(adir)
    abs_b = os.path.abspath(bdir)
    abs_tuple = ("Hint: Debugging is easier when diff -r is applied for the filepaths",
                 abs_a, abs_b)
    assert _path_lines_list(adir) == _path_lines_list(bdir), abs_tuple


def _path_lines_list(d):
    return sorted(list(_path_lines_gen(d)))


def _path_lines_gen(d):
    with in_dir(d):
        for r, _, fs in os.walk(os.path.curdir):
            if r != os.path.join(os.path.curdir, 'crl_api'):
                for f in fs:
                    path = os.path.join(r, f)
                    yield PathLines(
                        path=path,
                        lines=list(generation_time_removed_lines(path)))


def assert_files_are_same_modulo_generated(af, bf):
    assert_generators_are_same(*map(generation_time_removed_lines, [af, bf]))


GENERATED_RE = re.compile('^(:generated: ).+$')


def generation_time_removed_lines(path):
    with open(path) as f:
        lines = f.readlines()
        for l in lines:
            yield re.sub(GENERATED_RE, r'\1', l)


class PathLines(namedtuple('PathLines', ['path', 'lines'])):
    def __lt__(self, other):
        return self.path < other.path


def assert_generators_are_same(agen, bgen):
    assert list(agen) == list(bgen)


class CrlDocRunner(DocRunnerBase):

    spec_arg = ' --docspec crl'
    expected_relative_dir = 'expected_crldoc'


class BuiltInDocRunner(DocRunnerBase):
    spec_arg = ' --docspec builtin'
    expected_relative_dir = 'expected_builtindoc'


class AllDocRunner(DocRunnerBase):
    expected_relative_dir = 'expected_alldoc'


class LocalDocRunner(DocRunnerBase):
    spec_arg = ' -l local -r local/resources --docspec crl'
    expected_relative_dir = 'expected_localdoc'

    def run(self):
        shutil.copytree(THISLOCAL, 'local')
        with in_dir('local'):
            self._runner.run('python setup.py install')

        super(LocalDocRunner, self).run()


@pytest.fixture(params=[CrlDocRunner,
                        BuiltInDocRunner,
                        AllDocRunner,
                        LocalDocRunner])
def docrunner(tmpdir, request):
    r = request.param(tmpdir)
    with r.runner():
        yield r


def test_crl_doc_generate_rst(docrunner):
    docrunner.run()
