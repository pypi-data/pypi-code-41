"""
PyMBS is a Python library for use in modeling Mortgage-Backed Securities.

Copyright (C) 2019  Brian Farrell

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact: brian.farrell@me.com

The log module reads-in the pymbs_logging.json file that comes with the
distribution and sets up logging for PyMBS. This default file should suffice
for most installations, but the user *is* able to cutomize logging through
the use of environment variables.

If you would like to specify your own logging config file, in JSON format,
you can specify the location of that custom config file with the
``PYMBS_LOG_CONFIG`` environment variable.

By default, the log level is set to ``INFO``. If you would like to change the
level, you may set it using the ``PYMBS_LOG_LEVEL`` environment variable.

.. include:: ../source/log_file.rst

"""

import json
import logging
import logging.config
from pathlib import Path
import os
import sys

from pymbs.enums import ExitCode

platform = sys.platform

PYMBS_BASE_PATH = Path(__file__).parent

log_dir = 'pymbs'
log_file = 'pymbs.log'
rel_log_path = Path(log_dir, log_file)
user_home_dir = Path.home()
log_dir_mode = 0o774

if platform == 'darwin':
    pymbs_log_dir = Path(user_home_dir, '.local', 'log', log_dir)
elif platform == 'linux':
    pymbs_log_dir = Path(user_home_dir, '.local', 'log', log_dir)
elif platform == 'win32':
    pymbs_log_dir = Path(user_home_dir, 'AppData', 'Local', log_dir)

if not pymbs_log_dir.exists():
    pymbs_log_dir.mkdir(mode=log_dir_mode, parents=True)

PYMBS_LOG_FILE = Path(pymbs_log_dir, log_file)

if not PYMBS_LOG_FILE.exists():
    PYMBS_LOG_FILE.touch()

PYMBS_LOG_CONFIG = Path(PYMBS_BASE_PATH, 'config', 'pymbs_logging.json')

PYMBS_LOG_LEVEL = 'INFO'


def _get_logging_config(env_log_level='PYMBS_LOG_LEVEL',
                        env_log_config='PYMBS_LOG_CONFIG',
                        env_log_file='PYMBS_LOG_FILE'):
    """Setup logging configuration."""
    value = os.getenv(env_log_config)
    if value:
        log_config_path = value
    else:
        log_config_path = PYMBS_LOG_CONFIG

    try:
        with open(log_config_path, 'rt') as f:
            logging_config = json.load(f)
    except OSError:
        print(f"Failed to open PyMBS logging configuration file at "
              f"{log_config_path}\nExiting...\n\n")
        sys.exit(ExitCode.EX_NOINPUT)

    value = os.getenv(env_log_file)
    if value:
        pymbs_log_file = value
    else:
        pymbs_log_file = PYMBS_LOG_FILE
    logging_config['handlers']['default_handler']['filename'] = pymbs_log_file

    value = os.getenv(env_log_level)
    if value:
        pymbs_log_level = value
    else:
        pymbs_log_level = PYMBS_LOG_LEVEL
    logging_config['loggers']['pymbs']['level'] = pymbs_log_level

    return logging_config


logging.config.dictConfig(_get_logging_config())


def get_logger(logger_name):
    """Return a logger instance named ``logger_name``
    """
    logger = logging.getLogger(logger_name)

    return logger
