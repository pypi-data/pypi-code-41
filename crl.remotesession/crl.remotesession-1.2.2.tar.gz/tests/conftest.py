# pylint: disable=redefined-outer-name
import abc
from collections import namedtuple
from contextlib import contextmanager
import mock
import six
import pytest
from crl.remotesession.remotesessionbase import (
    RemoteRunner,
    RemoteScript)
from crl.remotesession.remotesession import RemoteSession
from crl.remotesession.exceptions import (
    ExecFailedError,
    RemoteSessionError)
from .execsubprocess import exec_cmd
from .sessionenv import (
    SessionEnvForeground,
    SessionEnvBackground,
    SessionEnvRemoteScript,
    SessionEnvTargetNotSet)
from .atestsessionenv import AtestSessionEnv


__copyright__ = 'Copyright (C) 2019, Nokia'


class RemoteSessionMocks(namedtuple('RemoteSessionMocks',
                                    ['session', 'engine'])):
    pass


class RemoteMocks(namedtuple('RemoteMocks',
                             ['runner', 'script'])):
    pass


@pytest.fixture
def remotesessionmocks(remotesession, mock_engine):
    return RemoteSessionMocks(session=remotesession,
                              engine=mock_engine)


@pytest.fixture(params=[
    'mock_remoterunner',
    'mock_remotescript'])
def mock_engine(request,
                mock_remoterunner,
                mock_remotescript,
                remotesession):

    for name in ['default', 'target', 'other', 'name']:
        if request.param == 'mock_remoterunner':
            remotesession.set_runner_target(None, name=name)
        else:
            remotesession.set_target('host', 'user', 'password', name=name)
    return {'mock_remoterunner': mock_remoterunner,
            'mock_remotescript': mock_remotescript}[request.param]


@pytest.fixture
def remotemocks(mock_remoterunner, mock_remotescript):
    return RemoteMocks(runner=mock_remoterunner,
                       script=mock_remotescript)


@pytest.fixture
def mock_remoterunner():
    m = mock.create_autospec(RemoteRunner)
    m.targets = mock.Mock()
    with mock.patch('crl.remotesession.remotesessionbase.RemoteRunner',
                    return_value=m) as p:
        yield p


@pytest.fixture
def mock_remotescript():
    m = mock.create_autospec(RemoteScript)
    m._engine = mock.Mock()
    with mock.patch('crl.remotesession.remotesessionbase.RemoteScript',
                    return_value=m) as p:
        yield p


@pytest.fixture
def remotesession(  # pylint: disable=unused-argument
        mock_remoterunner,
        mock_remotescript):
    return RemoteSession()


@pytest.fixture
def mock_shutil_rmtree():
    with mock.patch('shutil.rmtree') as p:
        yield p


@pytest.fixture
def mock_tempfile_mkdtemp():
    with mock.patch('tempfile.mkdtemp') as p:
        yield p


class SessionTarget(namedtuple('SessionTarget', ['session', 'targetkwargs'])):
    @property
    def expected_target(self):
        return self.targetkwargs.get('name', 'default')

    @property
    def kwargs_to_exec(self):
        if 'name' in self.targetkwargs:
            return {'target': self.targetkwargs['name']}
        return {}


@pytest.fixture(params=[{}, {'name': 'target'}])
def session_target(mock_engine, remotesession, request):
    mock_engine.return_value.execute_command_in_target.side_effect = exec_cmd
    return SessionTarget(session=remotesession, targetkwargs=request.param)


@six.add_metaclass(abc.ABCMeta)
class SourceFileBase(object):

    def __init__(self):
        self._tmpdir = None

    def set_tmpdir(self, tmpdir):
        self._tmpdir = tmpdir

    @property
    def source(self):
        return 'source'

    @property
    def _source_path(self):
        return self._tmpdir.join(self.source)

    @abc.abstractmethod
    def _create_source(self):
        """Create source file using *_source_path*
        """

    @contextmanager
    def in_source(self):
        self._create_source()
        with self._tmpdir.as_cwd():
            yield self


@pytest.fixture
def sourcefile_fact(tmpdir):
    def fact(cls):
        s = cls()
        s.set_tmpdir(tmpdir)
        return s

    return fact


