import logging
from datetime import datetime


def singleton(cls):
    instances = {}

    def _singleton(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return _singleton


@singleton
class LogEngine(object):
    """日志引擎"""

    # 单例模式
    # __metaclass__ = VtSingleton
    # __instance = None

    # ---------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.logger = logging.getLogger('LogEngine')
        self.formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s')
        self.level = logging.INFO
        self.logger.setLevel(self.level)

        self.consoleHandler = None
        self.fileHandler = None

        # 添加NullHandler防止无handler的错误输出
        null_handler = logging.NullHandler()
        self.logger.addHandler(null_handler)
        # self.add_console_handler()

    # ----------------------------------------------------------------------
    def set_log_level(self, level):
        """设置日志级别"""
        self.logger.setLevel(level)
        self.level = level

        if self.level == logging.DEBUG:
            self.add_console_handler()

        if self.consoleHandler is not None:
            self.consoleHandler.setLevel(level)

        if self.fileHandler is not None:
            self.fileHandler.setLevel(level)

    # ----------------------------------------------------------------------
    def add_console_handler(self):
        """添加终端输出"""
        if self.consoleHandler is None:
            self.consoleHandler = logging.StreamHandler()
            self.consoleHandler.setLevel(self.level)
            self.consoleHandler.setFormatter(self.formatter)
            self.logger.addHandler(self.consoleHandler)

    # ----------------------------------------------------------------------
    def add_file_handler(self, filename=''):
        """添加文件输出"""
        if self.fileHandler is None:
            if filename == '':
                filename = 'vt_' + datetime.now().strftime('%Y%m%d') + '.log'
            self.fileHandler = logging.FileHandler(filename, encoding='UTF-8-sig')
            self.fileHandler.setLevel(self.level)
            self.fileHandler.setFormatter(self.formatter)
            self.logger.addHandler(self.fileHandler)

    # ----------------------------------------------------------------------
    def debug(self, msg):
        """开发时用"""
        self.logger.debug(msg)

    # ----------------------------------------------------------------------
    def info(self, msg):
        """正常输出"""
        self.logger.info(msg)

    # ----------------------------------------------------------------------
    def warning(self, msg):
        """警告信息"""
        self.logger.warning(msg)

    # ----------------------------------------------------------------------
    def error(self, msg):
        """报错输出"""
        self.logger.error(msg)

    # ----------------------------------------------------------------------
    def exception(self, msg):
        """报错输出+记录异常信息"""
        self.logger.exception(msg)

    # ----------------------------------------------------------------------
    def critical(self, msg):
        """影响程序运行的严重错误"""
        self.logger.critical(msg)
