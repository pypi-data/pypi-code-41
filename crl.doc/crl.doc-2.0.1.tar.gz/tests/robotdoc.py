import abc
import os
import itertools
from contextlib import contextmanager
import six
from crl.doc.robotdocsconfs import RobotdocsconfBase  # pylint: disable=E0401


def parity(count):
    return 'odd' if count % 2 else 'even'


class CountRobotdocsconf(RobotdocsconfBase):
    def __init__(self, count):
        self._count = count

    @property
    def robotdocsconf(self):
        return self._count

    @property
    def _metadata_str(self):
        pass


class Counts():
    def __init__(self, counts):
        self._counts = frozenset(counts)

    def __hash__(self):
        return hash(self._counts)

    def __repr__(self):
        return str(self._counts)

    def __eq__(self, other):
        return self._counts == other.counts

    def __len__(self):
        return len(self._counts)

    @property
    def counts(self):
        return self._counts


@six.add_metaclass(abc.ABCMeta)
class NameRobotdocsconfBase():

    @abc.abstractproperty
    def robotdocsconf(self):
        """Return robotdocsconf dictionary.
        """

    @abc.abstractproperty
    def name(self):
        """Return name of the robotdocsconf (section)
        """

    def __eq__(self, other):
        return (self.robotdocsconf == other.robotdocsconf and
                self.name == other.name)

    def __repr__(self):
        return 'name={name}, robotdocsconf={robotdocsconf}'.format(
            name=self.name,
            robotdocsconf=self.robotdocsconf)

    def __len__(self):
        return len(self.robotdocsconf)

    def __hash__(self):
        return hash((self.name, frozenset([r for r in self.robotdocsconf])))


class ExpectedRobotdocsconf(NameRobotdocsconfBase):

    def __init__(self, counts):
        self._counts = counts

    @property
    def robotdocsconf(self):
        return {'lib{}'.format(c): None for c in self._counts}

    @property
    def name(self):
        return parity(next(iter(self._counts)))


class ActualRobotdocsconf(NameRobotdocsconfBase):
    def __init__(self, name, robotdocsconf):
        self._name = name
        self._robotdocsconf = robotdocsconf

    @property
    def robotdocsconf(self):
        return self._robotdocsconf

    @property
    def name(self):
        return self._name


class RobotDoc():
    def __init__(self, tmpdir, rootpaths):
        self._tmpdir = tmpdir
        self._rootpaths = rootpaths
        self._expected_robotdocsconfs = set()
        self._content_iter = self._content_gen()
        self._count = 0

    @contextmanager
    def ctx(self):
        with self._tmpdir.as_cwd():
            self._create_robotdocsconf_files()
            yield self

    @property
    def rootpath(self):
        return {os.path.join(*r) for r in self._rootpaths}

    @property
    def expected_robotdocsconfs(self):
        return set(self._robotdocsconfs_gen())

    def _robotdocsconfs_gen(self):
        for i in [1, 2]:
            e = ExpectedRobotdocsconf(self._get_every_second(i))
            if e:
                yield e

    def _get_every_second(self, start):
        return range(start, self._count + 1, 2)

    def _create_robotdocsconf_files(self):
        for rootpath in self._rootpaths:
            self._create_to_root(rootpath)

    def _create_to_root(self, rootpath):
        rd = self._mkdir_rootpath(*rootpath)
        for a in self._mkdir_args:
            d = rd.mkdir(*a) if a else rd
            r = d.join('robotdocsconf.py')
            r.write(next(self._content_iter))

    def _mkdir_rootpath(self, *rootpath):
        r = self._tmpdir
        for p in rootpath:
            r = r.mkdir(p)
        return r

    def _content_gen(self):
        for self._count in itertools.count(start=1):  # pragma: no branch
            yield 'section = {parity!r}\nrobotdocs = {docdic}'.format(
                parity=parity(self._count),
                docdic={'lib{}'.format(self._count): None})

    @property
    def _mkdir_args(self):
        return [[], ['child']]
