import os

def _get_color(color=None):
  """Get color name from pre-defined color list"""
  from .rainbow import _is_no_color
  if 'RAINBOW_LOGGER_NO_COLOR' in os.environ and os.environ['RAINBOW_LOGGER_NO_COLOR'] == 'true':
    return ''

  if _is_no_color:
    return ''

  if color is None and not color:
    raise ValueError('Must have color code')

  colors = {
    'PURPLE':'\033[96m',
    'MAGENTA':'\033[95m',
    'BLUE':'\033[94m',
    'GREEN':'\033[92m',
    'YELLOW':'\033[93m',
    'RED':'\033[91m',
    'DARKGRAY':'\033[90m',
    'GREY':'\033[0m',
    'WHITE':'\033[1m'
  }

  if color not in colors:
    raise KeyError('Use a proper color name: {}'.format(list(colors.keys())))

  return colors[color]

def _get_message(no_time=False):
  """Get message parts"""
  time = '{}%(asctime)s{}'.format(_get_color('DARKGRAY'), _get_color('GREY'))
  name = '{}%(name)-12s{}'.format(_get_color('PURPLE'), _get_color('GREY'))
  level = '%(levelname)-8s'
  message = '%(message)s'

  if 'RAINBOW_LOGGER_NO_TIME' in os.environ and os.environ['RAINBOW_LOGGER_NO_TIME'] == 'true':
    return ''

  if no_time:
    return '{} {}\t{}'.format(name, level, message)

  return '{} {} {}\t{}'.format(time, name, level, message)

def _set_level_format(level=None, color='WHITE', logging_module=None):
  """Set logging format based on level and color"""
  FORMAT = '{}{}{}'
  _logging_module = logging_module
  parsed_format = FORMAT.format(
    _get_color(color),
    _logging_module.getLevelName(level),
    _get_color('GREY')
  )

  if level is not None:
    _logging_module.addLevelName(level, parsed_format)

  return True
