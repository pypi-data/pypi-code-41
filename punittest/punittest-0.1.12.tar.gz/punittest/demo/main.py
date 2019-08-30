#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from punittest import SETTINGS, RELOAD_SETTINGS
from punittest import logger, TestRunner

# 先修改punittest的设置然后重载
SETTINGS.EXCEL_TEST_SET = True
SETTINGS.RUN_TAGS = ["All"]
SETTINGS.LOG_FILE_SWITCH = True
SETTINGS.LOG_REPORT_SWITCH = True
SETTINGS.LOG_DIR = r"D:\Temp\Logs"
SETTINGS.REPORT_DIR = r"D:\Temp\Reports"
SETTINGS.CAP_FUNC = lambda _dir, name, **kwargs: logger\
    .info(r"创建截图{}\{}，参数{}".format(_dir, name, kwargs))
SETTINGS.CAP_DIR = r"D:\Temp\screenshots"
SETTINGS.CAP_KWARGS = {"arg1": "val1", "arg2": "val2"}
RELOAD_SETTINGS()

# 运行测试
logger.info("开始")
runner = TestRunner("demo接口测试用例")
results = runner.run()
logger.info("结束")
