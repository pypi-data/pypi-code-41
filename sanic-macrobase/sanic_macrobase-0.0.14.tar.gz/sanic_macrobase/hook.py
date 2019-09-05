from enum import Enum

class SanicHookNames(Enum):
    before_server_start = 'before_server_start'
    after_server_start = 'after_server_start'
    before_server_stop = 'before_server_stop'
    after_server_stop = 'after_server_stop'
