"""
Simple config.py file that loads the VaultAnyConfig package to get configuration for the service (optionally using Vault).
"""
# pylint: disable=invalid-name

import urllib
import ssl
import os.path
from copy import deepcopy

from elasticsearch_dsl import connections
from vault_anyconfig.vault_anyconfig import VaultAnyConfig


class VaultConfig:  # pylint: disable=too-many-instance-attributes,too-few-public-methods
    """
    Config object which can connect to a Hashicorp Vault instance
    """

    def __init__(self, config, vault_config, vault_creds, config_format=None, load_certs=False):
        """
        Args:
            config{str} -- [File path to configuration or a string containing the configuration] (default: {'config.yaml'})
            vault_config {str} -- [File path to configuration or a string containing the configuration] (default: {'vault.yaml'})
            vault_creds {str} -- [File path to configuration or a string containing the configuration](default: {'vault.yaml'})
            load_certs {bool} -- Automatically load certificate and key files during configuration (default: {False})
            config_format {str} -- Specifies the parser to use when reading the configuration, only needed if reading a string. See the ac_parser option
            in python-anyconfig for available formats. Common ones are `json` and `yaml`.
        """
        config_client = VaultAnyConfig(vault_config, ac_parser=config_format)
        config_client.auto_auth(vault_creds, ac_parser=config_format)
        if os.path.isfile(config):
            config = config_client.load(config, process_secret_files=load_certs)
        else:
            config = config_client.loads(config, process_secret_files=load_certs, ac_parser=config_format)

        # Elastic Search
        elastic_config = config["elastic"]
        self.connect_elastic(elastic_config)
        self.ES_INDEX = elastic_config["index"]

    @staticmethod
    def connect_elastic(src_config):
        """
        Connects the elasticsearch client
        Args:
        config: configuration dictionary for elasticsearch
        """
        local_src_config = deepcopy(src_config)
        user = urllib.parse.quote_plus(local_src_config["user"])
        password = urllib.parse.quote_plus(local_src_config["pwd"])

        # If the ca_certs is a string value rather than a file path, we should setup  an SSL Context that loads this certificate.
        if not os.path.isfile(local_src_config.get("ca_certs", "")) and local_src_config.get("ca_certs", False):
            ssl_context = ssl.create_default_context()
            ssl_context.load_verify_locations(cadata=local_src_config["ca_certs"])
            local_src_config.update({"ssl_context": ssl_context})
            del local_src_config["ca_certs"]

        del local_src_config["user"]
        del local_src_config["pwd"]

        local_src_config.update({"http_auth": user + ":" + password})
        connections.create_connection(hosts=[local_src_config])
