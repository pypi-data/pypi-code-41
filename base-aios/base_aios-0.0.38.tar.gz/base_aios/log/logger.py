import os
import logging
from logging.handlers import RotatingFileHandler
class InfoFilter(logging.Filter):
    def filter(self, record):
        """only use INFO
        筛选, 只需要 INFO 级别的log
        :param record:
        :return:
        """
        if logging.INFO <= record.levelno < logging.ERROR:
            # 已经是INFO级别了
            # 然后利用父类, 返回 1
            return super().filter(record)
        else:
            return 0

class AiosLogger():

    def __init__(self, log_path='logs'):
        # Formatter
        self.formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(process)d %(thread)d '
            '%(pathname)s %(lineno)s %(message)s')
        self.log_path = log_path
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path, mode=777)

    def get_info_handler(self):
        # FileHandler Info
        info_handler = RotatingFileHandler(filename=os.path.join(self.log_path, 'info.txt'))
        info_handler.setFormatter(self.formatter)
        info_handler.setLevel(logging.INFO)
        info_filter = InfoFilter()
        info_handler.addFilter(info_filter)
        return info_handler
        
    def get_error_handler(self):
        # FileHandler Error
        error_handler = RotatingFileHandler(filename=os.path.join(self.log_path, 'error.txt'))
        error_handler.setFormatter(self.formatter)
        error_handler.setLevel(logging.ERROR)
        return error_handler