import logging
import sys

from podder_task_base.log.log_setting import LogSetting


class SqlalchemyLoggerSetting():
    def __init__(self):
        setting = LogSetting().load()
        log_format = setting["sql_log_format"]
        log_level = setting["sql_log_level"]

        logging.basicConfig()

        sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
        sqlalchemy_logger.propagate = False
        sqlalchemy_logger.setLevel(log_level)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        handler.setFormatter(logging.Formatter(fmt=log_format, datefmt='%Y-%m-%d %H:%M:%S'))
        sqlalchemy_logger.addHandler(handler)
