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
"""

import os
from pathlib import Path
import sys

from IPython.display import display, HTML
from jinja2 import Environment, PackageLoader, select_autoescape
import yaml

from pymbs.enums import ExitCode
from pymbs.exceptions import _no_config_msg
from pymbs.log import get_logger

logger = get_logger(__name__)

# Python Decimal Module
DEFAULT_PRECISION = 18
DEFAULT_EMAX = 12
DEFAULT_EMIN = -10
DEFAULT_ROUND_PRECISION = 10

# Pandas
DEFAULT_MAX_ROWS = 400


class Config(object):
    """The Config object holds all configuration values for PyMBS, except for
    those related to Logging, which are stored in the ``pymbs.log`` module.
    See the documentation for that module in regards to the Logging settings.

    The user is able to customize settings via the ``config.yaml`` file, which
    is located in a subdirectory of the user's HOME directory, and is
    described further in the :ref:`configuration` section of this
    documentation.

    Many of the settings in the config object *may* be specifed in
    environment variables. If a value for a setting is specified simultaneously
    in the ``config.yaml`` file *and* as an environment variable, the
    value from the environment variable will be used.

    As noted below, some of the properties set in the ``config`` object are
    actually attributes of the ``Context`` object in Python's ``Decimal``
    module.

    For more information on the Decimal Context object, see:

    https://docs.python.org/3/library/decimal.html#decimal.Context

    Some of the properties set in the ``config`` object are actually options
    in the ``Pandas`` library.

    For more information, see:

    https://pandas.pydata.org/pandas-docs/stable/user_guide/options.html#available-options
    """
    _platform = sys.platform
    _config_dir = 'pymbs'
    _config_file = 'config.yaml'
    _rel_config_path = Path(_config_dir, _config_file)
    _user_home_dir = Path.home()
    _config_file_mode = 0o774
    _help_url = 'https://brianfarrell.gitlab.io/pymbs/configuration.html'

    if _platform != 'win32':
        _user_app_config_dir = Path(_user_home_dir, '.config')
    else:
        _user_app_config_dir = Path(_user_home_dir, 'AppData', 'Local')

    _pymbs_config_path = Path(
        _user_app_config_dir, _rel_config_path
    )

    _jinja_env = Environment(
        loader=PackageLoader('pymbs', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    _ipython_active = False

    def __init__(self):
        Config._detect_ipython()
        _config = Config._load_config()

        # PyMBS Config
        self._project_dir = None
        self._terms_sheet = None
        self._model = {}
        self._cache = {}

        # Pandas Config
        self._precision = None
        self._emax = None
        self._emin = None
        self._round_precision = None
        self._max_rows = None

        self._configure(_config)

    ########################
    ##### PyMBS Config #####
    ########################

    @property
    def project_dir(self):
        """The project_dir *must* be set, as it can not be known or
        discovered in advance.

        The project directory is a dicrecotry in the file system that contains
        one subdirectory for each deal modeled with PyMBS. By convention,
        each subdirectory is named using the name of the deal being modeled.
        For more information about the directory structure, see the
        :ref:`setup` section of this documentation.

        This may set in the ``config.yaml`` file, or via the
        ``PYMBS_PROJECT_DIR`` environment variable.
        """
        return self._project_dir

    @project_dir.setter
    def project_dir(self, value):
        logger.info(f"Setting project_dir in config: {value}")
        self._project_dir = value

    @property
    def terms_sheet(self):
        """The terms_sheet value should *never* be set directly. This value
        is set by calling the ``api.load_deal(series_name)`` function,
        passing the name of the directory that holds the files for the deal.

        The ``load_deal`` function deserializes the ``series_ts.json`` file
        and converts all ``Float`` values into ``Decimal`` values, using
        Python's Decimal module.

        The Terms Sheet structure may be viewed as a Python dictionary by
        referencing the ``config.terms_sheet`` property.
        """
        return self._terms_sheet

    @terms_sheet.setter
    def terms_sheet(self, value):
        logger.info(
            f"Setting terms_sheet in config: "
            f"Series: {value['meta']['series_no']} | "
            f"TS Version: {value['meta']['ts_version']} | "
            f"Underwriter: {value['meta']['lead_underwriter']}"
        )
        self._terms_sheet = value

    @property
    def model(self):
        """The model value should *never* be set directly. This value
        is set by calling the ``api.load_model(model_json)`` function,
        passing the name of the JSON file that holds the model for the deal.

        The ``load_model`` function deserializes the JSON data into Python
        data types, for use in all subsequent function calls to compute the
        outputs of the model.

        The model structure may be viewed as a Python dictionary by
        referencing the ``config.model`` property.
        """
        return self._model

    @property
    def cache(self):
        """The cache value should *never* be set directly. This Python
        dictionary is referenced and modified by private functions throughout
        the PyMBS code.

        The values in this dictionary change quicky when running the model, so
        viewing it by referencing the ``config.cache`` property may not make
        sense, except in a debugging context.
        """
        return self._cache

    @property
    def round_precision(self):
        """round_precision is the number of decimals to round to, when
        rounding a decimal value. It is *not* part of the specification
        described in the Python Decimal Module, but is a custom value
        created and used by PyMBS.

        This value is used in the custom ``_round_dec()`` function, located
        in the ``pymbs.utils`` module.

        This may set in the ``config.yaml`` file, or via the
        ``PYMBS_ROUND_PRECISION`` environment variable.
        """
        return self._round_precision

    @round_precision.setter
    def round_precision(self, value):
        logger.info(f"Setting round_precision in config: {value}")
        self._round_precision = value

    #################################
    ##### Python Decimal Config #####
    #################################

    @property
    def precision(self):
        """prec[ision] is an attribute of the ``Context`` object in Python's
        Decimal module.

        The precision is an integer in the range [1, MAX_PREC]
        that sets the precision for arithmetic operations in the context.

        This may set in the ``config.yaml`` file, or via the
        ``PYMBS_PRECISION`` environment variable.
        """
        return self._precision

    @precision.setter
    def precision(self, value):
        logger.info(f"Setting precision in config: {value}")
        self._precision = value

    @property
    def emax(self):
        """Emax is an attribute of the ``Context`` object in Python's
        Decimal module. The Emax field is an integer specifying the outer
        limit allowable for the max exponent.

        Emax must be in the range [0, MAX_EMAX].

        This may set in the ``config.yaml`` file, or via the ``PYMBS_EMAX``
        environment variable.
        """
        return self._emax

    @emax.setter
    def emax(self, value):
        logger.info(f"Setting emax in config: {value}")
        self._emax = value

    @property
    def emin(self):
        """Emin is an attribute of the ``Context`` object in Python's
        Decimal module. The Emin field is an integer specifying the outer
        limit allowable for the min exponent.

        Emin must be in the range [MIN_EMIN, 0].

        This may set in the ``config.yaml`` file, or via the ``PYMBS_EMIN``
        environment variable.
        """
        return self._emin

    @emin.setter
    def emin(self, value):
        logger.info(f"Setting emin in config: {value}")
        self._emin = value

    #########################
    ##### Pandas Config #####
    #########################

    @property
    def max_rows(self):
        """This sets the maximum number of rows Pandas should output when
        printing out various output. For example, this value determines
        whether the repr() for a dataframe prints out fully or just a
        truncated or summary repr. ‘None’ value means unlimited.

        The Pandas default is 60.

        The PyMBS default for this value is 400, which was determined by
        rounding up from 360, which is the number of monthly periods in a
        30-year cash flow.

        This may set in the ``config.yaml`` file, or via the ``PYMBS_MAX_ROWS``
        environment variable.
        """
        return self._max_rows

    @max_rows.setter
    def max_rows(self, value):
        logger.info(f"Setting max_rows in config: {value}")
        self._max_rows = value

    def _configure(self, _config):
        _env_project_dir = os.getenv('PYMBS_PROJECT_DIR')

        _env_precision = os.getenv('PYMBS_PRECISION')
        _env_emax = os.getenv('PYMBS_EMAX')
        _env_emin = os.getenv('PYMBS_EMIN')
        _env_round_precision = os.getenv('PYMBS_ROUND_PRECISION')
        _env_max_rows = os.getenv('PYMBS_MAX_ROWS')

        _file_project_dir = None

        _file_precision = None
        _file_emax = None
        _file_emin = None
        _file_round_precision = None
        _file_max_rows = None

        pymbs_config = _config.get('pymbs')
        if pymbs_config:
            _file_project_dir = pymbs_config.get('project directory')

        pandas_config = _config.get('pandas')
        if pandas_config:
            _file_precision = pandas_config.get('precision')
            _file_emax = pandas_config.get('emax')
            _file_emin = pandas_config.get('emin')
            _file_round_precision = pandas_config.get('round precision')
            _file_max_rows = pandas_config.get('max rows')

        if _env_project_dir and _file_project_dir:
            self.project_dir = _env_project_dir
        elif _env_project_dir:
            self.project_dir = _env_project_dir
        elif _file_project_dir:
            self.project_dir = _file_project_dir

        if _env_precision and _file_precision:
            self.precision = _env_precision
        elif _env_precision:
            self.precision = _env_precision
        elif _file_precision:
            self.precision = _file_precision
        else:
            self.precision = DEFAULT_PRECISION

        if _env_emax and _file_emax:
            self.emax = _env_emax
        elif _env_emax:
            self.emax = _env_emax
        elif _file_emax:
            self.emax = _file_emax
        else:
            self.emax = DEFAULT_EMAX

        if _env_emin and _file_emin:
            self.emin = _env_emin
        elif _env_emin:
            self.emin = _env_emin
        elif _file_emin:
            self.emin = _file_emin
        else:
            self.emin = DEFAULT_EMIN

        if _env_round_precision and _file_round_precision:
            self.round_precision = _env_round_precision
        elif _env_round_precision:
            self.round_precision = _env_round_precision
        elif _file_round_precision:
            self.round_precision = _file_round_precision
        else:
            self.round_precision = DEFAULT_ROUND_PRECISION

        if _env_max_rows and _file_max_rows:
            self.max_rows = _env_max_rows
        elif _env_max_rows:
            self.max_rows = _env_max_rows
        elif _file_max_rows:
            self.max_rows = _file_max_rows
        else:
            self.max_rows = DEFAULT_MAX_ROWS

    @classmethod
    def _detect_ipython(cls):
        try:
            cfg = get_ipython().config  # noqa
            cls._ipython_active = True
        except NameError:
            cls._ipython_active = False

    @staticmethod
    def _load_config():
        alt_config_path = os.getenv('PYMBS_CONFIG_PATH')
        if alt_config_path:
            _pymbs_config_path = alt_config_path
        else:
            _pymbs_config_path = Config._pymbs_config_path
        try:
            with open(_pymbs_config_path, 'r') as stream:
                data = yaml.full_load(stream)
        except FileNotFoundError:
            pymbs_config_dir = Path(
                Config._user_app_config_dir, Config._config_dir
            )
            if not pymbs_config_dir.exists():
                pymbs_config_dir.mkdir(
                    mode=Config._config_file_mode, parents=True
                )
            _pymbs_config_path.touch()

            if not Config._ipython_active:
                print(_no_config_msg(_pymbs_config_path, Config._help_url))
                sys.exit(ExitCode.EX_CONFIG)
            else:
                no_config_html = Config._jinja_env.get_template(
                    'new_config.html'
                )
                msg = no_config_html.render(
                    _pymbs_config_path=_pymbs_config_path,
                    _help_url=Config._help_url
                )
                display(HTML(msg))
        else:
            return data


config = Config()
