# Python Logger
# Requires a log_config.yaml in log folder
# Written by Stefan McShane

import os
import logging.config
import yaml
import pathlib



# Logger manages logging in a uniform way
# Call Logger.setup() before running


# Expects config file to be found in PROJECT_ROOT/install/log_config.yaml
# This can be overwritten by passing LOG_CFG as param on script call


# Logs informational messages
# Use this instead of printing files
def info(msg):
    logging.info(msg)


# Use when 'caveman debugging'
# This will keep track of errors for testing and debugging but will not show up in production code
def debug(msg):
    logging.debug(msg)


# Logs error messages including stacktrace
# Will find "NoneType: None" in log where this is used and no exception was caught
# Best to use in try/except statements
def error(msg, exit_after=False):
    if exit_after:
        new = 'Exited Application. {0}'.format(msg)
        logging.exception(new)
        exit(1)
    logging.exception(msg)


def setup(
    default_path='log_config.yaml',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):

    # Get log config location
    HERE = pathlib.Path(__file__).parent
    path = (HERE / "log_config.yaml")

    # Create log directory if it doesn't exist
    if os.path.exists("log"):
        pass
    else:
        os.mkdir("log")

    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
