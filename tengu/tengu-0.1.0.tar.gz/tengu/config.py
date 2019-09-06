import os


class FlaskDevelopmentConfig:
    ENV_NAME = 'dev'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class FlaskTestingConfig:
    ENV_NAME = 'test'
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


def get_config_by_env(env):

    envs = [
        FlaskTestingConfig,
        FlaskDevelopmentConfig,
        ]

    envs_dict = {e.ENV_NAME: e for e in envs}

    return envs_dict[env]
