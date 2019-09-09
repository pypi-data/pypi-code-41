import os
import logging


class VariablesConfig(object):

    missing_env_vars = list()
    logger = logging.getLogger("VariablesConfig")

    def __init__(self, required_env_vars, optional_env_vars=None):

        for env_var in required_env_vars:
            value = os.getenv(env_var)
            if not value:
                self.missing_env_vars.append(env_var)
            setattr(self, env_var, value)

        if optional_env_vars:
            for env_var in optional_env_vars:
                if isinstance(env_var, tuple):
                    value = os.getenv(env_var[0], env_var[1])
                    key = env_var[0]
                else:
                    value = os.getenv(env_var)
                    key = env_var
                if value:
                    setattr(self, key, value)

    def validate(self):
        if len(self.missing_env_vars) != 0:
            self.logger.error(f"Missing the following required environment variable(s) {self.missing_env_vars}")
            return False
        return True
