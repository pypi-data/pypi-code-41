import logging
import os
from pathlib import Path

import yaml


class LogSetting:
    PIPELINE_YML_PATH = str(Path('config/pipeline.yml'))
    TASK_NAME_PATH = 'task_name.ini'
    _log_setting = None

    def load(self):
        if LogSetting._log_setting is None:
            LogSetting._log_setting = self._load_log_yml()
        return LogSetting._log_setting

    def _load_log_yml(self):
        if os.path.exists(self.PIPELINE_YML_PATH):
            with open(self.PIPELINE_YML_PATH, 'r') as stream:
                pipeline_yml_data = yaml.safe_load(stream)
        else:
            pipeline_yml_data = {}

        if os.path.exists(self.TASK_NAME_PATH):
            with open(self.TASK_NAME_PATH, 'r') as stream:
                task_name = stream.read()
        else:
            task_name = ''

        ret = {'task_name': task_name}
        if pipeline_yml_data.get('task_log_format') is None:
            ret['task_log_format'] = "[%(asctime)s] %(levelname)s - %(message)s"
        else:
            ret['task_log_format'] = '"' + pipeline_yml_data['task_log_format'] + '"'

        if pipeline_yml_data.get('task_log_level') is None:
            ret['task_log_level'] = logging.DEBUG
        else:
            ret['task_log_level'] = pipeline_yml_data['task_log_level']

        if pipeline_yml_data.get('sql_log_format') is None:
            ret['sql_log_format'] = "[%(asctime)s] %(levelname)s - %(message)s"
        else:
            ret['sql_log_format'] = '"' + pipeline_yml_data['task_log_format'] + '"'

        if pipeline_yml_data.get('sql_log_level') is None:
            ret['sql_log_level'] = logging.WARN
        else:
            ret['sql_log_level'] = pipeline_yml_data['sql_log_level']

        return ret
