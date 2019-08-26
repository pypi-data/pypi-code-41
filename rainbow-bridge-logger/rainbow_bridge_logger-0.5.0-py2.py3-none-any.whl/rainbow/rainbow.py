"""
:Author: Almer Mendoza
:Since: 10/10/2018
:Updated:
  - 08/26/2019: Environment level configurations
"""
import os
from .helpers import _set_level_format, _get_message

_logging_module = None
_is_no_color = False

class RainbowLogger:
  """A customized logger built on top of Python's logging"""
  def __new__(self,
              name=None,
              no_time=False,
              no_color=False,
              new_logging=None,
              filepath=None,
              log_level=None,
              get_logging=False):
    import logging
    global _logging_module
    global _is_no_color

    _is_no_color = no_color
    _logging_module = logging
    if new_logging is not None:
      _logging_module = new_logging

    level_color_mapping = [
      {"level": _logging_module.DEBUG, "color": "BLUE"},
      {"level": _logging_module.INFO, "color": "GREEN"},
      {"level": _logging_module.WARN, "color": "YELLOW"},
      {"level": _logging_module.ERROR, "color": "RED"},
      {"level": _logging_module.CRITICAL, "color": "MAGENTA"}
    ]

    for l in level_color_mapping:
      _set_level_format(level=l['level'],
                        color=l['color'],
                        logging_module=_logging_module)

    if name is None:
      logger = _logging_module
    else:
      logger = _logging_module.getLogger(name)

    handler = _logging_module.StreamHandler()
    final_message = _get_message(no_time)
    formatter = _logging_module.Formatter(final_message)

    handler.setFormatter(formatter)
    log_level = log_level if log_level else _logging_module.DEBUG
    if 'RAINBOW_LOGGER_ON_WARN' in os.environ and os.environ['RAINBOW_LOGGER_ON_WARN'] == 'true':
      log_level = _logging_module.WARN

    if 'RAINBOW_LOGGER_ON_ERROR' in os.environ and os.environ['RAINBOW_LOGGER_ON_ERROR'] == 'true':
      log_level = _logging_module.ERROR

    if name is None:
      _logging_module.basicConfig(format=final_message,
                                  level=log_level)
    else:
      logger.addHandler(handler)
      logger.setLevel(log_level)

    if filepath and name:
      handler = _logging_module.FileHandler(filepath)
      _is_no_color = True
      final_message = _get_message(no_time)
      formatter = _logging_module.Formatter(final_message)
      handler.setFormatter(formatter)
      logger.addHandler(handler)

    if get_logging:
      return _logging_module

    return logger

def __init__():
  return RainbowLogger
