
def singleton(cls):
    instances = {}
    def getinstance(*args,**kwargs):
        if cls not in instances:
            instances[cls] = cls(*args,**kwargs)
        return instances[cls]
    return getinstance

LogLevel_DEBUG  = 101
LogLevel_INFO   = 102
LogLevel_WARN   = 103
LogLevel_ERROR  = 104
LogLevel_FATAL  = 105

@singleton
class WtLogger:

    __api__ = None

    def __init__(self, api):
        self.__api__ = api

    def debug(self, message, catName = ""):
        if self.__api__  is not None:
            self.__api__.write_log(LogLevel_DEBUG, message, catName)

    def info(self, message, catName = ""):
        if self.__api__  is not None:
            self.__api__.write_log(LogLevel_INFO, message, catName)

    def warn(self, message, catName = ""):
        if self.__api__  is not None:
            self.__api__.write_log(LogLevel_WARN, message, catName)

    def error(self, message, catName = ""):
        if self.__api__  is not None:
            self.__api__.write_log(LogLevel_ERROR, message, catName)

    def fatal(self, message, catName = ""):
        if self.__api__  is not None:
            self.__api__.write_log(LogLevel_FATAL, message, catName)
