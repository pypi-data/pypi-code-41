api_key = None
private_key_path = None
private_key = None
public_key_path = None
public_key = None
base_url = 'https://api.adapay.tech'
connect_timeout = 30

from fishbase.fish_logger import set_log_file, set_log_stdout
import logging

log_level = logging.INFO
log_tag = '{adapay}'
log_file_path = ''
log_console_enable = False

if log_console_enable:
    set_log_stdout()
if log_file_path:
    set_log_file(log_file_path)

__version__ = '1.0.3'

from adapay.api import *
