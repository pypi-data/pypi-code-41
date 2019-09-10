# -*- coding: utf-8 -*-
# @Date    : 2019-07-03
# @Author  : Kelly (weiqin.wang_c@chinapnr.com)
# @Desc    : contains app and routes
# @Version : 1.0.0
import logging


log_config = {
    "version": 1,
    'disable_existing_loggers': False,  # 是否禁用现有的记录器

    # 日志管理器集合
    'loggers': {
        # 管理器
        'default': {
            'handlers': ['console', 'log'],
            'level': 'DEBUG',
            'propagate': True,  # 是否传递给父记录器
        },
    },

    # 处理器集合
    'handlers': {
        # 输出到控制台
        'console': {
            'level': 'INFO',  # 输出信息的最低级别
            'class': 'logging.StreamHandler',
            'formatter': 'standard',  # 使用standard格式
            'filters': ['require_debug_true', ],  # 仅当 DEBUG = True 该处理器才生效
        },
        # 输出到文件
        'log': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': 'log',  # 输出位置 日志文件路径
            'maxBytes': 1024 * 1024 * 5,  # 文件大小 5M
            'backupCount': 5,  # 备份份数
            'encoding': 'utf8',  # 文件编码
        },
    },
    # 过滤器
    'filters': {
        'require_debug_true': {
            '()': "RequireDebugTrue",
        }
    },

    # 日志格式集合
    'formatters': {
        # 标准输出格式
        'standard': {
            # [具体时间][线程名:线程ID][日志名字:日志级别名称(日志级别ID)] [输出的模块:输出的函数]:日志内容
            'format': '[%(asctime)s][%(name)s:%(levelname)s(%(lineno)d)]--[%(module)s]:%(message)s'
        }
    }
}

def create_logger(app):
    """
    """
    logging.config.dictConfig(log_config)
    logger = logging.getLogger(app.config['name'])

    if app.debug and not logger.level:
        logger.setLevel(logging.DEBUG)


    if not has_level_handler(logger):
        logger.addHandler(default_handler)

    return logger