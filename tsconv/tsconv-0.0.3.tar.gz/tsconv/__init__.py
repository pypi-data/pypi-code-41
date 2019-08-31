import datetime
import enum
import os
import sys
import time

import pytz


MIN_DATE = datetime.datetime(year=2000, month=1, day=1)
MAX_DATE = MIN_DATE + datetime.timedelta(days=100*365)
MIN_TS = MIN_DATE.timestamp()
MAX_TS = MAX_DATE.timestamp()
VERSION = '0.0.3'


class UnitPerSec(enum.IntEnum):
    SEC = 1
    MILI_SEC = int(1e3)
    MICRO_SEC = int(1e6)
    NANO_SEC = int(1e9)


def is_reasonable(ts: float):
    return MIN_TS <= ts <= MAX_TS


def check_interval():
    MAX_TS  < MIN_TS * UnitPerSec.MILI_SEC


class InvalidTsValue(ValueError):
  pass


def guess_ts_unit(ts: float):
  for unit_per_sec in UnitPerSec:
    if is_reasonable(ts/unit_per_sec.value):
      return unit_per_sec
  else:
    raise InvalidTsValue('Timestamp value not in reasonable range!')


def ts_to_datetime(ts, tz):
  unit_per_sec = guess_ts_unit(ts)
  ts = ts / unit_per_sec.value
  return datetime.datetime.fromtimestamp(ts, tz)


def print_usage():
  program_name = sys.argv[0]
  print(f'{program_name} {VERSION}')
  print('usage:')
  print(f'\t{program_name} timestamp')


def main(argv=None):
  argv = argv or sys.argv
  check_interval()

  tz_str = os.environ.get('TZ', 'UTC')
  tzinfo = pytz.timezone(tz_str)
  try:
    timestamp = float(argv[1])
    result = ts_to_datetime(timestamp, tzinfo)
    print(result)
  except InvalidTsValue:
    print(f'Reasonable time range [{MIN_DATE}, {MAX_DATE}]')
  except (IndexError, KeyError):
    print_usage()


if __name__ == "__main__":
  sys.exit(main(sys.argv))
