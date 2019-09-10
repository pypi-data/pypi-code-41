import json
from .atestexample_envcreator import AtestExampleEnvCreator
from .sessionenvbase import SessionEnvBase


__copyright__ = 'Copyright (C) 2019, Nokia'


class AtestSessionEnv(SessionEnvBase):
    def __init__(self):
        super(AtestSessionEnv, self).__init__()
        self._envcreator = None
        self.envdictsource = None

    def set_targetkwargs(self, targetkwargs):
        self._targetkwargs = targetkwargs

    def create_envdictsource(self, envdictsource_fact):
        self.envdictsource = envdictsource_fact(self._envdict)

    def exec_and_verify(self):
        tdict = self._get_dict_from_target(self.target)
        edict = self._get_dict_from_target(self.envtarget)
        diff_dict = dict(set(edict.items()) - set(tdict.items()))
        assert diff_dict == self.update_env_dict

    def _get_dict_from_target(self, target):
        result = self.remotesession.execute_command_in_target(
            self._env_cmd,
            target=target)
        return json.loads(result.stdout)

    @property
    def _env_cmd(self):
        return "python -c 'import os, json; print(json.dumps(os.environ.copy()))'"

    @property
    def _envdict(self):
        return {'example': 'example-value'}

    def initialize(self):
        self._envcreator = AtestExampleEnvCreator(
            source=self.envdictsource.source,
            remotesession=self.remotesession)
        self.remotesession.set_envcreator(self._envcreator)
        self.remotesession.set_runner_target(self.shelldicts, **self._targetkwargs)

    @property
    def update_env_dict(self):
        d = self._envdict.copy()
        d.update(self._envcreator.get_update_dict(self.envname))
        return d

    @property
    def shelldicts(self):
        return [{'shellname': 'BashShell'}]
