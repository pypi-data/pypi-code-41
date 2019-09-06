import os
import argparse
import textwrap
from ._version import get_version
from .robotdocsconfs import (
    FileRobotdocsconf,
    CumulativeRobotdocsconf)


__copyright__ = 'Copyright (C) 2019, Nokia'


CLI = 'crl_doc_generate_rst'


class DocArgParser():

    _conffile = 'robotdocsconf.py'

    def __init__(self):
        self._parser = get_argparser()
        self._args = None
        self._robotdocsconfs_dict = {}
        self._parse()

    @property
    def args(self):
        return self._args

    def _parse(self):
        self._args, _ = self._parser.parse_known_args()
        self._update_docspec()
        self._setup_robotdocsconfs()
        self._update_resource()

    def _update_docspec(self):
        if self._args.docspec is None:
            self._args.docspec = ['all']

    def _setup_robotdocsconfs(self):
        for r in self._robotdocsconfs_gen():
            if r.section not in self._robotdocsconfs_dict:
                self._robotdocsconfs_dict[r.section] = CumulativeRobotdocsconf(r.section)
            self._robotdocsconfs_dict[r.section].update(r)

        self._args.robotdocsconfs = [r for _, r in self._robotdocsconfs_dict.items()]

    def _update_resource(self):
        if self._args.resource is None:
            self._args.resource = []

    def _robotdocsconfs_gen(self):
        for r in self._libpaths_gen():
            for d, _, f in os.walk(r):
                if self._conffile in f:
                    yield FileRobotdocsconf(os.path.join(d, self._conffile))

    def _libpaths_gen(self):
        if self._args.libpath:
            for l in self.args.libpath:
                yield l


DESCRIPTION = textwrap.dedent('''\
    Documentation generator script. Documents are generated from:
     - Robot Framework built-in libraries,
     - installed Common Robot Library packages,

    The ReStructuredText documentation source is generated to the following relative directories:
     - sphinxdocs/builtin : Robot Framework built-in keywords.
     - sphinxdocs/crl : Common Robot Libraries Robot Framework keyword documentation.
    ''')


DOCSPEC_HELP = textwrap.dedent('''\
    Documentation type filter
    usage example:
      crl_doc_generate_rst -d builtin -d crl
    without giving this option all types will be generated
    ''')


LIBPATH_HELP = textwrap.dedent('''\
    Root paths to the directories from where robotdocsconf.py files are are
    searched. Each configuration file must contain the following attributes:
     - section: section name for which index file and ReST files are generated
     - robotdocs: robotdocs dictionary

    Example of robotdocsconf.py file content:

        section = 'Example Libraries'

        robotdocs = {
            'examplelib.LocalExample1':
                {'docformat': 'rest',
                 'synopsis': 'Local example1 library'},
            'examplelib.LocalExample2':
                {'docformat': 'rest',
                 'synopsis': 'Local example2 library'}}
    ''')


RESOURCE_HELP = textwrap.dedent('''\
    Root paths to Robot Framework resource and test case files ending with .robot
    ''')


def get_argparser():
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '--version', action='version', version='{cli} {version}'.format(
            cli=CLI,
            version=get_version()))
    parser.add_argument(
        '-d', '--docspec', dest='docspec', action='append',
        help=DOCSPEC_HELP, choices=['crl', 'builtin', 'api', 'all'])
    parser.add_argument(
        '-l', dest='libpath', action='append',
        help=LIBPATH_HELP)
    parser.add_argument(
        '-r', dest='resource', action='append',
        help=RESOURCE_HELP)

    return parser