class EnvDictSource(SourceFileBase):

    def __init__(self):
        super(EnvDictSource, self).__init__()
        self.envdict = None

    def set_envdict(self, envdict):
        self.envdict = envdict

    def _create_source(self):
        with self._source_path.open('w') as f:
            f.write('echo to out\n')
            for n, v in self.envdict.items():
                f.write('export {}={!r}\n'.format(n, v))


@pytest.fixture
def envdictsource_fact(sourcefile_fact):
    def fact(envdict):
        e = sourcefile_fact(EnvDictSource)
        e.set_envdict(envdict)
        assert e.envdict
        return e

    return fact


@pytest.fixture(params=[{'a': '1'}, {'a': '1', 'b': '2'}])
def source_file(request, envdictsource_fact):
    s = envdictsource_fact(request.param)
    with s.in_source():
        yield s


@six.add_metaclass(abc.ABCMeta)
class CorruptedSourceBase(SourceFileBase):

    @abc.abstractproperty
    def expected_exception(self):
        """Return expected exception class.
        """

    @property
    def expected_msg(self):
        return 'expected msg'

    def _create_source(self):
        self._source_path.write('echo {}; exit 1'.format(self.expected_msg))


class CorruptedExecutionFailed(CorruptedSourceBase):
    @property
    def expected_exception(self):
        return ExecFailedError


class CorruptedRemoteSessionError(CorruptedSourceBase):
    @property
    def expected_exception(self):
        return RemoteSessionError


@pytest.fixture(params=[CorruptedExecutionFailed, CorruptedRemoteSessionError])
def corrupted_source(request, sourcefile_fact):
    c = sourcefile_fact(request.param)
    with c.in_source():
        yield c


class RemoteSessionCaller(object):
    def __init__(self, method, args):
        self.method = method
        self.args = args
        self.remotesession = None

    def set_remotesession(self, remotesession):
        self.remotesession = remotesession

    def call_method(self):
        return getattr(self.remotesession, self.method)(*self.args)


@pytest.fixture(params=[
    RemoteSessionCaller('get_target_properties', ['default']),
    RemoteSessionCaller('execute_command_in_target', ['command']),
    RemoteSessionCaller('execute_background_command_in_target', ['command']),
    RemoteSessionCaller('copy_file_between_targets', ['default',
                                                      'source',
                                                      'to_target']),
    RemoteSessionCaller('copy_file_between_targets', ['settarget',
                                                      'source',
                                                      'default']),
    RemoteSessionCaller('copy_file_from_target', ['source']),
    RemoteSessionCaller('copy_file_to_target', ['source']),
    RemoteSessionCaller('copy_directory_to_target', ['source']),
    RemoteSessionCaller('create_directory_in_target', ['path']),
    RemoteSessionCaller('get_source_update_env_dict', ['path'])])
def notsetremotesession(request,
                        remotesession):
    request.param.set_remotesession(remotesession)
    remotesession.set_runner_target(None, name='settarget')
    return request.param


@pytest.fixture(params=[
    RemoteSessionCaller('wait_background_execution', ['exec_id']),
    RemoteSessionCaller('kill_background_execution', ['exec_id'])])
def notsetbackground(request,
                     remotesession):
    request.param.set_remotesession(remotesession)
    return request.param


@pytest.fixture(params=[{}, {'name': 'target'}])
def sessionenv_fact(mock_remoterunner, request):
    def fact(sessionenvcls):
        s = sessionenvcls()
        s.set_mock_remoterunner(mock_remoterunner)
        s.set_targetkwargs(request.param)
        s.initialize()
        return s

    return fact


@pytest.fixture(params=[SessionEnvForeground,
                        SessionEnvBackground,
                        SessionEnvRemoteScript,
                        SessionEnvTargetNotSet])
def sessionenv(sessionenv_fact, request):
    return sessionenv_fact(request.param)


@pytest.fixture(params=[{}, {'name': 'target'}])
def atestsessionenv(envdictsource_fact, request):
    s = AtestSessionEnv()
    s.set_targetkwargs(request.param)
    s.create_envdictsource(envdictsource_fact)
    s.initialize()

    with s.envdictsource.in_source():
        yield s
