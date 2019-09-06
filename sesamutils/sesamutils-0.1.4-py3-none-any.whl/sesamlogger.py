import logging
import os


def sesam_logger(logger_name, timestamp=False):
    logger = logging.getLogger(logger_name)
    log_level = os.getenv('LOG_LEVEL')
    level = logging.getLevelName(log_level.upper()) if log_level is not None else None
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                                                  if timestamp else '%(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(stdout_handler)
    if not isinstance(level, int):
        logger.warning("Unsupported value or no LOG_LEVEL provided. Hence, setting default log level to 'INFO'")
        level = logging.INFO
    logger.setLevel(level)
    return logger



