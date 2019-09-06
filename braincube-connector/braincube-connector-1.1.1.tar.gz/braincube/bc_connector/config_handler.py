import json
import logging
import os
from os.path import join

from braincube.bc_connector.certificate_gen import gen_ssl_cert_if_none

logger = logging.getLogger(__name__)

config_dir = os.path.expanduser('~/.braincube')
file_path = join(config_dir, "config.json")
config_template = {'client_secret': '', 'client_id': '', 'domain': 'mybraincube.com'}

config = None


def config_setup_ok():
    """
    Generate a self-signed ssl certificate if none are found in ~./braincube
    Read the local config file and check if it's filled
    If no file is found one is created
    If the file is not filled a console message is displayed
    """
    if os.path.isfile(file_path):
        gen_ssl_cert_if_none(config_dir)
        read_local_config()
        return is_config_filled(config)

    else:
        logger.warn("No configuration file found. ")
        init_config_file()


def init_config_file():
    logger.info("Configuration file created in: " + file_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as outfile:
        json.dump(config_template, outfile)
    logger.warn("Current domain: '" + config_template["domain"] + "' change it to add your sub-domain if you have one")
    logger.warn("Please fill the client_id and the client_secret and try again")


def is_config_filled(config):
    if config is None or not config['client_id'] or not config['client_secret']:
        logger.info("client_id and/or client_secret are empty, please fill them in: " + file_path)
        return False
    else:
        logger.info("config filled with: %s", config)
        return True


def read_local_config():
    logger.info("Reading configuration from: " + file_path)
    with open(file_path) as json_data_file:
        global config
        config = json.load(json_data_file)


def get_client_id():
    return config['client_id']


def get_client_secret():
    return config['client_secret']


def get_domain():
    if config is None:
        return ""
    else:
        return config['domain']
