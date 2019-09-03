
import logging
import logging.config
import os

from pyux import __LOGGING_CONFIG__
from pyux import __LAUNCH_TIME__


def init_logger(folder: str = './logs',
                filename: str = 'activity',
                run_name: str = 'default',
                time_format: str = "%Y%m%d-%Hh%Mm%Ss",
                config_file = None):
    """Return a logger instance with predefined or custom format.
    
    A different log file is saved at each execution. The logger is formatted
    with a default ``logging.conf`` when ``config_file`` is not provided.
    
    Log file name is of the form ``filename_run_name_time-format``. Default
    values yield, for instance : ``logs/activity_default_20190721-18h34h20s.log``. You can
    cheat with ``time_format`` by specifying a normal word.
    
    To use the logger across submodules, it is advised to instantiate the logger in
    the main script with ``logger = init_logger()``, then instantiate it in the other
    modules with ``logger = logging.getLogger(__name__)``. This will not duplicate
    logging instances, and will display in the logged message the name of the
    module from which the logger was called.
    
    :param folder: default ``'./logs'`` : folder to save log files in, created if does not exist
    :type folder: str
    :param filename: default ``'activity'`` : name of log files (first to appear)
    :type filename: str
    :param run_name: default ``'default'`` : name of run
    :type: run_name: str
    :param time_format: default ``'%Y%m%d-%Hh%Mm%Ss'`` : time format for date
    :type time_format: str
    :param config_file: default ``None`` : path to logging.conf configuration file
    :type config_file: str
    
    :return: A 'root' logger from ``logging`` package

    :Example:

    >>> logger = init_logger(
    >>>     folder = 'logs', filename = 'exemple',
    >>>     run_name = 'daily-run', time_format = "%Y%m%d"
    >>> )
    """
    config_file = __LOGGING_CONFIG__ if config_file is None else config_file
    log_filename = filename + '_' + run_name + '_' + __LAUNCH_TIME__.strftime(time_format)
    log_path = os.path.join(folder, "%s.log" % log_filename)
    
    try:
        logging.config.fileConfig(config_file, defaults = {'logfilename': log_path})
    except FileNotFoundError:
        os.makedirs(folder, exist_ok = True)
        logging.config.fileConfig(config_file, defaults = {'logfilename': log_path})
    return logging.getLogger('root')
