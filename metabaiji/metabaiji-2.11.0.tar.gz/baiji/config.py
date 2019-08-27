import os
from baiji.exceptions import AWSCredentialsMissing

class ConfigFile(object):
    def __init__(self, default_path, environment_variable):
        self.default_path = default_path
        self.environment_variable = environment_variable

    @property
    def path(self):
        from baiji.util.environ import getenvpath
        # Check the environment here so that we check at the moment of load, not
        # when the file is import; this lets us be testable.
        return os.path.expanduser(getenvpath(self.environment_variable, self.default_path))

    @property
    def exists(self):
        return os.path.isfile(self.path)


class YAMLConfigFile(ConfigFile):
    def load(self):
        from baiji.util import yaml
        data = yaml.load(self.path)
        if data is None:
            return {}
        if not isinstance(data, dict):
            raise AWSCredentialsMissing("Unable to read AWS configuration file: {}".format(self.path))
        return data


class ConfConfigFile(ConfigFile):
    def __init__(self, default_path, environment_variable, keys):
        super(ConfConfigFile, self).__init__(default_path, environment_variable)
        self.keys = keys

    def load(self):
        import ConfigParser
        config = ConfigParser.ConfigParser()
        config.read([self.path])
        data = {}
        for out_key, conf_key in self.keys.items():
            try:
                data[out_key] = config.get('default', conf_key)
            except ConfigParser.NoOptionError:
                pass
        return data


class Settings(object):
    '''
    Amazon AWS credential and settings object

    This loads credentials from the standard aws cli config files in ~/.aws files
    and from the ~/.bodylabs legacy Body Labs internal credentials file. The
    legacy ~/.bodylabs file is a yaml file containing a dict with the keys
    ``AWS_ACCESS_KEY`` and ``AWS_SECRET``.

    If both ~/.aws/credentials and ~/.bodylabs exist, ~/.bodylabs takes precedence.

    We load the key and secret from ~/.aws/credentials and ~/.bodylabs. We load the
    default region from ~/.aws/config. All three files can contain other stuff; the
    rest of it is irrelevant to our needs here.

    The locations of the files can be over ridden by environment variables:
    - ~/.bodylabs by BODYLABS_CREDENTIAL_FILE
    - ~/.aws/credentials by AWS_CREDENTIAL_FILE
    - ~/.aws/config by AWS_CONFIG_FILE

    The values can also be set by environment variables:
    - AWS_ACCESS_KEY_ID or AWS_ACCESS_KEY
    - AWS_SECRET_ACCESS_KEY or AWS_SECRET
    - AWS_DEFAULT_REGION

    If the environment variables are set, they will override any files found.

    The credential object makes these available as ``o.key``, ``o.secret``, and
    ``o.region``.

    Region is optional and defaults to ``us-east-1``.
    '''

    dot_bodylabs = YAMLConfigFile('~/.bodylabs', 'BODYLABS_CREDENTIAL_FILE')
    aws_credentials = ConfConfigFile('~/.aws/credentials', 'AWS_CREDENTIAL_FILE',
                                     keys={'AWS_ACCESS_KEY': 'aws_access_key_id', 'AWS_SECRET': 'aws_secret_access_key'})
    aws_config = ConfConfigFile('~/.aws/config', 'AWS_CONFIG_FILE',
                                keys={'REGION': 'region'})

    def __init__(self):
        self._raw_data = None

    def load(self):
        if self._raw_data is None:
            self._raw_data = self._load()
        return self._raw_data

    def _load(self):
        if not self.aws_credentials.exists and not self.dot_bodylabs.exists:
            raise AWSCredentialsMissing("Missing AWS configuration file: {}".format(self.aws_credentials.path))
        raw_data = {}
        # load ~/.aws/credentials
        if self.aws_credentials.exists:
            raw_data.update(self.aws_credentials.load())
        # load ~/.bodylabs -- If the two files have different keys, `.bodylabs` takes precedence
        if self.dot_bodylabs.exists:
            raw_data.update(self.dot_bodylabs.load())
        # load ~/.aws/config
        if self.aws_config.exists:
            raw_data.update(self.aws_config.load())
        if 'AWS_ACCESS_KEY' not in raw_data or 'AWS_SECRET' not in raw_data:
            raise AWSCredentialsMissing("Missing AWS credentials")
        return raw_data

    def _get(self, key, default=None):
        config = self.load()
        if key not in config and default is None:
            raise AWSCredentialsMissing('AWS configuration is missing {}.'.format(key))
        return config.get(key, default)

    def _try(self, var_list, key, default=None):
        for var in var_list:
            val = os.getenv(var, None)
            if val is not None:
                return val
        try:
            return self._get(key, default)
        except AWSCredentialsMissing:
            if default is not None:
                return default
            else:
                raise

    @property
    def key(self):
        return self._try(['AWS_ACCESS_KEY_ID', 'AWS_ACCESS_KEY'], 'AWS_ACCESS_KEY')

    @property
    def secret(self):
        return self._try(['AWS_SECRET_ACCESS_KEY', 'AWS_SECRET'], 'AWS_SECRET')

    @property
    def region(self):
        return self._try(['AWS_DEFAULT_REGION'], 'REGION', default='us-east-1')

settings = Settings()
credentials = settings # for backwards compatibility

def is_available():
    from baiji.util.reachability import internet_reachable
    try:
        settings.load()
    except AWSCredentialsMissing:
        return False
    return internet_reachable()
