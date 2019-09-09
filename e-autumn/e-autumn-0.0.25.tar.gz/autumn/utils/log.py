import os
import sys
from loguru import logger


def initialize_logger(log_file_path=os.getcwd(), log_file_name=None, file_log_level="INFO", stderr_log_level="DEBUG"):
    """
    Get logging handler

    :param log_file_path: the path of logging file
    :param log_file_name: the filename of logging file
    :param file_log_level: the file logging level 
    :param stderr_log_level: the stderr logging level 
    :returns: loguru.logger
    """
    log_file_name = log_file_name or "app.log"
    logger.remove()
    logger.add("%s/%s" % (log_file_path, log_file_name), backtrace=True, rotation="00:00",
               retention="30 days", compression="zip", enqueue=True, level=file_log_level)
    logger.add(sys.stderr, level=stderr_log_level)
    return logger
