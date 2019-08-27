import unittest
import tempfile
from test.test_support import EnvironmentVarGuard
from baiji.config import Settings
from baiji.exceptions import AWSCredentialsMissing

class FakeConfigFile(object):
    def __init__(self, contents):
        self.tf = tempfile.NamedTemporaryFile()
        self.tf.write(contents)
        self.tf.flush()
        self.path = self.tf.name

class FakeYAMLConfigFile(FakeConfigFile):
    def __init__(self, contents):
        import yaml
        super(FakeYAMLConfigFile, self).__init__(yaml.dump(contents))

class FakeConfConfigFile(FakeConfigFile):
    def __init__(self, contents):
        rendered_contents = ["[default]"] + ["{} = {}".format(k, v) for k, v in contents.items()]
        super(FakeConfConfigFile, self).__init__("\n".join(rendered_contents))


def AWSEnvironmentVarGuard():
    env = EnvironmentVarGuard()
    env.unset('AWS_ACCESS_KEY_ID')
    env.unset('AWS_ACCESS_KEY')
    env.unset('AWS_SECRET_ACCESS_KEY')
    env.unset('AWS_SECRET')
    env.unset('AWS_DEFAULT_REGION')
    env.set('BODYLABS_CREDENTIAL_FILE', '/this_file_does_not_exist')
    env.set('AWS_CONFIG_FILE', '/this_file_does_not_exist')
    env.set('AWS_CREDENTIAL_FILE', '/this_file_does_not_exist')
    return env

class ConfigFileOverride(object):
    def __init__(self):
        self.env = AWSEnvironmentVarGuard()
        self._dot_bodylabs = None
        self._aws_credentials = None
        self._aws_config = None
    def __enter__(self):
        return self.env.__enter__()
    def __exit__(self, exception_type, exception_value, traceback):
        return self.env.__exit__(exception_type, exception_value, traceback)

    @property
    def dot_bodylabs(self):
        return self._dot_bodylabs
    @dot_bodylabs.setter
    def dot_bodylabs(self, fake):
        self._dot_bodylabs = fake
        if hasattr(fake, 'path'):
            self.env.set('BODYLABS_CREDENTIAL_FILE', fake.path)

    @property
    def aws_credentials(self):
        return self._aws_credentials
    @aws_credentials.setter
    def aws_credentials(self, fake):
        self._aws_credentials = fake
        if hasattr(fake, 'path'):
            self.env.set('AWS_CREDENTIAL_FILE', fake.path)

    @property
    def aws_config(self):
        return self._aws_config
    @aws_config.setter
    def aws_config(self, fake):
        self._aws_config = fake
        if hasattr(fake, 'path'):
            self.env.set('AWS_CONFIG_FILE', fake.path)


