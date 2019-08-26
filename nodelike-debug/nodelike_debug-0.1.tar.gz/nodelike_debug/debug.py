import os
import hashlib

env_var_name = 'DEBUG'

def get_enabled_rules():
    if env_var_name not in os.environ:
        return []
    enabled_rules = os.environ[env_var_name].split(',')
    enabled_rules = [rule.strip() for rule in enabled_rules]
    return enabled_rules

enabled_rules = get_enabled_rules()

colors = [
    '\x1b[32m',
    '\x1b[33m',
    '\x1b[34m',
    '\x1b[31m',
    '\x1b[35m',
    '\x1b[36m',
    '\x1b[37m',
]

def is_name_enabled(name):
    is_enabled = name in enabled_rules or '*' in enabled_rules
    return is_enabled

def Debug(name):
    color_index = int(hashlib.sha1(name.encode()).hexdigest(), 16) % len(colors)
    colored_name = colors[color_index] + name + '\x1b[0m'
    is_enabled = is_name_enabled(name)
    if is_name_enabled('debug'):
        print('debug for name', colored_name, 'enabled')


    def debug(*args):
       print(colored_name, *args)

    def nop(*args):
        pass

    if is_enabled:
        return debug
    else:
        return nop

def test_colors():
    for i, col in enumerate(colors):
        print(col + 'text in color #' + str(i) + '\x1b[0m')

# test_colors()
