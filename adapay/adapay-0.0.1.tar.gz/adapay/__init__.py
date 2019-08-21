api_key = None
private_key_path = None
private_key = None
public_key_path = None
public_key = None
base_url = 'http://api.payun.cloud'
connect_timeout = 30

from fishbase.fish_logger import set_log_file, set_log_stdout
import logging

log_level = logging.INFO
log_tag = '{adapay}'
# log 将log输出到指定路径下
log_file_path = ''
# 日志在编辑本地显示
log_console_enable = False

if log_console_enable:
    set_log_stdout()
if log_file_path:
    set_log_file(log_file_path)

from adapay.api import *

# sdk 版本
__version__ = '0.0.1'
