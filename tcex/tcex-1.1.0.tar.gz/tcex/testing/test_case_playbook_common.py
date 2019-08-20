# -*- coding: utf-8 -*-
"""TcEx Playbook Common module"""
import json
import os
from .test_case import TestCase


class TestCasePlaybookCommon(TestCase):
    """Playbook TestCase Class"""

    _output_variables = None
    redis_client = None
    redis_staging_data = {
        '#App:1234:empty!String': '',
        '#App:1234:null!String': None,
        '#App:1234:non-ascii!String': 'ドメイン.テスト',
    }

    @property
    def default_args(self):
        """Return App default args."""
        args = super(TestCasePlaybookCommon, self).default_args
        args.update(
            {
                'tc_playbook_db_context': self.context,
                'tc_playbook_db_path': os.getenv('TC_PLAYBOOK_DB_PATH', 'localhost'),
                'tc_playbook_db_port': os.getenv('TC_PLAYBOOK_DB_PORT', '6379'),
                'tc_playbook_db_type': os.getenv('TC_PLAYBOOK_DB_TYPE', 'Redis'),
                'tc_playbook_out_variables': '',
            }
        )
        return args

    @property
    def output_variables(self):
        """Return playbook output variables"""
        if self._output_variables is None:
            output_variables = self.install_json.get('playbook', {}).get('outputVariables') or []
            self._output_variables = self.output_variable_creator(output_variables)
        return self._output_variables

    @staticmethod
    def output_variable_creator(output_variables, job_id=9876):
        """Create output variables.

        Args:
            output_variables (dict): A dict of the output variables
            job_id (int): A job id to use in output variable string.
        """
        variables = []
        if output_variables is None:
            output_variables = []

        for p in output_variables:
            # "#App:9876:app.data.count!String"
            variables.append('#App:{}:{}!{}'.format(job_id, p.get('name'), p.get('type')))
        return variables

    def populate_output_variables(self, profile):
        """Generate validation rules from App outputs."""
        profile_filename = os.path.join(self.profiles_dir, '{}.json'.format(profile.get('name')))
        profile_name = profile.get('name')
        with open(profile_filename, 'r+') as fh:
            profile_data = json.load(fh)
            pov = profile_data.get('permutation_output_variables')
            if pov is not None:
                pov = self.output_variable_creator(pov)

            redis_data = self.redis_client.hgetall(self.context)
            outputs = {}
            for variable in self.output_variables:
                if pov is not None and variable not in pov:
                    # variable is not in permutation output variables
                    continue

                data = redis_data.get(variable.encode('utf-8'))

                # validate redis variables
                if data is None:
                    # log warning missing output data
                    self.log.error(
                        '[{}] Missing redis output for variable {}'.format(profile_name, variable)
                    )
                else:
                    data = json.loads(data.decode('utf-8'))

                # validate validation variables
                validation_output = (profile_data.get('outputs') or {}).get(variable)
                if validation_output is None and profile_data.get('outputs') is not None:
                    self.log.error(
                        '[{}] Missing validations rule: {}'.format(profile_name, variable)
                    )
                outputs[variable] = {'expected_output': data, 'op': 'eq'}

            if profile_data.get('outputs') is None:
                # update the profile
                profile_data['outputs'] = outputs

                fh.seek(0)
                fh.write(json.dumps(profile_data, indent=2, sort_keys=True))
                fh.truncate()

    def run(self, args):
        """Implement in Child Class"""
        raise NotImplementedError('Child class must implement this method.')

    def stage_data(self, staged_data):
        """Stage the data in the profile."""
        for key, value in list(staged_data.get('redis', {}).items()):
            self.stager.redis.stage(key, value)
