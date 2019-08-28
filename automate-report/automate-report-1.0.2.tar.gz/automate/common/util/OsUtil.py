#coding=utf-8
__author__ = 'circlq'

import platform #获取操作系统的信息

def get_os():
    return platform.system().lower()  # window运行

def is_linux():   # # window运行
    if get_os() == "linux":
        return True
    else:
        return False

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(__name__)

    logger.info(get_os())
    logger.info(is_linux())
