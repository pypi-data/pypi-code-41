# -*- coding: utf-8 -*-
"""
Provides support for AWS Lambda execution of the board
"""
import os

import awsgi
from ssm_parameter_store import EC2ParameterStore

# This definitely exists, but something about `python setup.py lint`'s execution can't find it
from ebr_board import create_app  # pylint: disable=no-name-in-module


def handler(event, context):
    """
    Provides support for AWS Lambda
    """
    config_name = os.environ.get("config_name", "ebr_board_config")
    vault_config_name = os.environ.get("vault_config_name", "ebr_board_vault_config")
    vault_creds_name = os.environ.get("vault_creds_name", "ebr_board_vault_creds")
    config_format = os.environ.get("config_format", "yaml")

    store = EC2ParameterStore()
    config = store.get_parameters([config_name, vault_config_name, vault_creds_name], decrypt=True)

    app = create_app(
        config=config[config_name],
        vault_config=config[vault_config_name],
        vault_creds=config[vault_creds_name],
        config_format=config_format,
    )
    return awsgi.response(app, event, context)