class TestAWS(unittest.TestCase):

    def test_exception_thrown_if_there_are_no_credential_files(self):
        override = ConfigFileOverride()
        with override:
            with self.assertRaisesRegexp(AWSCredentialsMissing, "Missing AWS configuration file"):
                settings = Settings()
                _ = settings.key

    def test_exception_thrown_if_dot_bodylabs_malformed(self):
        override = ConfigFileOverride()
        override.dot_bodylabs = FakeConfigFile("This is a random text file")
        with override:
            with self.assertRaisesRegexp(AWSCredentialsMissing, "Unable to read AWS configuration file"):
                settings = Settings()
                _ = settings.key

    def test_exception_thrown_if_dot_bodylabs_not_a_dictionary(self):
        override = ConfigFileOverride()
        override.dot_bodylabs = FakeYAMLConfigFile([1, 2, 3])
        with override:
            with self.assertRaisesRegexp(AWSCredentialsMissing, "Unable to read AWS configuration file"):
                settings = Settings()
                _ = settings.key

    def test_exception_thrown_if_no_credentials_found(self):
        override = ConfigFileOverride()
        override.dot_bodylabs = FakeYAMLConfigFile({'NO_ACCESS_KEY': 'abc', 'AWS_SECRET': 'cba'})
        with override:
            with self.assertRaisesRegexp(AWSCredentialsMissing, "Missing AWS credentials"):
                settings = Settings()
                _ = settings.key

    def test_just_a_dot_bodylabs_file(self):
        override = ConfigFileOverride()
        override.dot_bodylabs = FakeYAMLConfigFile({'AWS_ACCESS_KEY': 'abc', 'AWS_SECRET': 'cba'})
        with override:
            settings = Settings()
            self.assertEqual(settings.key, 'abc')
            self.assertEqual(settings.secret, 'cba')

    def test_just_a_aws_credentials_file(self):
        override = ConfigFileOverride()
        override.aws_credentials = FakeConfConfigFile({'aws_access_key_id': 'abc', 'aws_secret_access_key': 'cba'})
        with override:
            settings = Settings()
            self.assertEqual(settings.key, 'abc')
            self.assertEqual(settings.secret, 'cba')

    def test_empty_dot_bodylabs_is_fine(self):
        override = ConfigFileOverride()
        override.dot_bodylabs = FakeConfigFile('')
        override.aws_credentials = FakeConfConfigFile({'aws_access_key_id': 'abc', 'aws_secret_access_key': 'cba'})
        with override:
            settings = Settings()
            self.assertEqual(settings.key, 'abc')
            self.assertEqual(settings.secret, 'cba')

    def test_dot_bodylabs_without_keys_is_fine(self):
        override = ConfigFileOverride()
        override.dot_bodylabs = FakeYAMLConfigFile({'FOO': 'XXX', 'BAR': 'XYZZX'})
        override.aws_credentials = FakeConfConfigFile({'aws_access_key_id': 'abc', 'aws_secret_access_key': 'cba'})
        with override:
            settings = Settings()
            self.assertEqual(settings.key, 'abc')
            self.assertEqual(settings.secret, 'cba')

    def test_dot_bodylabs_overrides_aws_credentials(self):
        override = ConfigFileOverride()
        override.dot_bodylabs = FakeYAMLConfigFile({'AWS_ACCESS_KEY': 'abc', 'AWS_SECRET': 'cba'})
        override.aws_credentials = FakeConfConfigFile({'aws_access_key_id': 'XXX', 'aws_secret_access_key': 'XYZZX'})
        with override:
            settings = Settings()
            self.assertEqual(settings.key, 'abc')
            self.assertEqual(settings.secret, 'cba')

    def test_environment_variables_override_files(self):
        override = ConfigFileOverride()
        override.dot_bodylabs = FakeYAMLConfigFile({'AWS_ACCESS_KEY': 'XXX', 'AWS_SECRET': 'XYZZX'})
        override.env.set('AWS_ACCESS_KEY_ID', 'abc')
        override.env.set('AWS_SECRET_ACCESS_KEY', 'cba')
        with override:
            settings = Settings()
            self.assertEqual(settings.key, 'abc')
            self.assertEqual(settings.secret, 'cba')

    def test_exception_not_thrown_with_environment_variables_set_but_no_config_files(self):
        override = ConfigFileOverride()
        override.env.set('AWS_ACCESS_KEY_ID', 'abc')
        override.env.set('AWS_SECRET_ACCESS_KEY', 'cba')
        with override:
            settings = Settings()
            self.assertEqual(settings.key, 'abc')
            self.assertEqual(settings.secret, 'cba')

    def test_defaults_to_us_east_1_if_config_missing(self):
        override = ConfigFileOverride()
        override.dot_bodylabs = FakeYAMLConfigFile({'AWS_ACCESS_KEY': 'abc', 'AWS_SECRET': 'cba'})
        with override:
            settings = Settings()
            self.assertEqual(settings.region, 'us-east-1')

    def test_defaults_to_us_east_1_if_config_contains_no_region(self):
        override = ConfigFileOverride()
        override.dot_bodylabs = FakeYAMLConfigFile({'AWS_ACCESS_KEY': 'abc', 'AWS_SECRET': 'cba'})
        override.aws_config = FakeConfConfigFile({'not_a_region': 'northpole-santasvillage-1', 'otherstuff': 'just-some-junk'})
        with override:
            settings = Settings()
            self.assertEqual(settings.region, 'us-east-1')

    def test_region_being_pulled_from_config(self):
        override = ConfigFileOverride()
        override.dot_bodylabs = FakeYAMLConfigFile({'AWS_ACCESS_KEY': 'abc', 'AWS_SECRET': 'cba'})
        override.aws_config = FakeConfConfigFile({'region': 'northpole-santasvillage-1', 'otherstuff': 'just-some-junk'})
        with override:
            settings = Settings()
            self.assertEqual(settings.region, 'northpole-santasvillage-1')

    def test_region_being_overriden_by_env_var_when_config_exists(self):
        override = ConfigFileOverride()
        override.dot_bodylabs = FakeYAMLConfigFile({'AWS_ACCESS_KEY': 'abc', 'AWS_SECRET': 'cba'})
        override.aws_config = FakeConfConfigFile({'region': 'northpole-santasvillage-1', 'otherstuff': 'just-some-junk'})
        override.env.set('AWS_DEFAULT_REGION', 'ap-northeast-1')
        with override:
            settings = Settings()
            self.assertEqual(settings.region, 'ap-northeast-1')

    def test_region_being_overriden_by_env_var_when_config_missing(self):
        override = ConfigFileOverride()
        override.dot_bodylabs = FakeYAMLConfigFile({'AWS_ACCESS_KEY': 'abc', 'AWS_SECRET': 'cba'})
        override.env.set('AWS_DEFAULT_REGION', 'ap-northeast-1')
        with override:
            settings = Settings()
            self.assertEqual(settings.region, 'ap-northeast-1')
