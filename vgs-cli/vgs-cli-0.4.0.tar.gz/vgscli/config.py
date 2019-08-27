import os

import yaml


def load_config(config_path=None):
    config_path = config_path or __get_config_path()
    try:
        with open(config_path, 'r') as stream:
            config = yaml.load(stream)
            # non mandatory fields in config.yaml
            config["auth0_url"] = config.get("auth0_url", "https://vgs-dashboard.auth0.com/oauth/token")
            config["kc_server_url"] = config.get("kc_server_url", "https://auth.verygoodsecurity.com/auth")
            config["kc_realm"] = config.get("kc_realm", "vgs")
            config["kc_oidc_provider_alias"] = config.get("kc_oidc_provider_alias", "oidc")
            return config
    except (yaml.YAMLError, OSError):
        config = {}
        return config


def __get_config_path():
    path = os.path.abspath(os.environ.get('VGS_CONFIG', 'config.yaml'))
    return path
