import configparser
from upload import __root__
import json
import os
from AuditModule.common.configuration_settings import config
import ast

#Root path
root_path = __root__.path()

# Properties file
CONFIGURATION_FILE = "conf\settings.yaml"

# Config file parser
parser = configparser.RawConfigParser()

parser.read(CONFIGURATION_FILE)

# Log
# LOG_BASE_PATH = parser.get('LOG', 'base_path')
LOG_LEVEL = config["LOG"]['log_level']
LOG_BASEPATH = os.environ.get('LOG_BASEPATH', config["LOG"]['base_path'])
FILE_NAME = LOG_BASEPATH + os.environ.get('FILE_NAME', config["LOG"]['file_name'])
FILE_NAME_JSON = LOG_BASEPATH + os.environ.get('FILE_NAME_JSON',
                                               config["LOG"]['file_name_json'])
LOG_HANDLERS = os.environ.get('LOG_HANDLERS',
                              config["LOG"]['log_level'])

# Adaptors
persistence_adaptor = config["ADAPTOR"]['persistence_adaptor']

# Server
PORT = os.environ.get('SERVICE_PORT', config['SERVER']['port'])