from .robotdoc import ActualRobotdocsconf

__copyright__ = 'Copyright (C) 2019, Nokia'


class CliVerifier():

    def __init__(self):
        self._script_runner = None
        self._docspec = None
        self._mock_crldocbuilder = None
        self._robotdoc = None
        self._resource = None

    def set_script_runner(self, script_runner):
        self._script_runner = script_runner

    def set_docspec(self, docspec):
        self._docspec = docspec

    def set_mock_crldocbuilder(self, mock_crldocbuilder):
        self._mock_crldocbuilder = mock_crldocbuilder

    def set_robotdoc(self, robotdoc):
        self._robotdoc = robotdoc

    def set_resource(self, resource):
        self._resource = resource

    def verify(self):
        self._verify_valid()
        self._verify_invalid()

    def _verify_valid(self):
        ret = self._run(*self._args)
        assert ret.success, (ret.stdout, ret.stderr)
        assert self._actual_docspec == self._expected_docspec, (
            'Expected {expected}, actual {actual}'.format(
                expected=self._expected_docspec,
                actual=self._actual_docspec))
        self._assert_robotdocsconfs()
        assert self._actual_resource == self._resource, (
            'Expected {expected}, actual {actual}'.format(
                expected=self._resource,
                actual=self._actual_resource))

    def _assert_robotdocsconfs(self):
        assert self._actual_robotdocsconfs == self._robotdoc.expected_robotdocsconfs, (
            'Expected {expected}, actual {actual}'.format(
                expected=self._robotdoc.expected_robotdocsconfs,
                actual=self._actual_robotdocsconfs))

    def _verify_invalid(self):
        ret = self._run('-d', 'invalid', *self._args)
        assert not ret.success
        assert (
            "invalid choice: 'invalid' "
            "(choose from 'crl', 'builtin', 'api', 'all')") in ret.stderr, ret.stderr

    def _run(self, *args):
        return self._script_runner.run('crl_doc_generate_rst', *args)

    @property
    def _args(self):
        return ([a for d in self._docspec for a in ['-d', d]] +
                [a for l in self._robotdoc.rootpath for a in ['-l', l]] +
                [a for r in self._resource for a in ['-r', r]])

    @property
    def _actual_docspec(self):
        return set(self._actual_arg.docspec)

    @property
    def _actual_robotdocsconfs(self):
        return {ActualRobotdocsconf(name=r.metadata.get('Name'),
                                    robotdocsconf=r.robotdocsconf)
                for r in self._actual_arg.robotdocsconfs}

    @property
    def _actual_resource(self):
        return self._actual_arg.resource

    @staticmethod
    def _actual_counts(robotdocsconfs):
        for r in robotdocsconfs:
            assert not r.metadata.get('Version')
        return [r.robotdocsconf for r in robotdocsconfs]

    @property
    def _actual_arg(self):
        _, args, _ = self._mock_crldocbuilder.mock_calls[0]
        return args[0]

    @property
    def _expected_docspec(self):
        return self._docspec or set(['all'])
