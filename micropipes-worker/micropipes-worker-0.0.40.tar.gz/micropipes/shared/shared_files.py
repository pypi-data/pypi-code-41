from enum import Enum
import os

'''
hourDir="${SHARED_DIR}"/h
dayDir="${SHARED_DIR}"/d
weekDir="${SHARED_DIR}"/w
monthDir="${SHARED_DIR}"/m
permanentDir="${SHARED_DIR}"/p
'''

ENV_SHARED_DIR = "SHARED_DIR"

class Duration(Enum):
    HOUR = "h"
    DAY = "d"
    WEEK = "w"
    MONTH = "m"
    PERMANENT = "p"


def get_shared_dir(duration):
    if not isinstance(duration,Duration):
        raise TypeError('duration must be an instance of Duration Enum')
    if not ENV_SHARED_DIR in os.environ:
        raise EnvironmentError('{} must be set as environemt variable'.format(ENV_SHARED_DIR))
    base =  os.environ[ENV_SHARED_DIR]
    return os.path.join(base,duration.value)


if __name__ == "__main__":

    values = ["nic", Duration.HOUR, Duration.PERMANENT]
    for v in values:
        try:
            print(get_shared_dir(v))
        except Exception as e:
            print(e)
    os.environ[ENV_SHARED_DIR] = "c:\\users\\tmp"
    for v in values:
        try:
            print(get_shared_dir(v))
        except Exception as e:
            print(e)
