# coding=utf-8
from ibm_ai_openscale_cli.api_environment import ApiEnvironment
import logging
import tempfile
import sys

name = 'ibm-ai-openscale-cli'
logging_temp_file = tempfile.NamedTemporaryFile(suffix='{0}.log'.format(name), delete=False)

sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(logging.Formatter('%(message)s'))
sh.setLevel(logging.INFO)

# create file handler which logs even debug messages
fh = logging.FileHandler(logging_temp_file.name)
fh.setFormatter(logging.Formatter('%(asctime)-15s %(name)-12s %(levelname)s - %(message)s'))
fh.setLevel(logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

if ApiEnvironment().is_cli_logging_from_api_enabled():
    logger.setLevel(logging.INFO)
    sh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

if not logger.handlers:
    logger.addHandler(fh)
    logger.addHandler(sh)

# Disable AIOS warnings
logging.getLogger('handle_response').setLevel(logging.WARNING)
logging.getLogger('ibm_ai_openscale.utils.client_errors').setLevel(logging.WARNING)

